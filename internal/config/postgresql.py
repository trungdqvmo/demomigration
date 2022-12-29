from internal.config.config_env import get_env


class Postgresql:
    dns = get_env("POSTGRES_DNS")
    migration_path = get_env("MIGRATION_PATH")
    keep_alive = 1
    keep_alive_idle = 30
    keep_alive_interval = 10
    keep_alive_count = 5
