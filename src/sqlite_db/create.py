import sqlite3
import pandas as pd
from pathlib import Path


def csv_to_sqlite(db_name: str, csv_files: dict, n_rows: int = None):
    """Import CSV files into a SQLite database

    Args:
        db_name (str): Database name
        csv_files (dict): Dictionary with table names as keys and
                          CSV file paths as values
        n_rows (int, optional): Maximum number of rows to consider
    """
    conn = sqlite3.connect(db_name)

    for table_name, f in csv_files.items():
        df = pd.read_csv(f, nrows=n_rows) if n_rows else pd.read_csv(f)
        # Write the DataFrame to the SQLite database
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        print(f"Imported {f} into table {table_name}")

    conn.commit()
    conn.close()
    print("All tables imported successfully!")


def main():
    raw_csv_path = Path(__file__).parent / "raw_data"
    DATABASE = Path(__file__).parent / "flights.db"

    csv_files = {file.stem: file for file in raw_csv_path.glob("*.csv")}
    csv_to_sqlite(DATABASE, csv_files, n_rows=10000)


if __name__ == "__main__":
    main()
