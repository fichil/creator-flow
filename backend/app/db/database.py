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
        _ensure_preview_artifact_columns(connection)


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


def _ensure_preview_artifact_columns(connection: sqlite3.Connection) -> None:
    table = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'render_artifacts'"
    ).fetchone()
    if table is None:
        return
    table_sql = table[0]
    if (
        "fake_preview_manifest" in table_sql
        and "subtitle_draft_id" in table_sql
        and "checksum_sha256" in table_sql
    ):
        return

    connection.execute("PRAGMA foreign_keys = OFF")
    connection.executescript(
        """
        CREATE TABLE render_artifacts_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            render_job_id INTEGER NOT NULL,
            subtitle_draft_id INTEGER,
            artifact_type TEXT NOT NULL DEFAULT 'fake_preview_manifest',
            file_name TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            duration_seconds INTEGER NOT NULL,
            width INTEGER NOT NULL,
            height INTEGER NOT NULL,
            storage_path TEXT NOT NULL,
            checksum_sha256 TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES content_projects(id) ON DELETE CASCADE,
            FOREIGN KEY (render_job_id) REFERENCES render_jobs(id) ON DELETE CASCADE,
            FOREIGN KEY (subtitle_draft_id) REFERENCES subtitle_drafts(id) ON DELETE SET NULL,
            CHECK (artifact_type IN ('fake_video', 'fake_preview_manifest')),
            CHECK (mime_type IN ('video/mp4', 'application/json')),
            CHECK (file_size_bytes >= 0),
            CHECK (duration_seconds > 0),
            CHECK (width > 0),
            CHECK (height > 0)
        );

        INSERT INTO render_artifacts_new (
            id, project_id, render_job_id, artifact_type, file_name, mime_type,
            file_size_bytes, duration_seconds, width, height, storage_path, created_at
        )
        SELECT id, project_id, render_job_id, artifact_type, file_name, mime_type,
               file_size_bytes, duration_seconds, width, height, storage_path, created_at
        FROM render_artifacts;

        DROP TABLE render_artifacts;
        ALTER TABLE render_artifacts_new RENAME TO render_artifacts;

        CREATE INDEX IF NOT EXISTS idx_render_artifacts_render_job_id
        ON render_artifacts (render_job_id);
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
