import sqlite3
import os
import uuid
import datetime

DB_FILE = "scanner.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Table for scan metadata
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS scan_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT UNIQUE,
            target TEXT,
            status TEXT,
            started_at TIMESTAMP,
            finished_at TIMESTAMP
        )
        """
    )

    # Table for alerts
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS scan_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT,
            alert_name TEXT,
            risk TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scan_id) REFERENCES scan_runs(scan_id)
        )
        """
    )

    conn.commit()
    conn.close()

def create_scan(target):
    """Create a new scan entry and return scan_id"""
    conn = get_connection()
    c = conn.cursor()
    scan_id = str(uuid.uuid4())
    started_at = datetime.datetime.now().isoformat()
    c.execute(
        "INSERT INTO scan_runs (scan_id, target, status, started_at) VALUES (?, ?, ?, ?)",
        (scan_id, target, "running", started_at),
    )
    conn.commit()
    conn.close()
    return scan_id

def finish_scan(scan_id, status="completed"):
    """Mark scan as finished"""
    conn = get_connection()
    c = conn.cursor()
    finished_at = datetime.datetime.now().isoformat()
    c.execute(
        "UPDATE scan_runs SET status=?, finished_at=? WHERE scan_id=?",
        (status, finished_at, scan_id),
    )
    conn.commit()
    conn.close()

def insert_alert(scan_id, alert_name, risk):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO scan_alerts (scan_id, alert_name, risk) VALUES (?, ?, ?)",
        (scan_id, alert_name, risk),
    )
    conn.commit()
    conn.close()

def fetch_all_results():
    """Fetch all alerts with their scan info"""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        SELECT r.scan_id, r.target, r.started_at, r.finished_at, a.alert_name, a.risk, a.created_at
        FROM scan_runs r
        LEFT JOIN scan_alerts a ON r.scan_id = a.scan_id
        ORDER BY r.started_at DESC
        """
    )
    rows = c.fetchall()
    conn.close()
    return rows
