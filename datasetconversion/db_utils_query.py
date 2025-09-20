import sqlite3

DB_PATH = "../data/processedCSV/argo_dummy.db"

def run_query(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows