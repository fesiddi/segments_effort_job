from unittest.mock import patch
from db.database import Database
from dotenv import load_dotenv

load_dotenv()


def test_db_connection():
    # This test uses the real database to test the connection
    db = Database()
    assert db is not None


@patch.object(Database, 'insert_log_entry')
def test_insert_log_entry(mock_insert_log_entry):
    db = Database()
    log_entry = "Test log entry"
    db.insert_log_entry({"log": log_entry})
    mock_insert_log_entry.assert_called_once_with({"log": log_entry})


@patch.object(Database, 'upload_logs_to_db')
def test_upload_logs_to_db(mock_upload_logs_to_db):
    db = Database()
    db.upload_logs_to_db()
    mock_upload_logs_to_db.assert_called_once()

