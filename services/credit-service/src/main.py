"""
FinCore AI — Credit Service (Port 8004)
Alternative credit scoring engine using behavioral analysis.
Placeholder — will be populated when ML teammate delivers the credit model.
"""
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from shared.database import CreditScore, SMEUser
from shared.database.session import get_db
from shared.database.models import Base
from shared.database.session import engine
from shared.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinCore AI — Credit Service",
    description="Behavioral credit scoring and loan recommendations.",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/")
def health():
    return {"service": "credit-service", "status": "running", "port": settings.CREDIT_SERVICE_PORT}


@app.get("/score/{sme_id}")
def get_credit_score(sme_id: int, db: Session = Depends(get_db)):
    """Get the latest credit score for an SME. Returns mock data until ML model is integrated."""
    score = db.query(CreditScore).filter(CreditScore.sme_id == sme_id).order_by(
        CreditScore.timestamp.desc()
    ).first()

    if score:
        return {
            "sme_id": sme_id,
            "score": score.score,
            "risk_band": score.risk_band,
            "eligible_limit": score.eligible_limit,
            "timestamp": score.timestamp.isoformat()
        }

    # Mock response for demo
    return {
        "sme_id": sme_id,
        "score": 720,
        "risk_band": "Good",
        "eligible_limit": 2500000.0,
        "source": "mock — awaiting ML model integration"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.CREDIT_SERVICE_PORT)
