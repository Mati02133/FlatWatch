import sqlite3

from backend.scrapers.config import DATABASE_URL

DB_PATH = DATABASE_URL.replace("sqlite:///", "") # converts the database url into a local sqlite file path

def get_connection():
    conn = sqlite3.connect(DB_PATH) 
    conn.row_factory = sqlite3.Row # enables column-name access when reading database rows
    return conn

def create_tables():
    conn = get_connection() # opens the sqlite connection for schema setup

    conn.execute("""
        CREATE TABLE IF NOT EXISTS offers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT UNIQUE NOT NULL,
            service     TEXT NOT NULL,
            title       TEXT,
            description TEXT,
            price       INTEGER,
            area        TEXT,
            rooms       TEXT,
            city        TEXT,
            url         TEXT,
            is_private  INTEGER DEFAULT 1,
            is_active   INTEGER DEFAULT 1,
            created_at  TEXT,
            last_seen   TEXT
        )
    """)

    conn.commit() 
    conn.close()
    print("DATABASE CREATED")
