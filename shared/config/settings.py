"""
FinCore AI — Centralized Configuration
All environment variables and service URLs are managed here.
Every microservice imports from this single source of truth.
"""
import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


class Settings:
    """Application-wide configuration."""

    # --- Squad API ---
    SQUAD_API_KEY: str = os.getenv("SQUAD_API_KEY", "")
    SQUAD_BASE_URL: str = os.getenv("SQUAD_BASE_URL", "https://sandbox-api-d.squadco.com")

    # --- Mono API ---
    MONO_SECRET_KEY: str = os.getenv("MONO_SECRET_KEY", "")
    MONO_PUBLIC_KEY: str = os.getenv("MONO_PUBLIC_KEY", "")
    MONO_BASE_URL: str = os.getenv("MONO_BASE_URL", "https://api.withmono.com/v2")

    # --- Database ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fincore.db")

    # --- Service Ports (Microservice Architecture) ---
    API_GATEWAY_PORT: int = int(os.getenv("API_GATEWAY_PORT", "8000"))
    PAYMENT_SERVICE_PORT: int = int(os.getenv("PAYMENT_SERVICE_PORT", "8001"))
    BANKING_SERVICE_PORT: int = int(os.getenv("BANKING_SERVICE_PORT", "8002"))
    FRAUD_SERVICE_PORT: int = int(os.getenv("FRAUD_SERVICE_PORT", "8003"))
    CREDIT_SERVICE_PORT: int = int(os.getenv("CREDIT_SERVICE_PORT", "8004"))
    FORECASTING_SERVICE_PORT: int = int(os.getenv("FORECASTING_SERVICE_PORT", "8005"))
    IDENTITY_SERVICE_PORT: int = int(os.getenv("IDENTITY_SERVICE_PORT", "8006"))

    # --- Internal Service URLs (used by API Gateway) ---
    @property
    def PAYMENT_SERVICE_URL(self) -> str:
        return f"http://localhost:{self.PAYMENT_SERVICE_PORT}"

    @property
    def BANKING_SERVICE_URL(self) -> str:
        return f"http://localhost:{self.BANKING_SERVICE_PORT}"

    @property
    def FRAUD_SERVICE_URL(self) -> str:
        return f"http://localhost:{self.FRAUD_SERVICE_PORT}"

    @property
    def CREDIT_SERVICE_URL(self) -> str:
        return f"http://localhost:{self.CREDIT_SERVICE_PORT}"

    @property
    def FORECASTING_SERVICE_URL(self) -> str:
        return f"http://localhost:{self.FORECASTING_SERVICE_PORT}"

    @property
    def IDENTITY_SERVICE_URL(self) -> str:
        return f"http://localhost:{self.IDENTITY_SERVICE_PORT}"


settings = Settings()
