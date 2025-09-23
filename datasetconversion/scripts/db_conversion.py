import os
import pandas as pd
import sqlite3
from pathlib import Path
import logging

# Folder where your CSV files are stored
CSV_FOLDER = Path(__file__).resolve().parent.parent.parent / 'data' / 'processedCSV'

# Set the database path to the backend folder
DB_PATH = Path(__file__).resolve().parent.parent.parent / 'backend' / 'argo_profiles.db'
TABLE_NAME = "profiles"

def create_database():
    # Connect to SQLite (creates file if not exists)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table (if not exists) - simplified like working version
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
        PSAL_ADJUSTED REAL,
        SOURCE_FILE TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_data_from_csv():
    repo_root = Path(__file__).resolve().parent.parent.parent
    logs_dir = repo_root / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'db_load.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    # Use WAL mode and timeout to handle database locking
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    CSV_FOLDER.mkdir(parents=True, exist_ok=True)

    # Look for the consolidated CSV file
    consolidated_csv = CSV_FOLDER / "argo_profiles_consolidated.csv"
    
    if not consolidated_csv.exists():
        logging.warning(f"Consolidated CSV not found: {consolidated_csv}")
        conn.close()
        return

    logging.info(f"Processing consolidated CSV: {consolidated_csv}")
    try:
        df = pd.read_csv(consolidated_csv)
        logging.info(f"Loaded {len(df)} rows from CSV")
        
        # Check if we've already processed this data by checking SOURCE_FILE
        cursor = conn.cursor()
        if 'SOURCE_FILE' in df.columns:
            # Get unique source files in CSV
            csv_sources = set(df['SOURCE_FILE'].unique())
            # Get already processed source files from DB
            cursor.execute(f"SELECT DISTINCT SOURCE_FILE FROM {TABLE_NAME} WHERE SOURCE_FILE IS NOT NULL")
            db_sources = set(row[0] for row in cursor.fetchall())
            
            # Only process new source files
            new_sources = csv_sources - db_sources
            if new_sources:
                logging.info(f"Processing new source files: {new_sources}")
                df_new = df[df['SOURCE_FILE'].isin(new_sources)]
                logging.info(f"Processing {len(df_new)} new rows")
            else:
                logging.info("No new data to process - all source files already in database")
                conn.close()
                return
        
        # Ensure all expected columns are present
        expected_cols = [
            'N_PROF','N_LEVELS','JULD','LATITUDE','LONGITUDE',
            'PRES','TEMP','PSAL','PRES_ADJUSTED','TEMP_ADJUSTED','PSAL_ADJUSTED','SOURCE_FILE'
        ]
        keep = [c for c in expected_cols if c in df.columns]
        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            logging.warning(f"Missing columns: {missing}")
        
        df = df[keep]
        
        # Simple append like working version
        df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)
        conn.commit()
        
        # Count total rows in DB
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        total_rows = cursor.fetchone()[0]
        logging.info(f"Database now contains {total_rows} total rows")
        
    except Exception as exc:
        logging.error(f"Failed to process CSV: {exc}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
    insert_data_from_csv()
    print(f"All CSV files inserted into {DB_PATH}")
