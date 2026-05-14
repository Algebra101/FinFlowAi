"""
FinCore AI — Banking Service (Port 8002)
Handles all Mono Open Banking integrations:
  - Auth code exchange → Account ID
  - Balance retrieval
  - Transaction history ingestion
  - Multi-bank account aggregation
"""
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

import requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from shared.database import SessionLocal, LinkedBankAccount
from shared.database.session import get_db
from shared.database.models import Base
from shared.database.session import engine
from shared.config import settings

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinCore AI — Banking Service",
    description="Mono Open Banking integration for account aggregation and transaction ingestion.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Mono API Helpers ---
def get_mono_headers():
    return {
        "mono-sec-key": settings.MONO_SECRET_KEY,
        "Content-Type": "application/json"
    }


# --- Pydantic Schemas ---
class MonoExchangePayload(BaseModel):
    sme_id: int
    auth_code: str


# ========== HEALTH CHECK ==========
@app.get("/")
def health():
    return {"service": "banking-service", "status": "running", "port": settings.BANKING_SERVICE_PORT}


# ========== MONO AUTH CODE EXCHANGE ==========
@app.post("/exchange")
def mono_exchange_code(payload: MonoExchangePayload, db: Session = Depends(get_db)):
    """Exchange a Mono Connect widget auth_code for a permanent account_id."""
    url = f"{settings.MONO_BASE_URL}/accounts/auth"
    resp = requests.post(url, headers=get_mono_headers(), json={"code": payload.auth_code})

    if resp.status_code != 200:
        print("MONO ERROR RESPONSE:", resp.text)
        raise HTTPException(status_code=400, detail="Mono exchange failed")

    response_json = resp.json()
    print("MONO SUCCESS RESPONSE:", response_json)

    # Mono v2 nests the ID inside a "data" object
    account_id = response_json.get("id")
    if not account_id and response_json.get("data"):
        account_id = response_json.get("data", {}).get("id")

    if not account_id:
        raise HTTPException(status_code=500, detail="Could not extract Account ID from Mono response")

    # Persist the linked bank account
    new_link = LinkedBankAccount(
        sme_id=payload.sme_id,
        mono_account_id=account_id,
        bank_name="Linked Bank",
        account_name="Unknown"
    )
    db.add(new_link)
    db.commit()

    return {"status": "success", "mono_account_id": account_id}


# ========== GET BALANCE ==========
@app.get("/balance/{account_id}")
def mono_get_balance(account_id: str, db: Session = Depends(get_db)):
    """Fetch current balance for a linked bank account."""
    url = f"{settings.MONO_BASE_URL}/accounts/{account_id}"
    resp = requests.get(url, headers=get_mono_headers())

    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch balance")

    raw_data = resp.json()
    # Mono v2: data is nested inside data -> account
    account_data = raw_data.get("data", {}).get("account", raw_data)

    # Update the linked account record with real bank info
    link = db.query(LinkedBankAccount).filter(LinkedBankAccount.mono_account_id == account_id).first()
    if link:
        link.bank_name = account_data.get("institution", {}).get("name", "Unknown Bank")
        link.account_name = account_data.get("name", "Unknown Name")
        link.balance = account_data.get("balance", 0)
        db.commit()

    return {
        "balance": account_data.get("balance"),
        "currency": account_data.get("currency"),
        "bank": account_data.get("institution", {}).get("name"),
        "name": account_data.get("name"),
        "account_number": account_data.get("account_number"),
        "type": account_data.get("type")
    }


# ========== GET TRANSACTIONS ==========
@app.get("/transactions/{account_id}")
def mono_get_transactions(account_id: str):
    """Fetch transaction history for a linked bank account."""
    url = f"{settings.MONO_BASE_URL}/accounts/{account_id}/transactions"
    resp = requests.get(url, headers=get_mono_headers())
    return resp.json()


# ========== LIST LINKED ACCOUNTS ==========
@app.get("/linked-accounts/{sme_id}")
def get_linked_accounts(sme_id: int, db: Session = Depends(get_db)):
    """List all bank accounts linked by a specific SME."""
    accounts = db.query(LinkedBankAccount).filter(LinkedBankAccount.sme_id == sme_id).all()
    return {
        "sme_id": sme_id,
        "accounts": [
            {
                "id": a.id,
                "mono_account_id": a.mono_account_id,
                "bank_name": a.bank_name,
                "account_name": a.account_name,
                "balance": a.balance
            }
            for a in accounts
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.BANKING_SERVICE_PORT)
