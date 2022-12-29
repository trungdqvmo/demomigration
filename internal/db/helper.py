init_migration_table = "".join([
    "CREATE TABLE IF NOT EXISTS migration(",
    "version varchar(14) constraint migration_pk primary key,",
    "batch integer not null,",
    "apply_time timestamp default now() not null",
    ");"
])

update_migration = "".join([

])
