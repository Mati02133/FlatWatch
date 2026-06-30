import sqlite3

from config import DATABASE_URL

DB_PATH = DATABASE_URL.replace("sqlite:///", "")

def get_connection():
    conn = sqlite3.connect(DB_PATH) 
    conn.row_factory = sqlite3.Row # ustawiamy row_factory aby zwracac wiersze wedlug nazw kolumn
    return conn

def create_tables():
    conn = get_connection()

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
            created_at  TEXT
        )
    """)

    conn.commit() 
    conn.close()
    print("DATABASE CREATED")
