import os
import sys

# BASE_DIR points to 'backend'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask
from extensions import db

# Alias so both 'app_init' and 'backend.app_init' resolve to this module instance
if 'backend.app_init' not in sys.modules:
    sys.modules['backend.app_init'] = sys.modules[__name__]
if 'app_init' not in sys.modules:
    sys.modules['app_init'] = sys.modules[__name__]
# BASE_DIR points to 'backend'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Go up one directory to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))

# Database path in top-level 'instance' folder
INSTANCE_DIR = os.path.join(PROJECT_ROOT, 'instance')
DB_PATH = os.path.join(INSTANCE_DIR, 'basketball.db')

# Make sure the instance folder exists
os.makedirs(INSTANCE_DIR, exist_ok=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from sqlalchemy import event

with app.app_context():
    @event.listens_for(db.engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode = WAL")
        cursor.execute("PRAGMA synchronous = NORMAL")
        cursor.execute("PRAGMA cache_size = -64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store = MEMORY")
        cursor.execute("PRAGMA mmap_size = 268435456")  # 256MB memory-mapped I/O
        cursor.execute("PRAGMA busy_timeout = 30000")
        cursor.close()
'''
# Test connection
import sqlite3
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS test(id INTEGER PRIMARY KEY)")
conn.close()

print("Database connection works!")
print(f"DB_PATH = {DB_PATH}")
'''