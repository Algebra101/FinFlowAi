"""
FinCore AI — Payment Service (Port 8001)
Handles all Squad API integrations:
  - Virtual Account creation
  - Webhook processing
  - Account Lookup & Transfers
  - Payment Gateway initiation
  - Demo simulation
"""
import sys
import os

# Add project root to Python path for shared module access
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

import json
import hmac
import hashlib
import requests
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from shared.database import SessionLocal, SMEUser, VirtualAccount, Transaction, FraudFlag, WebhookLog
from shared.database.session import get_db
from shared.database.models import Base
from shared.database.session import engine
from shared.config import settings

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinCore AI — Payment Service",
    description="Squad API integration for payments, transfers, and virtual accounts.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Squad API Helpers ---
def get_squad_headers():
    return {
        "Authorization": f"Bearer {settings.SQUAD_API_KEY}",
        "Content-Type": "application/json"
    }


# --- Pydantic Schemas ---
from pydantic import BaseModel


class SMEPayload(BaseModel):
    business_name: str
    bvn: str
    phone_number: str
    gtbank_account: str


class TransferPayload(BaseModel):
    transaction_reference: str
    amount: int  # Kobo (₦100 = 10000)
    bank_code: str
    account_number: str
    account_name: str
    remark: str


class SimulatePayload(BaseModel):
    virtual_account_number: str
    amount: int  # Kobo


class LookupPayload(BaseModel):
    bank_code: str
    account_number: str


# ========== HEALTH CHECK ==========
@app.get("/")
def health():
    return {"service": "payment-service", "status": "running", "port": settings.PAYMENT_SERVICE_PORT}


# ========== VIRTUAL ACCOUNT CREATION ==========
@app.post("/virtual-account")
def create_virtual_account(sme: SMEPayload, db: Session = Depends(get_db)):
    url = f"{settings.SQUAD_BASE_URL}/virtual-account/business"
    payload = {
        "business_name": sme.business_name,
        "bvn": sme.bvn,
        "customer_identifier": sme.phone_number,
        "mobile_num": sme.phone_number,
        "beneficiary_account": sme.gtbank_account
    }
    response = requests.post(url, headers=get_squad_headers(), json=payload)
    data = response.json()

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Squad API Error: {data}")

    virtual_account_number = data["data"]["virtual_account_number"]

    new_sme = SMEUser(
        business_name=sme.business_name,
        bvn=sme.bvn,
        phone_number=sme.phone_number
    )
    db.add(new_sme)
    db.commit()
    db.refresh(new_sme)

    new_va = VirtualAccount(
        sme_id=new_sme.id,
        account_number=virtual_account_number,
        account_name=sme.business_name,
        bank_name="GTBank",
        label="Revenue"
    )
    db.add(new_va)
    db.commit()

    return {
        "status": "success",
        "sme_id": new_sme.id,
        "virtual_account_number": virtual_account_number
    }


# ========== SQUAD WEBHOOK HANDLER ==========
@app.post("/webhook/squad")
async def squad_webhook(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()
    payload = json.loads(raw_body)

    txn_ref = payload.get("transaction_reference", "")

    # Idempotency check
    existing = db.query(WebhookLog).filter(WebhookLog.transaction_ref == txn_ref).first()
    if existing:
        return {"status": "duplicate, already processed"}

    # HMAC-SHA512 signature verification
    squad_signature = request.headers.get("x-squad-encrypted-body", "")
    expected_hash = hmac.new(
        settings.SQUAD_API_KEY.encode("utf-8"),
        raw_body,
        hashlib.sha512
    ).hexdigest()

    if squad_signature and squad_signature != expected_hash:
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Log the webhook
    log = WebhookLog(transaction_ref=txn_ref, payload=raw_body.decode("utf-8"))
    db.add(log)

    # Save the transaction
    amount = payload.get("amount", 0)
    txn = Transaction(
        account_id=payload.get("virtual_account_number", ""),
        amount=amount / 100,  # Kobo → Naira
        transaction_type="Credit",
        narration=payload.get("transaction_ref", "Squad Inbound"),
        source="squad",
        date=datetime.utcnow()
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    # Conservation Law Check (PINN F-II) — forward to fraud service
    va = db.query(VirtualAccount).filter(
        VirtualAccount.account_number == payload.get("virtual_account_number")
    ).first()

    if va:
        all_txns = db.query(Transaction).filter(
            Transaction.account_id == va.account_number
        ).all()
        expected_balance = sum(
            t.amount if t.transaction_type == "Credit" else -t.amount
            for t in all_txns
        )
        observed_balance = payload.get("principal_amount", amount) / 100
        difference = abs(expected_balance - observed_balance)

        if difference > 1000:  # ₦1000 threshold
            flag = FraudFlag(
                sme_id=va.sme_id,
                transaction_id=txn.id,
                pinn_law_violated="F-II: Conservation Law (Ghost Spike)",
                c_score_tier="RED",
                timestamp=datetime.utcnow()
            )
            db.add(flag)
            db.commit()
            return {"status": "FRAUD DETECTED", "law": "Conservation", "tier": "RED"}

    db.commit()
    return {"status": "success", "transaction_id": txn.id}


# ========== ACCOUNT LOOKUP ==========
@app.post("/account-lookup")
def account_lookup(payload: LookupPayload):
    url = f"{settings.SQUAD_BASE_URL}/payout/account/lookup"
    squad_payload = {
        "bank_code": payload.bank_code,
        "account_number": payload.account_number
    }
    resp = requests.post(url, headers=get_squad_headers(), json=squad_payload)
    return resp.json()


# ========== TRANSFER FUNDS ==========
@app.post("/transfer")
def transfer_funds(transfer: TransferPayload):
    # Step 1: Verify the recipient
    lookup_url = f"{settings.SQUAD_BASE_URL}/payout/account/lookup"
    lookup_payload = {
        "bank_code": transfer.bank_code,
        "account_number": transfer.account_number
    }
    lookup_resp = requests.post(lookup_url, headers=get_squad_headers(), json=lookup_payload)
    if lookup_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Account lookup failed")

    # Step 2: Execute transfer
    transfer_url = f"{settings.SQUAD_BASE_URL}/payout/transfer"
    transfer_payload = {
        "transaction_reference": transfer.transaction_reference,
        "amount": str(transfer.amount),
        "bank_code": transfer.bank_code,
        "account_number": transfer.account_number,
        "account_name": transfer.account_name,
        "currency_id": "NGN",
        "remark": transfer.remark
    }
    resp = requests.post(transfer_url, headers=get_squad_headers(), json=transfer_payload)
    return resp.json()


# ========== PAYMENT GATEWAY ==========
@app.post("/initiate-payment")
def initiate_payment(email: str, amount: int, transaction_ref: str):
    url = f"{settings.SQUAD_BASE_URL}/transaction/initiate"
    payload = {
        "email": email,
        "amount": amount,
        "currency": "NGN",
        "initiate_type": "inline",
        "transaction_ref": transaction_ref,
        "callback_url": f"http://localhost:{settings.PAYMENT_SERVICE_PORT}/webhook/squad"
    }
    resp = requests.post(url, headers=get_squad_headers(), json=payload)
    return resp.json()


# ========== DEMO SIMULATOR ==========
@app.post("/demo/simulate-payment")
def simulate_payment(sim: SimulatePayload):
    url = f"{settings.SQUAD_BASE_URL}/virtual-account/simulate/payment"
    payload = {
        "virtual_account_number": sim.virtual_account_number,
        "amount": str(sim.amount)
    }
    resp = requests.post(url, headers=get_squad_headers(), json=payload)
    return resp.json()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PAYMENT_SERVICE_PORT)
