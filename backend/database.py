"""
database.py — SQLite schema & connection management for AquaPulse
"""
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "aquapulse.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS stations (
        station_id      TEXT PRIMARY KEY,
        station_name    TEXT NOT NULL,
        state           TEXT NOT NULL,
        district        TEXT NOT NULL,
        latitude        REAL NOT NULL,
        longitude       REAL NOT NULL,
        aquifer_type    TEXT NOT NULL,   -- alluvial | hard-rock | coastal
        baseline_level  REAL NOT NULL,   -- historical average depth (m bgl)
        is_anomaly_seed INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS readings (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        station_id  TEXT NOT NULL,
        timestamp   TEXT NOT NULL,       -- ISO-8601 UTC
        level_m     REAL,                -- depth to water table in m bgl (NULL = sensor dropout)
        is_flagged  INTEGER DEFAULT 0,
        FOREIGN KEY (station_id) REFERENCES stations(station_id)
    );

    CREATE INDEX IF NOT EXISTS idx_readings_station_ts
        ON readings (station_id, timestamp);

    CREATE TABLE IF NOT EXISTS alerts (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        station_id  TEXT NOT NULL,
        alert_type  TEXT NOT NULL,  -- GAP | SPIKE | SUSTAINED_DECLINE | OVER_EXPLOITED
        severity    TEXT NOT NULL,  -- INFO | WARNING | CRITICAL
        reason      TEXT NOT NULL,
        timestamp   TEXT NOT NULL,
        resolved    INTEGER DEFAULT 0,
        FOREIGN KEY (station_id) REFERENCES stations(station_id)
    );
    """)

    conn.commit()
    conn.close()
