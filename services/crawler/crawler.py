import time,requests,uuid,random

while True:
    payload = {
        "type": "distressed_property",
        "address": f"{random.randint(100,999)} Foreclosure Ave",
        "signal": "tax_delinquent",
        "confidence": round(random.uniform(0.85,0.99),2),
        "crawl_id": str(uuid.uuid4())
    }
    try:
        requests.post("http://gateway:8080/ingest", json=payload, timeout=3)
        print("crawler sent:", payload["crawl_id"])
    except Exception as e:
        print("gateway not ready")
    time.sleep(6)
