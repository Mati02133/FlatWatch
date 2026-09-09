import psycopg
from psycopg.rows import dict_row

from backend.scrapers.config import DATABASE_URL

_connection = None

def get_connection():
    global _connection

    if _connection is None or _connection.closed:
        if not DATABASE_URL:
            raise RuntimeError(
                "Brak DATABASE_URL. Ustaw go w pliku .env albo w sekretach repozytorium."
            )
        if not DATABASE_URL.startswith(("postgresql://", "postgres://")):
            schemat = DATABASE_URL.split("://", 1)[0] if "://" in DATABASE_URL else "(brak schematu)"
            raise RuntimeError(
                f"DATABASE_URL wskazuje na '{schemat}', a potrzebny jest Postgres. "
                "Skopiuj adres z Supabase: Connect -> Session pooler."
            )
        _connection = psycopg.connect(DATABASE_URL, row_factory=dict_row, autocommit=True)

    return _connection

def close_connection():
    global _connection

    if _connection is not None and not _connection.closed:
        _connection.close()
    _connection = None

def create_tables():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS offers (
            id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            external_id TEXT UNIQUE NOT NULL,
            service     TEXT NOT NULL,
            title       TEXT,
            description TEXT,
            price       NUMERIC,
            area        TEXT,
            rooms       TEXT,
            city        TEXT,
            url         TEXT,
            is_private  BOOLEAN DEFAULT TRUE,
            is_active   BOOLEAN DEFAULT TRUE,
            created_at  TIMESTAMPTZ DEFAULT now(),
            last_seen   TIMESTAMPTZ
        )
    """)

    print("DATABASE READY")
