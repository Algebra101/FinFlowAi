"""
FinCore AI — Local Development Launcher
Starts all microservices on their designated ports.
Run this script from the project root: python scripts/start_all.py
"""
import subprocess
import sys
import time
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

services = [
    ("Payment Service",     "services/payment-service/src/main.py",     8001),
    ("Banking Service",     "services/banking-service/src/main.py",     8002),
    ("Fraud Service",       "services/fraud-service/src/main.py",       8003),
    ("Credit Service",      "services/credit-service/src/main.py",      8004),
    ("Forecasting Service", "services/forecasting-service/src/main.py", 8005),
    ("Identity Service",    "services/identity-service/src/main.py",    8006),
]

processes = []

print("=" * 60)
print("  FINCORE AI — Starting Microservices")
print("=" * 60)

for name, path, port in services:
    full_path = os.path.join(PROJECT_ROOT, path)
    print(f"  Starting {name} on port {port}...")
    proc = subprocess.Popen(
        [sys.executable, full_path],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    processes.append((name, proc, port))

# Give services time to boot
time.sleep(3)

# Start API Gateway (foreground so you can see logs)
print(f"\n  Starting API Gateway on port 8000 (foreground)...")
print("=" * 60)
print("  All services running! API Gateway: http://localhost:8000")
print("  Health check:  http://localhost:8000/health")
print("  Swagger docs:  http://localhost:8000/docs")
print("=" * 60)

try:
    gateway_path = os.path.join(PROJECT_ROOT, "services/api-gateway/src/main.py")
    subprocess.run([sys.executable, gateway_path], cwd=PROJECT_ROOT)
except KeyboardInterrupt:
    print("\n\nShutting down all services...")
    for name, proc, port in processes:
        proc.terminate()
        print(f"  Stopped {name} (port {port})")
    print("All services stopped.")
