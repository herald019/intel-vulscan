import os
from src import db

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")

def generate_report():
    results = db.fetch_all_results()

    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    html_content = """
    <html>
    <head>
        <title>Scan Report</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h2>Vulnerability Scan Report</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Scan ID</th>
                <th>Target</th>
                <th>Alert</th>
                <th>Risk</th>
                <th>Timestamp</th>
            </tr>
    """

    for row in results:
        html_content += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>"

    html_content += """
        </table>
    </body>
    </html>
    """

    report_path = os.path.join(REPORTS_DIR, "report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] Report generated: {report_path}")
