import os
import pandas as pd
import sqlite3
from pathlib import Path

# Folder where your CSV files are stored
CSV_FOLDER = Path(__file__).resolve().parent.parent.parent / 'data' / 'processedCSV'

# Set the database path to the backend folder
DB_PATH = Path(__file__).resolve().parent.parent.parent / 'backend' / 'argo_profiles.db'
TABLE_NAME = "profiles"

def create_database():
    # Connect to SQLite (creates file if not exists)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table (if not exists)
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        N_PROF INTEGER,
        N_LEVELS INTEGER,
        JULD REAL,
        LATITUDE REAL,
        LONGITUDE REAL,
        PRES REAL,
        TEMP REAL,
        PSAL REAL,
        PRES_ADJUSTED REAL,
        TEMP_ADJUSTED REAL,
        PSAL_ADJUSTED REAL
    )
    """)
    conn.commit()
    conn.close()

def insert_data_from_csv():
    conn = sqlite3.connect(DB_PATH)
    
    # Loop through all CSV files
    for file in os.listdir(CSV_FOLDER):
        if file.endswith(".csv"):
            file_path = os.path.join(CSV_FOLDER, file)
            print(f"Processing {file_path} ...")
            
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Insert into DB
            df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)
    
    conn.close()

if __name__ == "__main__":
    create_database()
    insert_data_from_csv()
    print(f"All CSV files inserted into {DB_PATH}")
