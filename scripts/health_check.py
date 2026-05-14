import requests

ports = {
    "payment": 8001,
    "banking": 8002,
    "fraud": 8003,
    "credit": 8004,
    "forecast": 8005,
    "identity": 8006,
}

print("=" * 50)
print("  FINCORE AI — SERVICE HEALTH CHECK")
print("=" * 50)

for name, port in ports.items():
    try:
        r = requests.get(f"http://localhost:{port}/", timeout=2)
        data = r.json()
        svc = data.get("service", "unknown")
        print(f"  {name.upper():15s} (:{port})  =>  UP  [{svc}]")
    except Exception:
        print(f"  {name.upper():15s} (:{port})  =>  DOWN")

print("=" * 50)

# Test Gateway proxy
print("\nTesting API Gateway proxy routes...")
try:
    r = requests.get("http://localhost:8000/api/fraud/risk-summary/1", timeout=5)
    print(f"  Gateway -> Fraud Service:  {r.status_code} {r.json()}")
except Exception as e:
    print(f"  Gateway -> Fraud Service:  FAILED ({e})")

try:
    r = requests.get("http://localhost:8000/api/credit/score/1", timeout=5)
    print(f"  Gateway -> Credit Service: {r.status_code} {r.json()}")
except Exception as e:
    print(f"  Gateway -> Credit Service: FAILED ({e})")
