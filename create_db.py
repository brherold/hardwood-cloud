"""
Convenience launcher for database creation.
Run from root: python create_db.py
"""

import os
import sys

# Add backend directory to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.scripts.create_db import init_database, DB_PATH
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Hardwood basketball.db if it does not exist.")
    parser.add_argument("--force", action="store_true", help="Force recreate database if it already exists.")
    parser.add_argument("--path", type=str, default=DB_PATH, help=f"Path to database file (default: {DB_PATH}).")
    args = parser.parse_args()

    init_database(db_path=args.path, force=args.force)
