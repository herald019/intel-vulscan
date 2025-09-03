import time
from zapv2 import ZAPv2
from src import db

ZAP_PROXY = "http://localhost:8090"
zap = ZAPv2(proxies={'http': ZAP_PROXY, 'https': ZAP_PROXY})

def run_scan(target):
    db.init_db()  # make sure the DB and table exist
    scan_id = db.create_scan_id()  # generate a unique ID for this scan
    print(f"Starting scan {scan_id} on {target}...")

    # Open target in ZAP
    zap.urlopen(target)
    time.sleep(2)

    # Spider phase
    spider_id = zap.spider.scan(target)
    while int(zap.spider.status(spider_id)) < 100:
        print("Spider progress:", zap.spider.status(spider_id) + "%")
        time.sleep(2)
    print("Spider completed.")

    # Active scan phase
    ascan_id = zap.ascan.scan(target)
    while int(zap.ascan.status(ascan_id)) < 100:
        print("Active scan progress:", zap.ascan.status(ascan_id) + "%")
        time.sleep(5)
    print("Active scan completed.")

    # Alerts
    alerts = zap.core.alerts(baseurl=target)
    print(f"Found {len(alerts)} alerts.")
    for alert in alerts:
        db.insert_alert(scan_id, target, alert["alert"], alert["risk"])
        print(f"{alert['alert']} - {alert['risk']}")

    return scan_id, alerts
