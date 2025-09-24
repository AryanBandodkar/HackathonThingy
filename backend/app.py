import os
import time
import argparse
import subprocess
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
# Removed db_utils_query import - using ETL pipeline instead


def print_db_overview():
    import sqlite3
    db_path = Path(__file__).resolve().parent / 'argo_profiles.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM profiles")
        count = cursor.fetchone()[0]
        print(f"[{datetime.now().isoformat()}] Total profiles in database: {count}")

        cursor.execute("SELECT * FROM profiles LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except Exception as exc:
        print(f"[{datetime.now().isoformat()}] Overview failed: {exc}")
    finally:
        conn.close()


LOGS_DIR = Path(__file__).resolve().parent.parent / 'logs'


def _setup_logging():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger()
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(ch)
        # Rotating file handler for scheduler
        fh = RotatingFileHandler(LOGS_DIR / 'scheduler.log', maxBytes=2_000_000, backupCount=3)
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(fh)


def _append_to_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(content)
        if not content.endswith('\n'):
            f.write('\n')


def run_etl_and_load():
    """Run complete pipeline: inspect -> ETL -> DB load -> cleanup."""
    repo_root = Path(__file__).resolve().parent.parent
    inspect_path = repo_root / 'datasetconversion' / 'scripts' / 'inspectNETCDF.py'
    etl_path = repo_root / 'datasetconversion' / 'scripts' / 'etl.py'
    db_path = repo_root / 'datasetconversion' / 'scripts' / 'db_conversion.py'

    # Step 1: Inspect NetCDF files first
    logging.info(f"Inspecting NetCDF files: {inspect_path}")
    result_inspect = subprocess.run(
        ["python", str(inspect_path)], capture_output=True, text=True
    )
    if result_inspect.stdout:
        logging.info(result_inspect.stdout)
        _append_to_file(LOGS_DIR / 'inspect.log', result_inspect.stdout)
    if result_inspect.stderr:
        logging.warning(result_inspect.stderr)
        _append_to_file(LOGS_DIR / 'inspect.log', result_inspect.stderr)

    # Step 2: Extract profiles to CSV
    logging.info(f"Running ETL: {etl_path}")
    result_etl = subprocess.run(
        ["python", str(etl_path)], capture_output=True, text=True
    )
    if result_etl.stdout:
        logging.info(result_etl.stdout)
        _append_to_file(LOGS_DIR / 'etl.log', result_etl.stdout)
    if result_etl.stderr:
        logging.warning(result_etl.stderr)
        _append_to_file(LOGS_DIR / 'etl.log', result_etl.stderr)
    if result_etl.returncode != 0:
        raise RuntimeError(f"ETL failed with code {result_etl.returncode}")

    # Small delay to prevent rapid DB access
    time.sleep(2)

    # Step 3: Load CSVs into SQLite
    logging.info(f"Loading CSVs into DB: {db_path}")
    result_db = subprocess.run(
        ["python", str(db_path)], capture_output=True, text=True
    )
    if result_db.stdout:
        logging.info(result_db.stdout)
        _append_to_file(LOGS_DIR / 'db_load.log', result_db.stdout)
    if result_db.stderr:
        logging.warning(result_db.stderr)
        _append_to_file(LOGS_DIR / 'db_load.log', result_db.stderr)
    if result_db.returncode != 0:
        raise RuntimeError(f"DB load failed with code {result_db.returncode}")

    # Step 4: Cleanup raw NetCDFs to save space
    try:
        raw_dir = repo_root / 'data' / 'rawNETCDF'
        deleted = 0
        if raw_dir.exists():
            for p in raw_dir.glob('*.nc'):
                try:
                    p.unlink()
                    deleted += 1
                except Exception as exc:
                    logging.warning(f"Failed to delete {p}: {exc}")
        logging.info(f"Deleted {deleted} raw NetCDF file(s) from {raw_dir}")
    except Exception as exc:
        logging.warning(f"Raw cleanup step failed: {exc}")


def fetch_and_update_job():
    started_at = datetime.now().isoformat()
    logging.info(f"Starting scheduled fetch & update job...")
    try:
        run_etl_and_load()
        logging.info("Job finished successfully.")
    except Exception as exc:
        logging.error(f"Job failed: {exc}")
        _append_to_file(LOGS_DIR / 'errors.log', f"{datetime.now().isoformat()} Job failed: {exc}")


def run_scheduler(interval_minutes: int):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        fetch_and_update_job,
        "interval",
        minutes=interval_minutes,
        id="fetch_update_job",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
        replace_existing=True,
    )
    scheduler.start()

    # Run once immediately on startup
    fetch_and_update_job()

    logging.info(
        f"Scheduler started with interval={interval_minutes} minutes. Press Ctrl+C to stop."
    )
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping scheduler...")
    finally:
        scheduler.shutdown(wait=False)
        logging.info("Scheduler stopped.")


def main():
    _setup_logging()
    parser = argparse.ArgumentParser(description="Backend utility & scheduler")
    parser.add_argument(
        "--mode",
        choices=["scheduler", "overview"],
        default="scheduler",
        help="Run background scheduler or print DB overview once.",
    )
    parser.add_argument(
        "--interval-minutes",
        type=int,
        default=int(os.environ.get("FETCH_INTERVAL_MINUTES", "60")),
        help="Scheduler interval in minutes (env FETCH_INTERVAL_MINUTES).",
    )
    args = parser.parse_args()

    if args.mode == "overview":
        print_db_overview()
    else:
        run_scheduler(args.interval_minutes)


if __name__ == "__main__":
    main()