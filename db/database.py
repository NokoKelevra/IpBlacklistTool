import sqlite3
import json
from datetime import datetime
from pathlib import Path
from config.settings import settings

DB_PATH = Path(settings.DB_PATH).resolve()

def get_connection():
    """Devuelve una conexión a la base de datos"""
    return sqlite3.connect(DB_PATH)


def database_exists():
    """Comprueba si la base de datos existe"""
    return DB_PATH.is_file()


def create_database():
    """Crea la base de datos y las tablas necesarias"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
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

def ip_exists(ip: str) -> bool:
    """
    Comprueba si una IP ya existe en la base de datos.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM ips WHERE ip = ? LIMIT 1",
        (ip,)
    )

    exists = cursor.fetchone() is not None
    conn.close()

    return exists

def insert_ip(
    ip: str,
    country: str | None = None,
    city: str | None = None,
    org: str | None = None,
    isp: str | None = None,
    last_seen: str | None = None,
    shodan_data: dict | None = None,
):
    """
    Inserta una IP nueva en la base de datos.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if last_seen is None:
        last_seen = datetime.utcnow().isoformat()

    cursor.execute(
        """
        INSERT INTO ips (
            ip, country, city, org, isp, last_seen, shodan_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ip,
            country,
            city,
            org,
            isp,
            last_seen,
            json.dumps(shodan_data) if shodan_data else None,
        ),
    )

    conn.commit()
    conn.close()

def update_last_seen(ip: str, timestamp: str | None = None):
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE ips
        SET last_seen = ?
        WHERE ip = ?
        """,
        (timestamp, ip),
    )

    conn.commit()
    conn.close()

def get_last_seen(ip: str) -> str | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT last_seen FROM ips WHERE ip = ?",
        (ip,),
    )

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None
