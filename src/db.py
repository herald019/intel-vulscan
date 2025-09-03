import sqlite3
import os
import uuid

DB_FILE = "scanner.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT,
            target TEXT,
            alert_name TEXT,
            risk TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

def create_scan_id():
    """Generate a unique scan ID (UUID string)."""
    return str(uuid.uuid4())

def insert_alert(scan_id, target, alert_name, risk):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO scans (scan_id, target, alert_name, risk) VALUES (?, ?, ?, ?)",
        (scan_id, target, alert_name, risk),
    )
    conn.commit()
    conn.close()

def fetch_all_results():
    """Fetch all rows from scans table"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, scan_id, target, alert_name, risk, created_at FROM scans")
    rows = c.fetchall()
    conn.close()
    return rows
