"""
FinCore AI — Domain Models (SQLAlchemy ORM)
All entity definitions for the FinCore platform.
Shared across all microservices to enforce schema consistency.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class SMEUser(Base):
    """Small & Medium Enterprise user — the core business entity."""
    __tablename__ = "sme_users"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String, index=True)
    bvn = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    virtual_accounts = relationship("VirtualAccount", back_populates="sme")
    linked_accounts = relationship("LinkedBankAccount", back_populates="sme")
    fraud_flags = relationship("FraudFlag", back_populates="sme")
    credit_scores = relationship("CreditScore", back_populates="sme")


class VirtualAccount(Base):
    """Squad-issued virtual account (NUBAN) for payment collection."""
    __tablename__ = "virtual_accounts"

    id = Column(Integer, primary_key=True, index=True)
    sme_id = Column(Integer, ForeignKey("sme_users.id"))
    account_number = Column(String, unique=True, index=True)
    account_name = Column(String)
    bank_name = Column(String)
    label = Column(String)  # e.g., "Revenue", "Tax", "Payroll"

    sme = relationship("SMEUser", back_populates="virtual_accounts")


class LinkedBankAccount(Base):
    """External bank account linked via Mono Open Banking."""
    __tablename__ = "linked_bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    sme_id = Column(Integer, ForeignKey("sme_users.id"))
    mono_account_id = Column(String, unique=True, index=True)
    bank_name = Column(String)
    account_name = Column(String)
    account_number = Column(String)
    balance = Column(Float, default=0.0)
    label = Column(String)

    sme = relationship("SMEUser", back_populates="linked_accounts")


class Transaction(Base):
    """Unified transaction record from Squad webhooks and Mono pulls."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, index=True)  # Squad NUBAN or Mono Account ID
    amount = Column(Float)
    transaction_type = Column(String)  # Credit / Debit
    narration = Column(String)
    source = Column(String, default="squad")  # "squad" or "mono"
    date = Column(DateTime, default=datetime.utcnow)


class FraudFlag(Base):
    """Fraud detection result from the PINN Conservation Law engine."""
    __tablename__ = "fraud_flags"

    id = Column(Integer, primary_key=True, index=True)
    sme_id = Column(Integer, ForeignKey("sme_users.id"))
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    pinn_law_violated = Column(String)  # e.g., "F-II: Conservation Law (Ghost Spike)"
    c_score_tier = Column(String)  # RED, ORANGE, YELLOW, GREEN
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sme = relationship("SMEUser", back_populates="fraud_flags")
    transaction = relationship("Transaction")


class CreditScore(Base):
    """Alternative credit score computed by behavioral analysis."""
    __tablename__ = "credit_scores"

    id = Column(Integer, primary_key=True, index=True)
    sme_id = Column(Integer, ForeignKey("sme_users.id"))
    score = Column(Integer)  # 0 to 1000
    risk_band = Column(String)  # High Risk, Moderate, Good, Excellent
    eligible_limit = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sme = relationship("SMEUser", back_populates="credit_scores")


class WebhookLog(Base):
    """Idempotency log for Squad webhook deduplication."""
    __tablename__ = "webhook_logs"

    id = Column(Integer, primary_key=True, index=True)
    transaction_ref = Column(String, unique=True, index=True)
    payload = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
