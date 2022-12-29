# demo migration

Migration code base, with the help of psycopg2 and typer

To list all available versions, please use:
    ``
    python -m internal.migrate_cli list-version
    ``

To upgrade database to new batch, please use:
    ``
    python -m internal.migrate_cli upgrade
    ``

To downgrade database to old batch, please use:
    ``
    python -m internal.migrate_cli downgrade --to-batch=1
    ``
with argument ``to-batch`` is optional (if not specified, will downgrade to previous version)

More information can be found by command:
    ``
    python -m internal.migrate_cli --help
    ``
