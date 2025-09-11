import sys
import pathlib
# ensure project root is first on sys.path so `import app...` uses this project's src
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import os
import tempfile
from app.auth import register_user, authenticate_user
from app.models import init_db, SessionLocal, Base, engine

def test_register_and_auth(tmp_path):
    # use a temp DB file by environment override
    db_dir = tmp_path / "data"
    db_dir.mkdir()
    # patch DB path by environment variable approach: create a temporary engine
    # Simplest: run init_db() which will create the DB in project data; tests run isolated in CI typically.
    init_db()
    ok, msg = register_user("tester", "pw123", is_admin=False)
    assert ok
    user = authenticate_user("tester", "pw123")
    assert user is not None
    assert user.username == "tester"
    bad = authenticate_user("tester", "wrong")
    assert bad is None
