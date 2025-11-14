# src/data_prep.py
import os
import json
import pandas as pd
from datetime import datetime
from src import db

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(PROJECT_ROOT, "reports", "scan_results.json")

def _parse_iso(ts):
    if ts is None:
        return None
    try:
        # accept either full iso or truncated forms
        return datetime.fromisoformat(ts)
    except Exception:
        try:
            return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None

def load_from_json(json_path=JSON_PATH):
    """Load scans from reports/scan_results.json and return expanded DataFrame of alerts."""
    if not os.path.exists(json_path):
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for scan in data:
        scan_id = scan.get("scan_id")
        target = scan.get("target")
        started_at = _parse_iso(scan.get("started_at"))
        finished_at = _parse_iso(scan.get("finished_at"))
        alerts = scan.get("alerts", [])
        # compute duration seconds (None if missing)
        duration = None
        if started_at and finished_at:
            duration = (finished_at - started_at).total_seconds()
        for a in alerts:
            rows.append({
                "scan_id": scan_id,
                "target": target,
                "started_at": started_at.isoformat() if started_at else None,
                "finished_at": finished_at.isoformat() if finished_at else None,
                "scan_duration_seconds": duration,
                "alert_name": a.get("alert_name"),
                "risk": a.get("risk"),
                "alert_created_at": a.get("created_at")
            })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    # compute alerts_in_scan
    counts = df.groupby("scan_id").size().rename("alerts_in_scan")
    df = df.merge(counts, how="left", left_on="scan_id", right_index=True)
    return df

def load_from_db():
    """Fallback: load directly from DB via db.fetch_all_results()."""
    rows = db.fetch_all_results()
    if not rows:
        return pd.DataFrame()
    # columns from fetch_all_results:
    # (scan_id, target, started_at, finished_at, alert_name, risk, created_at)
    df = pd.DataFrame(rows, columns=[
        "scan_id", "target", "started_at", "finished_at", "alert_name", "risk", "alert_created_at"
    ])
    # parse timestamps
    df["started_parsed"] = pd.to_datetime(df["started_at"], errors="coerce")
    df["finished_parsed"] = pd.to_datetime(df["finished_at"], errors="coerce")
    df["scan_duration_seconds"] = (df["finished_parsed"] - df["started_parsed"]).dt.total_seconds()
    # compute alerts in scan
    counts = df.groupby("scan_id").size().rename("alerts_in_scan")
    df = df.merge(counts, how="left", left_on="scan_id", right_index=True)
    # normalize column names for compatibility with JSON loader
    df = df.rename(columns={"started_parsed": "started_at", "finished_parsed": "finished_at"})
    return df[["scan_id", "target", "started_at", "finished_at", "scan_duration_seconds", "alert_name", "risk", "alert_created_at", "alerts_in_scan"]]

def load_dataset():
    """Return a pandas DataFrame ready for feature engineering. Prefers JSON, else DB."""
    df = load_from_json()
    if df is None or df.empty:
        df = load_from_db()
    if df is None:
        return pd.DataFrame()
    # drop alerts with missing alert_name or risk
    df = df.dropna(subset=["alert_name", "risk"])
    # trim whitespace
    df["alert_name"] = df["alert_name"].astype(str).str.strip()
    df["risk"] = df["risk"].astype(str).str.strip()
    # some normalization for risk labels (optional)
    df["risk"] = df["risk"].str.title()  # e.g., "low" -> "Low"
    return df
