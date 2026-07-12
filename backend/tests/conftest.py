"""
Shared pytest fixtures.

Uses a separate temporary SQLite database for tests (not your real
storage/app.db), so running tests never touches real data.
"""
import gc
import os
import tempfile

import pytest

# Point the app at a temporary test database BEFORE importing app.main,
# since settings are read once at import time.
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db")
os.close(_test_db_fd)  # close the OS handle immediately, SQLAlchemy manages its own
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db_path}"

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.db.session import engine  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True, scope="session")
def cleanup_test_db():
    yield
    # Dispose SQLAlchemy's connection pool so Windows releases its file lock
    # on the SQLite file before we try to delete it.
    engine.dispose()
    gc.collect()
    try:
        os.remove(_test_db_path)
    except PermissionError:
        # Best-effort cleanup — a leftover temp file in %TEMP% is harmless
        # and doesn't affect test correctness.
        pass