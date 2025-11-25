from pathlib import Path
import sys

import pytest
import werkzeug

if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "patched"

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from models import db


@pytest.fixture
def app_instance(tmp_path):
    """Create a fresh Flask app with an isolated SQLite DB for each test."""
    db_file = tmp_path / "test.sqlite"
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_file}",
    })
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app


@pytest.fixture
def client(app_instance):
    """Flask test client bound to the isolated app."""
    return app_instance.test_client()

