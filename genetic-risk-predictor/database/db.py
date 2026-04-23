"""
Database helper — supports SQL Server (via pyodbc) with automatic
SQLite fallback so the app runs without a SQL Server instance.

Configure SQL Server via environment variables:
    USE_SQLSERVER=true
    DB_SERVER=localhost
    DB_NAME=GeneticRiskPredictor
    DB_DRIVER=ODBC Driver 17 for SQL Server
    DB_TRUSTED=yes          (Windows Auth)
    DB_USER / DB_PASSWORD   (SQL Auth, when DB_TRUSTED=no)
"""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────
USE_SQLSERVER = os.getenv("USE_SQLSERVER", "false").lower() == "true"

SQLSERVER_CONFIG = {
    "server":   os.getenv("DB_SERVER",  "localhost"),
    "database": os.getenv("DB_NAME",    "GeneticRiskPredictor"),
    "driver":   os.getenv("DB_DRIVER",  "ODBC Driver 17 for SQL Server"),
    "trusted":  os.getenv("DB_TRUSTED", "yes"),
    "user":     os.getenv("DB_USER",    ""),
    "password": os.getenv("DB_PASSWORD",""),
}

SQLITE_PATH = Path(__file__).parent / "predictions.db"

# ── Internal helpers ──────────────────────────────────────────────────────────

def _get_sqlserver_conn():
    import pyodbc
    cfg = SQLSERVER_CONFIG
    if cfg["trusted"].lower() == "yes":
        cs = (
            f"DRIVER={{{cfg['driver']}}};"
            f"SERVER={cfg['server']};"
            f"DATABASE={cfg['database']};"
            "Trusted_Connection=yes;"
        )
    else:
        cs = (
            f"DRIVER={{{cfg['driver']}}};"
            f"SERVER={cfg['server']};"
            f"DATABASE={cfg['database']};"
            f"UID={cfg['user']};PWD={cfg['password']};"
        )
    return pyodbc.connect(cs)


def _get_sqlite_conn():
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.row_factory = sqlite3.Row
    _init_sqlite(conn)
    return conn


def _init_sqlite(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name      TEXT    NOT NULL,
            age               INTEGER NOT NULL,
            bmi               REAL    NOT NULL,
            blood_pressure    INTEGER NOT NULL,
            cholesterol       INTEGER NOT NULL,
            glucose           INTEGER NOT NULL,
            smoking           INTEGER NOT NULL DEFAULT 0,
            family_history    INTEGER NOT NULL DEFAULT 0,
            physical_activity INTEGER NOT NULL DEFAULT 0,
            alcohol_use       INTEGER NOT NULL DEFAULT 0,
            genetic_marker_1  INTEGER NOT NULL DEFAULT 0,
            genetic_marker_2  INTEGER NOT NULL DEFAULT 0,
            genetic_marker_3  INTEGER NOT NULL DEFAULT 0,
            genetic_marker_4  INTEGER NOT NULL DEFAULT 0,
            genetic_marker_5  INTEGER NOT NULL DEFAULT 0,
            risk_probability  REAL    NOT NULL,
            risk_level        TEXT    NOT NULL,
            created_at        TEXT    NOT NULL
        )
    """)
    conn.commit()


@contextmanager
def get_connection():
    conn = None
    try:
        conn = _get_sqlserver_conn() if USE_SQLSERVER else _get_sqlite_conn()
        yield conn
    finally:
        if conn:
            conn.close()


# ── Public API ────────────────────────────────────────────────────────────────

_FIELDS = [
    "patient_name","age","bmi","blood_pressure","cholesterol","glucose",
    "smoking","family_history","physical_activity","alcohol_use",
    "genetic_marker_1","genetic_marker_2","genetic_marker_3",
    "genetic_marker_4","genetic_marker_5",
    "risk_probability","risk_level","created_at",
]

_INSERT_SQL = f"""
    INSERT INTO predictions ({', '.join(_FIELDS)})
    VALUES ({', '.join(':' + f for f in _FIELDS)})
"""

_INSERT_SQL_SS = f"""
    INSERT INTO predictions ({', '.join(_FIELDS)})
    VALUES ({', '.join('?' for _ in _FIELDS)})
"""


def save_prediction(data: dict) -> int:
    """Insert a prediction record; returns the new row id."""
    params = {**data, "created_at": datetime.utcnow().isoformat(sep=" ", timespec="seconds")}

    with get_connection() as conn:
        if USE_SQLSERVER:
            cursor = conn.cursor()
            values = [params[f] for f in _FIELDS]
            cursor.execute(_INSERT_SQL_SS, values)
            conn.commit()
            cursor.execute("SELECT @@IDENTITY")
            return int(cursor.fetchone()[0])
        else:
            cursor = conn.execute(_INSERT_SQL, params)
            conn.commit()
            return cursor.lastrowid


def get_history(limit: int = 50, offset: int = 0) -> list:
    """Fetch recent predictions ordered newest first."""
    if USE_SQLSERVER:
        sql = "SELECT * FROM predictions ORDER BY id DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, [offset, limit])
            cols = [c[0] for c in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
    else:
        sql = "SELECT * FROM predictions ORDER BY id DESC LIMIT :limit OFFSET :offset"
        with get_connection() as conn:
            cursor = conn.execute(sql, {"limit": limit, "offset": offset})
            return [dict(r) for r in cursor.fetchall()]


def get_prediction_by_id(prediction_id: int):
    """Fetch a single prediction by id."""
    sql = "SELECT * FROM predictions WHERE id = :id"
    with get_connection() as conn:
        if USE_SQLSERVER:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM predictions WHERE id = ?", [prediction_id])
            cols = [c[0] for c in cursor.description]
            row  = cursor.fetchone()
            return dict(zip(cols, row)) if row else None
        else:
            cursor = conn.execute(sql, {"id": prediction_id})
            row = cursor.fetchone()
            return dict(row) if row else None


def get_total_count() -> int:
    """Total number of predictions stored."""
    with get_connection() as conn:
        if USE_SQLSERVER:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM predictions")
            return cursor.fetchone()[0]
        else:
            cursor = conn.execute("SELECT COUNT(*) FROM predictions")
            return cursor.fetchone()[0]
