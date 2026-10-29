"""
Database Initialization Script for Hardwood.
Creates instance/basketball.db with all SQLAlchemy models and tables if it does not already exist.
"""

import os
import sys
import argparse
import sqlite3

# Ensure backend directory is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
INSTANCE_DIR = os.path.join(PROJECT_ROOT, "instance")
DB_PATH = os.path.join(INSTANCE_DIR, "basketball.db")


def init_database(db_path=DB_PATH, force=False):
    """
    Creates the basketball.db SQLite database with all tables defined in models.py
    if the file does not already exist.

    Args:
        db_path (str): Path to the SQLite database file.
        force (bool): If True, overwrites existing database.

    Returns:
        bool: True if database was created, False if it already existed.
    """
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    if os.path.exists(db_path) and not force:
        print(f"[INFO] Database already exists at: {db_path}")
        print("       Initialization skipped. Use '--force' to overwrite.")
        return False

    if os.path.exists(db_path) and force:
        print(f"[WARN] '--force' flag provided. Removing existing database at: {db_path}")
        try:
            os.remove(db_path)
        except Exception as e:
            print(f"[ERROR] Could not remove existing file: {e}")
            return False

    print(f"[INFO] Creating new basketball database at: {db_path}...")

    from flask import Flask
    from extensions import db
    import models  # Registers all 12 SQLAlchemy models

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.abspath(db_path)}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        # Create all tables from registered models
        db.create_all()

    # Enable WAL mode and standard pragmas
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.execute("PRAGMA busy_timeout = 30000;")

    # Verify created tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cursor.fetchall() if r[0] != "sqlite_sequence"]
    conn.close()

    print(f"[SUCCESS] Successfully created {len(tables)} tables in {db_path}:")
    for t in tables:
        print(f"  - {t}")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Hardwood SQLite database if it does not exist.")
    parser.add_argument("--force", action="store_true", help="Force recreate database if it already exists.")
    parser.add_argument("--path", type=str, default=DB_PATH, help=f"Path to database file (default: {DB_PATH}).")
    args = parser.parse_args()

    init_database(db_path=args.path, force=args.force)
