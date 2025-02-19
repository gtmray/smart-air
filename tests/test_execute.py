import pytest
from src.sqlite_db.execute import execute_query
import sqlite3


@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE flights (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO flights VALUES (1, 'Flight A')")
    conn.commit()
    conn.close()
    return db_path


def test_execute_query_success(temp_db):
    result, error = execute_query(temp_db, "SELECT * FROM flights")
    assert result is not None  # Ensure we got some result
    assert len(result) == 1  # We expect one row
    assert error is None  # No error should occur


def test_execute_query_no_results(temp_db):
    result, error = execute_query(
        temp_db, "SELECT * FROM flights WHERE id = 99"
    )
    assert result is None  # Function returns None if no results
    assert error == "No results found"  # Should match the function's output


def test_execute_query_invalid_sql(temp_db):
    result, error = execute_query(temp_db, "SELECT * FROM invalid_table")
    assert result is None  # Should be None when an error occurs
    assert error is not None  # There should be an error message
    assert "SQL Error" in error  # Checking for SQL error message
