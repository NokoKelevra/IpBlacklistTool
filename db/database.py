import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "blacklist.db")


def get_connection():
    """Devuelve una conexión a la base de datos"""
    return sqlite3.connect(DB_PATH)


def database_exists():
    """Comprueba si la base de datos existe"""
    return os.path.isfile(DB_PATH)


def create_database():
    """Crea la base de datos y las tablas necesarias"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT UNIQUE NOT NULL,
            country TEXT,
            city TEXT,
            org TEXT,
            isp TEXT,
            last_seen TEXT,
            shodan_data TEXT
        )
    """)

    conn.commit()
    conn.close()
