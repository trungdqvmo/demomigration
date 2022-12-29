from typing import Optional
import typer

from internal.db.postgres_connector import Postgresql
from internal.db.versioning import Versioning

migrate_cli = typer.Typer()


@migrate_cli.command()
def list_version():
    versions = Versioning.load_migrations(Postgresql.migration_path)
    print(versions.information)


@migrate_cli.command()
def upgrade(
        from_version: Optional[int] = None,
        to_version: Optional[int] = None
):
    versions = Versioning.load_migrations(Postgresql.migration_path, from_version)
    if to_version is None:
        to_version = versions.latest
    if versions.current_version < to_version:
        versions.apply_new_batch(to_version)


@migrate_cli.command()
def downgrade(
        to_batch: Optional[int] = None,
        from_version: Optional[int] = None,
):
    versions = Versioning.load_migrations(Postgresql.migration_path, from_version)
    if to_batch is None:
        to_batch = versions.current_batch - 1
    versions.revert_to_old_batch(to_batch)


if __name__ == "__main__":
    migrate_cli()
