import sqlite3
import pandas as pd


def execute_query(db_name: str, query: str):
    # """Execute SQL query and return results"""
    """Execute SQL query from given database

    Args:
        db_name (str): Database name
        query (str): SQL Query
    """
    conn = sqlite3.connect(db_name)
    try:
        df = pd.read_sql_query(query, conn)
        if df.empty:
            return None, "No results found"
        return df.to_dict("records"), None
    except sqlite3.Error as e:
        return None, f"SQL Error: {str(e)}"
    except Exception as e:
        return None, f"Error: {str(e)}"
    finally:
        conn.close()
