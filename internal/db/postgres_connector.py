import traceback
from contextlib import contextmanager
from threading import Semaphore
from typing import Optional

import psycopg2
import psycopg2.extras
from loguru import logger
from psycopg2.extensions import connection
from psycopg2.pool import ThreadedConnectionPool

from internal.config.postgresql import Postgresql

MIN_CONN = 2
MAX_CONN = 4


class PostgresConnector(ThreadedConnectionPool):
    __flask_instance = None

    def __init__(self):
        self._semaphore = Semaphore(MAX_CONN)
        logger.info("Connecting to postgresQL...")
        super().__init__(
            MIN_CONN,
            MAX_CONN,
            Postgresql.dns,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5,
        )

    @staticmethod
    def __create_connect():
        return psycopg2.connect(
            dsn=Postgresql.dns,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5,
        )

    @property
    def db(self):
        return self.__create_connect()

    def get_db(self):
        try:
            cur = self.db.cursor()
            cur.execute("SELECT 1")
            self.db.commit()
        except psycopg2.Error as e:
            logger.error(f"Cannot connect to db due to {e}")
            traceback.print_exc()
            raise e
        return self.db

    @staticmethod
    def __close_session(session):
        try:
            session.close()
        except psycopg2.Error as postgres_error:
            logger.error(f"Close session got error: {str(postgres_error)}")
            traceback.print_exc()

    def get_cursor(self, session):
        try:
            cursor = session.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            return cursor
        except psycopg2.Error as postgres_error:
            logger.warning(
                f"Connect to db got error: {str(postgres_error)}. Trying to reconnect..."
            )
            traceback.print_exc()
            PostgresConnector.__close_session(session)
            session = self.__create_connect()
            cursor = session.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            return cursor

    def getconn(self, *args, **kwargs):
        self._semaphore.acquire()
        return super().getconn(*args, **kwargs)

    def putconn(self, *args, **kwargs):
        super().putconn(*args, **kwargs)
        self._semaphore.release()

    @staticmethod
    def get_instance():
        if PostgresConnector.__flask_instance is None:
            PostgresConnector.__flask_instance = PostgresConnector()
        return PostgresConnector.__flask_instance


@contextmanager
def session_scope():
    postgres_session: Optional[connection]
    postgres_session = None
    try:
        postgres_session = PostgresConnector.get_instance().get_db()
        postgres_session.autocommit = False
        yield postgres_session
        postgres_session.commit()
        postgres_session.close()
    except Exception as exception:
        logger.exception(exception)
        if postgres_session is not None:
            postgres_session.rollback()
            postgres_session.close()
        raise exception
