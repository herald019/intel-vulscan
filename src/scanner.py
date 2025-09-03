import time
import json
from pathlib import Path
from zapv2 import ZAPv2
from db import init_db
import sqlite3

# ZAP connection settings
ZAP_HOST = "localhost"
ZAP_PORT = 8090
ZAP_API = ZAPv2(apikey=None, proxies={"http": f"http://{ZAP_HOST}:{ZAP_PORT}", "https": f"http://{ZAP_HOST}:{ZAP_PORT}"})

# Target web app (inside Docker network)
TARGET = "http://dvwa:80"

def run_scan(target=TARGET):
    print(f"Starting scan on {target}...")

    # Spider
    scan_id = ZAP_API.spider.scan(target)
    while int(ZAP_API.spider.status(scan_id)) < 100:
        print("Spider progress:", ZAP_API.spider.status(scan_id) + "%")
        time.sleep(2)
    print("Spider completed.")

    # Active scan
    scan_id = ZAP_API.ascan.scan(target)
    while int(ZAP_API.ascan.status(scan_id)) < 100:
        print("Active scan progress:", ZAP_API.ascan.status(scan_id) + "%")
        time.sleep(5)
    print("Active scan completed.")

    # Alerts
    alerts = ZAP_API.core.alerts(baseurl=target)
    print(f"Found {len(alerts)} alerts.")

    return alerts


def save_to_json(alerts):
    results_dir = Path(__file__).resolve().parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    filename = results_dir / f"scan_{int(time.time())}.json"

    with open(filename, "w") as f:
        json.dump(alerts, f, indent=2)

    print(f"Results saved to {filename}")


def save_to_db(alerts, target=TARGET):
    init_db()
    conn = sqlite3.connect("scanner.db")
    cur = conn.cursor()

    for alert in alerts:
        cur.execute("""
            INSERT INTO scans (target, alert_name, risk, confidence, description, solution)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            target,
            alert.get("alert", ""),
            alert.get("risk", ""),
            alert.get("confidence", ""),
            alert.get("description", ""),
            alert.get("solution", "")
        ))

    conn.commit()
    conn.close()
    print(f"Results saved to database (scanner.db)")


if __name__ == "__main__":
    alerts = run_scan()
    save_to_json(alerts)
    save_to_db(alerts)
