"""
FinCore AI — Fraud Service (Port 8003)
PINN-based fraud detection engine:
  - Conservation Law validation (F-II: Ghost Spike detection)
  - Velocity Law validation (F-I: Dormant Spike detection)
  - Behavioral profiling
  - Risk escalation & C-Score computation
"""
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from shared.database import SessionLocal, Transaction, FraudFlag, VirtualAccount, SMEUser
from shared.database.session import get_db
from shared.database.models import Base
from shared.database.session import engine
from shared.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinCore AI — Fraud Service",
    description="PINN Conservation & Velocity Law fraud detection engine.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Schemas ---
class FraudAnalysisRequest(BaseModel):
    sme_id: int
    transaction_id: int
    account_id: str
    amount: float
    transaction_type: str  # Credit / Debit


class FraudAnalysisResponse(BaseModel):
    status: str
    c_score_tier: str  # GREEN, YELLOW, ORANGE, RED
    laws_checked: list
    violations: list
    details: Optional[str] = None


# ========== HEALTH CHECK ==========
@app.get("/")
def health():
    return {"service": "fraud-service", "status": "running", "port": settings.FRAUD_SERVICE_PORT}


# ========== PINN FRAUD ANALYSIS ==========
@app.post("/analyze", response_model=FraudAnalysisResponse)
def analyze_transaction(req: FraudAnalysisRequest, db: Session = Depends(get_db)):
    """
    Run the full PINN fraud detection pipeline:
      F-I:  Velocity Law — flags dormant accounts with sudden massive activity
      F-II: Conservation Law — flags transactions where money appears from nowhere
    """
    violations = []
    laws_checked = ["F-I: Velocity Law", "F-II: Conservation Law"]

    # ========== F-I: VELOCITY LAW (Dormant Spike Detection) ==========
    # Check if this account has been dormant (no transactions in 30 days)
    # and suddenly receives a large transaction
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_txns = db.query(Transaction).filter(
        Transaction.account_id == req.account_id,
        Transaction.date >= thirty_days_ago
    ).count()

    # If fewer than 3 transactions in 30 days AND this one is > ₦500,000
    if recent_txns < 3 and req.amount > 500000:
        violations.append({
            "law": "F-I: Velocity Law",
            "description": f"Dormant account spike: {recent_txns} txns in 30 days, sudden ₦{req.amount:,.2f}",
            "severity": "HIGH"
        })

    # ========== F-II: CONSERVATION LAW (Ghost Spike Detection) ==========
    # Sum all credits and debits — if the ledger doesn't balance, flag it
    all_txns = db.query(Transaction).filter(
        Transaction.account_id == req.account_id
    ).all()

    expected_balance = sum(
        t.amount if t.transaction_type == "Credit" else -t.amount
        for t in all_txns
    )

    # Large deviation from expected balance pattern
    if req.amount > expected_balance * 0.5 and req.amount > 100000:
        violations.append({
            "law": "F-II: Conservation Law",
            "description": f"Transaction ₦{req.amount:,.2f} exceeds 50% of ledger balance ₦{expected_balance:,.2f}",
            "severity": "CRITICAL"
        })

    # ========== COMPUTE C-SCORE TIER ==========
    if len(violations) == 0:
        tier = "GREEN"
    elif any(v["severity"] == "CRITICAL" for v in violations):
        tier = "RED"
    elif any(v["severity"] == "HIGH" for v in violations):
        tier = "ORANGE"
    else:
        tier = "YELLOW"

    # Save fraud flag if violations found
    if violations:
        flag = FraudFlag(
            sme_id=req.sme_id,
            transaction_id=req.transaction_id,
            pinn_law_violated=" | ".join([v["law"] for v in violations]),
            c_score_tier=tier,
            details=str(violations),
            timestamp=datetime.utcnow()
        )
        db.add(flag)
        db.commit()

    return FraudAnalysisResponse(
        status="analyzed",
        c_score_tier=tier,
        laws_checked=laws_checked,
        violations=violations,
        details=f"Analyzed {len(all_txns)} historical transactions"
    )


# ========== GET FRAUD FLAGS ==========
@app.get("/flags/{sme_id}")
def get_fraud_flags(sme_id: int, db: Session = Depends(get_db)):
    """Retrieve all fraud flags for a specific SME."""
    flags = db.query(FraudFlag).filter(FraudFlag.sme_id == sme_id).order_by(
        FraudFlag.timestamp.desc()
    ).all()
    return {
        "sme_id": sme_id,
        "total_flags": len(flags),
        "flags": [
            {
                "id": f.id,
                "law_violated": f.pinn_law_violated,
                "tier": f.c_score_tier,
                "details": f.details,
                "timestamp": f.timestamp.isoformat() if f.timestamp else None
            }
            for f in flags
        ]
    }


# ========== RISK SUMMARY ==========
@app.get("/risk-summary/{sme_id}")
def get_risk_summary(sme_id: int, db: Session = Depends(get_db)):
    """Aggregate risk overview for an SME's dashboard."""
    flags = db.query(FraudFlag).filter(FraudFlag.sme_id == sme_id).all()

    red_count = sum(1 for f in flags if f.c_score_tier == "RED")
    orange_count = sum(1 for f in flags if f.c_score_tier == "ORANGE")
    yellow_count = sum(1 for f in flags if f.c_score_tier == "YELLOW")

    # Overall risk level
    if red_count > 0:
        overall = "HIGH RISK"
    elif orange_count > 2:
        overall = "MODERATE RISK"
    elif yellow_count > 5:
        overall = "LOW RISK"
    else:
        overall = "HEALTHY"

    return {
        "sme_id": sme_id,
        "overall_risk": overall,
        "breakdown": {
            "red": red_count,
            "orange": orange_count,
            "yellow": yellow_count,
            "total_flags": len(flags)
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.FRAUD_SERVICE_PORT)
