"""
FinCore AI — Forecasting Service (Port 8005)
Delta PINNs-based cash flow forecasting engine.
Placeholder — will be populated when ML teammate delivers the forecasting model.
"""
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from datetime import datetime, timedelta
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from shared.database import Transaction
from shared.database.session import get_db
from shared.database.models import Base
from shared.database.session import engine
from shared.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinCore AI — Forecasting Service",
    description="Delta PINNs cash flow forecasting and liquidity analysis.",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/")
def health():
    return {"service": "forecasting-service", "status": "running", "port": settings.FORECASTING_SERVICE_PORT}


@app.get("/forecast/{account_id}")
def get_forecast(account_id: str, days: int = 90, db: Session = Depends(get_db)):
    """Generate a cash flow forecast. Returns mock projection until Delta PINNs model is integrated."""
    # Get recent transaction history for context
    txns = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).order_by(Transaction.date.desc()).limit(30).all()

    if not txns:
        return {
            "account_id": account_id,
            "forecast": [],
            "message": "No transaction history found"
        }

    # Calculate average daily flow from recent data
    credits = [t.amount for t in txns if t.transaction_type == "Credit"]
    debits = [t.amount for t in txns if t.transaction_type == "Debit"]

    avg_daily_credit = sum(credits) / max(len(credits), 1)
    avg_daily_debit = sum(debits) / max(len(debits), 1)
    net_daily_flow = avg_daily_credit - avg_daily_debit

    # Generate simple linear projection (mock — replace with Delta PINNs)
    forecast = []
    projected_balance = sum(credits) - sum(debits)

    for day in range(1, days + 1):
        projected_balance += net_daily_flow * 0.95  # slight decay factor
        forecast.append({
            "day": day,
            "date": (datetime.utcnow() + timedelta(days=day)).strftime("%Y-%m-%d"),
            "projected_balance": round(projected_balance, 2),
            "confidence": max(0.5, 1.0 - (day * 0.005))  # confidence decreases over time
        })

    return {
        "account_id": account_id,
        "forecast_days": days,
        "avg_daily_credit": round(avg_daily_credit, 2),
        "avg_daily_debit": round(avg_daily_debit, 2),
        "net_daily_flow": round(net_daily_flow, 2),
        "forecast": forecast,
        "source": "linear-projection — awaiting Delta PINNs model integration"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.FORECASTING_SERVICE_PORT)
