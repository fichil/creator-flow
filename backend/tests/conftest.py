import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("CREATOR_FLOW_DATABASE_PATH", str(tmp_path / "creator_flow.sqlite3"))
    monkeypatch.setenv("CREATOR_FLOW_UPLOADS_DIR", str(tmp_path / "uploads"))
    get_settings.cache_clear()
    with TestClient(app) as test_client:
        yield test_client
    get_settings.cache_clear()
