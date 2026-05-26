import sqlite3
from collections.abc import Generator

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.db.models import SCHEMA_SQL


def init_db(settings: Settings) -> None:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.database_path) as connection:
        connection.executescript(SCHEMA_SQL)
        _ensure_archived_status(connection)


def _ensure_archived_status(connection: sqlite3.Connection) -> None:
    table = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'content_projects'"
    ).fetchone()
    if table is None or "archived" in table[0]:
        return

    connection.execute("PRAGMA foreign_keys = OFF")
    connection.executescript(
        """
        CREATE TABLE content_projects_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'draft',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CHECK (status IN ('draft', 'materials_ready', 'archived'))
        );

        INSERT INTO content_projects_new (id, title, description, status, created_at, updated_at)
        SELECT id, title, description, status, created_at, updated_at
        FROM content_projects;

        DROP TABLE content_projects;
        ALTER TABLE content_projects_new RENAME TO content_projects;

        CREATE INDEX IF NOT EXISTS idx_content_projects_created_at
        ON content_projects (created_at DESC, id DESC);
        """
    )
    connection.execute("PRAGMA foreign_keys = ON")


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
