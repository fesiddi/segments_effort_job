from unittest.mock import patch
from db.database import Database
from dotenv import load_dotenv
from utils.config import ConfigForTest

load_dotenv()


def test_db_connection():
    # This test uses the real database to test the connection
    config = ConfigForTest()
    db = Database(config)
    assert db is not None

