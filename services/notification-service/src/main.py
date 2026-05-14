"""
FinCore AI — Notification Service (Port 8007)
Handles alerts, fraud notifications, and SMS/email dispatching.
Placeholder — will be expanded during frontend integration.
"""
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FinCore AI — Notification Service",
    description="Alert dispatching for fraud detection and transaction notifications.",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

NOTIFICATION_PORT = 8007


@app.get("/")
def health():
    return {"service": "notification-service", "status": "running", "port": NOTIFICATION_PORT}


@app.post("/alert")
def send_alert(sme_id: int, message: str, channel: str = "sms"):
    """Dispatch a notification to an SME. Channels: sms, email, push."""
    return {
        "status": "dispatched",
        "sme_id": sme_id,
        "channel": channel,
        "message": message,
        "note": "Placeholder — integration pending"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=NOTIFICATION_PORT)
