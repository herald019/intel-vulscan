import argparse
import json
import os
from src import db, scanner, report_generator

# Project root is the folder where cli.py lives
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")

def export_json():
    """Export all scan results to a JSON file."""
    results = db.fetch_all_results()
    if not results:
        print("[!] No scans available to export")
        return

    # Transform results into structured JSON
    scans = {}
    for row in results:
        scan_id, target, started, finished, alert, risk, created_at = row
        if scan_id not in scans:
            scans[scan_id] = {
                "scan_id": scan_id,
                "target": target,
                "started_at": started,
                "finished_at": finished,
                "status": "completed" if finished else "running",
                "alerts": []
            }
        if alert:  # only add alerts if present
            scans[scan_id]["alerts"].append({
                "alert_name": alert,
                "risk": risk,
                "created_at": created_at
            })

    json_data = list(scans.values())

    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    json_path = os.path.join(REPORTS_DIR, "scan_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)

    print(f"[+] JSON export created: {json_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Intelligent Vuln Scanner CLI"
    )

    parser.add_argument(
        "--target",
        type=str,
        help="Target URL to scan (e.g., http://dvwa:80)"
    )
    parser.add_argument(
        "--list-scans",
        action="store_true",
        help="List all previous scans"
    )
    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Generate an HTML report from the database"
    )
    parser.add_argument(
        "--export-json",
        action="store_true",
        help="Export all scans as JSON"
    )

    args = parser.parse_args()

    # Always initialize DB before anything else
    db.init_db()

    if args.target:
        scan_id, alerts = scanner.run_scan(args.target)
        print(f"[+] Scan {scan_id} completed with {len(alerts)} alerts")

    elif args.list_scans:
        results = db.fetch_all_results()
        if not results:
            print("[!] No scans found in database")
        else:
            print("Previous scans:")
            for row in results:
                scan_id, target, started, finished, alert, risk, created_at = row
                print(
                    f"Scan ID: {scan_id}, Target: {target}, "
                    f"Started: {started}, Finished: {finished}, "
                    f"Alert: {alert or '---'}, Risk: {risk or '---'}"
                )

    elif args.generate_report:
        report_generator.generate_report()

    elif args.export_json:
        export_json()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
