import os
import pathlib
from loguru import logger

DEFAULT_ENV = {
    "DEBUG": False,
    # postgres
    "POSTGRES_DNS": "",
    "MIGRATION_PATH": pathlib.Path("internal", "db", "migration"),
}


def get_env(key):
    logger.debug(f"{key}, {os.getenv(key, DEFAULT_ENV.get(key))}")
    return os.getenv(key, DEFAULT_ENV.get(key))
