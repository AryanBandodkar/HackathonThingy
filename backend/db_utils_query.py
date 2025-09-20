import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'argo_profiles.db'

def get_connection():
    """Returns a connection to the SQLite database."""
    print(f"Connecting to database at: {DB_PATH}")
    print(f"File exists: {DB_PATH.exists()}")
    print(f"Parent directory exists: {DB_PATH.parent.exists()}")
    return sqlite3.connect(DB_PATH)

def fetch_all_profiles():
    """Example utility: fetch all rows from the profiles table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles")
    rows = cursor.fetchall()
    conn.close()
    return rows