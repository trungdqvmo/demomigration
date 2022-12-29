from tabulate import tabulate
from internal.db.postgres_connector import PostgresConnector, session_scope
import datetime


class Versioning:
    fields = ["id", "filename", "batch_id", "applied_time"]

    def __init__(self, versions, upgrade_files, downgrade_files, current_version):
        self.__version_keys = dict(enumerate([""] + versions))
        self.__upgrade_files = [""] + upgrade_files
        self.__downgrade_files = [""] + downgrade_files

        self.__migration_info = {}
        self.__batch_info = {}
        self.__current_version = current_version
        self.__current_batch = 0
        self.__load_migration_info(versions)

    @property
    def connector(self):
        return PostgresConnector.get_instance()

    def apply(self, query, data=None):
        with session_scope() as conn:
            cursor = self.connector.get_cursor(conn)
            sql_query = cursor.mogrify(query, data)
            cursor.execute(sql_query)
            result = [dict(item) for item in cursor.fetchall()]
            cursor.close()
        return result

    @property
    def current_version(self):
        return self.__current_version

    @property
    def current_batch(self):
        return self.__current_batch

    def get_last_version_of_batch(self, batch_id):
        return self.__batch_info[batch_id]

    def __load_migration_info(self, versions) -> None:
        versions = dict(enumerate([""] + versions))
        exist_migration_info = \
            self.apply("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'migration');")
        if exist_migration_info[0]["exists"]:
            migration_table = self.apply("SELECT * FROM migration ORDER BY applied_time")
        else:
            migration_table = []
        self.__batch_info[0] = 0
        self.__current_version = 0
        self.__current_batch = 0
        for version_info in migration_table:
            version_id = version_info.pop("id")
            versions.pop(version_id)
            self.__migration_info[version_id] = version_info
            self.__batch_info[version_info["batch_id"]] = version_id
            self.__current_version = version_id
            self.__current_batch = version_info["batch_id"]

    @property
    def latest(self):
        return len(self.__version_keys) - 1

    @property
    def information(self):
        headers = self.fields
        information = []
        for version_index in self.__version_keys:
            if version_index in self.__migration_info:
                information.append([version_index] + list(self.__migration_info[version_index].values()))
            else:
                information.append([version_index, self.__version_keys[version_index], None, None])
        return tabulate(information, headers=headers)

    def __iter__(self):
        for upgrade_file in self.__upgrade_files:
            yield upgrade_file

    def get_query_from_index(self, version_index, up=True):
        if up:
            with open(self.__upgrade_files[version_index]) as version_file:
                version_query = version_file.read()
        else:
            with open(self.__downgrade_files[version_index]) as version_file:
                version_query = version_file.read()
        return version_query

    def upgrade_migration_query(self, version_ids):
        applied_time = datetime.datetime.now()
        if self.current_batch == 0:
            new_batch_id = 1
            sql_query = "CREATE TABLE IF NOT EXISTS migration(" \
                        + "id SERIAL NOT NULL CONSTRAINT migration_pk PRIMARY KEY," \
                        + "filename TEXT," \
                        + "batch_id INTEGER NOT NULL," \
                        + "applied_time TIMESTAMP default now() not null); "
        else:
            new_batch_id = len(self.__batch_info)
            sql_query = ""

        sql_data = []
        for version_id in version_ids:
            sql_data.extend((version_id, self.__version_keys[version_id], new_batch_id, applied_time))
        sql_query += "INSERT INTO migration (id, filename, batch_id, applied_time) VALUES" \
                     + ", ".join(["(%s, %s, %s, %s)"] * len(version_ids))
        return sql_query, sql_data

    def downgrade_version_query(self, version_ids, drop_migration=False):
        if len(self.__batch_info) == 0 or len(version_ids) == 0:
            return "", []

        sql_data = version_ids
        sql_query = "DELETE FROM migration WHERE id IN (" \
                    + ", ".join(["%s"] * len(version_ids)) \
                    + ")"
        if drop_migration:
            sql_query += "; DROP TABLE migration;"
        return sql_query, sql_data

    def apply_new_batch(self, to_version=None):
        if to_version is None:
            to_version = self.__current_version
        with session_scope() as conn:
            cursor = self.connector.get_cursor(conn)
            updating_versions = []
            for version_index in range(self.current_version + 1, to_version + 1):
                version_query = self.get_query_from_index(version_index)
                sql_query = cursor.mogrify(version_query)
                cursor.execute(sql_query)
                updating_versions.append(version_index)

            updating_versions_query, updating_versions_data = self.upgrade_migration_query(updating_versions)
            sql_query = cursor.mogrify(updating_versions_query, updating_versions_data)
            cursor.execute(sql_query)
            cursor.close()

    def revert_to_old_batch(self, batch_id):
        reversed_version = self.get_last_version_of_batch(batch_id)
        with session_scope() as conn:
            cursor = self.connector.get_cursor(conn)
            updating_versions = []
            for version_index in range(self.current_version, reversed_version, -1):
                version_query = self.get_query_from_index(version_index, up=False)
                sql_query = cursor.mogrify(version_query)
                cursor.execute(sql_query)
                updating_versions.append(version_index)
            downgrade_versions_query, downgrade_versions_data = self.downgrade_version_query(
                updating_versions, drop_migration=batch_id == 0
            )
            sql_query = cursor.mogrify(downgrade_versions_query, downgrade_versions_data)
            cursor.execute(sql_query)
            cursor.close()

    @classmethod
    def load_migrations(cls, file_path, current_version=None):
        # todo: changing load migrations with batch info
        upgrade_files = sorted(list(file_path.glob("**/*.up.sql")))
        downgrade_files = sorted(list(file_path.glob("**/*.down.sql")))
        upgrade_keys = [
            upgrade_version.name[:-len(".up.sql")]
            for upgrade_version in upgrade_files
        ]
        downgrade_keys = [
            downgrade_version.name[:-len(".down.sql")]
            for downgrade_version in downgrade_files
        ]
        if upgrade_keys != downgrade_keys:
            raise IndexError("Upgrade versions and downgrade versions not match!")
        return cls(upgrade_keys, upgrade_files, downgrade_files, current_version)
