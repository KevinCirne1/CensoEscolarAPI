import sqlite3
from contextlib import contextmanager

DB_PATH = "instituicoes.db"

@contextmanager
def get_db_connection():
    """Gerencia conexões com o banco SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    try:
        yield conn
    finally:
        conn.close()

def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    """Executa uma query SQL e retorna resultados, se necessário."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch_one:
            return cursor.fetchone()
        if fetch_all:
            return cursor.fetchall()
        conn.commit()
        return cursor.rowcount