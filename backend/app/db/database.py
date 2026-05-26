import sqlite3
from collections.abc import Generator

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.db.models import SCHEMA_SQL


def init_db(settings: Settings) -> None:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.database_path) as connection:
        connection.executescript(SCHEMA_SQL)


def connect_db(settings: Settings) -> sqlite3.Connection:
    connection = sqlite3.connect(settings.database_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_db(settings: Settings = Depends(get_settings)) -> Generator[sqlite3.Connection, None, None]:
    connection = connect_db(settings)
    try:
        yield connection
    finally:
        connection.close()
