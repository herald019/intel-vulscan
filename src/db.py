import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent.parent / "scanner.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    # Create table if it doesn't exist
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target TEXT,
        alert_name TEXT,
        risk TEXT,
        confidence TEXT,
        description TEXT,
        solution TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
