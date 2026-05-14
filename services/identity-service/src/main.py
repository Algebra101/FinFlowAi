"""
FinCore AI — Identity Service (Port 8006)
Handles authentication, OTP verification, and session management.
"""
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

import random
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from shared.config import settings

app = FastAPI(
    title="FinCore AI — Identity Service",
    description="OTP-based authentication and identity verification.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory OTP store (use Redis in production)
otp_store = {}


class OTPPayload(BaseModel):
    phone_number: str


@app.get("/")
def health():
    return {"service": "identity-service", "status": "running", "port": settings.IDENTITY_SERVICE_PORT}


@app.post("/send-otp")
def send_otp(otp_req: OTPPayload):
    """Generate and send a 6-digit OTP via Squad SMS API."""
    otp_code = str(random.randint(100000, 999999))
    otp_store[otp_req.phone_number] = otp_code

    url = f"{settings.SQUAD_BASE_URL}/sms/send/instant"
    payload = {
        "sender_id": "S-Alert",
        "messages": [
            {
                "phone_number": otp_req.phone_number,
                "message": f"FinCore AI Security Alert: Your verification code is {otp_code}. Do NOT share this code."
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {settings.SQUAD_API_KEY}",
        "Content-Type": "application/json"
    }
    resp = requests.post(url, headers=headers, json=payload)
    return {
        "status": "OTP sent",
        "squad_response": resp.json(),
        "hint_for_testing": otp_code  # Remove in production
    }


@app.post("/verify-otp")
def verify_otp(phone_number: str, otp: str):
    """Verify a previously sent OTP."""
    stored = otp_store.get(phone_number)
    if not stored:
        raise HTTPException(status_code=404, detail="No OTP found for this number")
    if stored != otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    del otp_store[phone_number]
    return {"status": "verified", "message": "Identity confirmed. Transaction approved."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.IDENTITY_SERVICE_PORT)
