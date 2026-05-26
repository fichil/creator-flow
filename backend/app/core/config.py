import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    database_path: Path
    uploads_dir: Path
    cors_origins: tuple[str, ...]


@lru_cache
def get_settings() -> Settings:
    root = _repo_root()
    database_path = Path(os.getenv("CREATOR_FLOW_DATABASE_PATH", root / "data" / "local" / "creator_flow.sqlite3"))
    uploads_dir = Path(os.getenv("CREATOR_FLOW_UPLOADS_DIR", root / "uploads"))
    cors_origins = tuple(
        origin.strip()
        for origin in os.getenv(
            "CREATOR_FLOW_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    )
    return Settings(database_path=database_path, uploads_dir=uploads_dir, cors_origins=cors_origins)
