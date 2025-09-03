from zapv2 import ZAPv2
import time

# Setup ZAP API
zap = ZAPv2(apikey='', proxies={'http': 'http://localhost:8090', 'https': 'http://localhost:8090'})

target = "http://dvwa:80"  # internal name from docker-compose

print(f"Starting scan on {target}...")

# Spider scan (crawl the site)
scan_id = zap.spider.scan(target)
while int(zap.spider.status(scan_id)) < 100:
    print(f"Spider progress: {zap.spider.status(scan_id)}%")
    time.sleep(2)
print("Spider completed.")

# Active scan (attack)
scan_id = zap.ascan.scan(target)
while int(zap.ascan.status(scan_id)) < 100:
    print(f"Active scan progress: {zap.ascan.status(scan_id)}%")
    time.sleep(5)
print("Active scan completed.")

# Print alerts
alerts = zap.core.alerts(baseurl=target)
print(f"Found {len(alerts)} alerts.")
for alert in alerts[:5]:  # show first 5 for now
    print(alert['alert'], "-", alert['risk'])
