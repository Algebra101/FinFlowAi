"""
FinCore AI — API Gateway (Port 8000)
Central orchestration layer. The frontend ONLY talks to this service.
Routes requests to the appropriate microservice via HTTP proxying.

Architecture:
  Frontend → API Gateway (8000) → Payment Service (8001)
                                → Banking Service (8002)
                                → Fraud Service (8003)
                                → Credit Service (8004)
                                → Forecasting Service (8005)
                                → Identity Service (8006)
"""
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.config import settings

app = FastAPI(
    title="FinCore AI — API Gateway",
    description="Central request orchestrator. All frontend traffic enters here.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Service Registry ---
SERVICE_MAP = {
    "payment": settings.PAYMENT_SERVICE_URL,
    "banking": settings.BANKING_SERVICE_URL,
    "fraud": settings.FRAUD_SERVICE_URL,
    "credit": settings.CREDIT_SERVICE_URL,
    "forecast": settings.FORECASTING_SERVICE_URL,
    "identity": settings.IDENTITY_SERVICE_URL,
}


# --- Proxy Helper ---
async def proxy_request(service_url: str, path: str, request: Request):
    """Forward a request to an internal microservice and return its response."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{service_url}{path}"

        # Forward query params
        params = dict(request.query_params)

        try:
            if request.method == "GET":
                resp = await client.get(url, params=params)
            elif request.method == "POST":
                body = await request.body()
                headers = {"Content-Type": "application/json"}
                resp = await client.post(url, content=body, headers=headers, params=params)
            elif request.method == "PUT":
                body = await request.body()
                headers = {"Content-Type": "application/json"}
                resp = await client.put(url, content=body, headers=headers, params=params)
            elif request.method == "DELETE":
                resp = await client.delete(url, params=params)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")

            return JSONResponse(status_code=resp.status_code, content=resp.json())

        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {service_url} is not running"
            )


# ========== HEALTH CHECK ==========
@app.get("/")
def health():
    return {
        "service": "api-gateway",
        "status": "running",
        "port": settings.API_GATEWAY_PORT,
        "services": SERVICE_MAP
    }


@app.get("/health")
async def health_check():
    """Check the health of all downstream services."""
    results = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in SERVICE_MAP.items():
            try:
                resp = await client.get(f"{url}/")
                results[name] = {"status": "up", "url": url}
            except Exception:
                results[name] = {"status": "down", "url": url}
    return {"gateway": "running", "services": results}


# ========== PAYMENT SERVICE ROUTES ==========
@app.api_route("/api/virtual-account", methods=["POST"])
async def gw_virtual_account(request: Request):
    return await proxy_request(settings.PAYMENT_SERVICE_URL, "/virtual-account", request)


@app.api_route("/api/webhook/squad", methods=["POST"])
async def gw_webhook(request: Request):
    return await proxy_request(settings.PAYMENT_SERVICE_URL, "/webhook/squad", request)


@app.api_route("/api/account-lookup", methods=["POST"])
async def gw_account_lookup(request: Request):
    return await proxy_request(settings.PAYMENT_SERVICE_URL, "/account-lookup", request)


@app.api_route("/api/transfer", methods=["POST"])
async def gw_transfer(request: Request):
    return await proxy_request(settings.PAYMENT_SERVICE_URL, "/transfer", request)


@app.api_route("/api/initiate-payment", methods=["POST"])
async def gw_initiate_payment(request: Request):
    return await proxy_request(settings.PAYMENT_SERVICE_URL, "/initiate-payment", request)


@app.api_route("/api/demo/simulate-payment", methods=["POST"])
async def gw_simulate(request: Request):
    return await proxy_request(settings.PAYMENT_SERVICE_URL, "/demo/simulate-payment", request)


# ========== BANKING SERVICE ROUTES ==========
@app.api_route("/api/mono/exchange", methods=["POST"])
async def gw_mono_exchange(request: Request):
    return await proxy_request(settings.BANKING_SERVICE_URL, "/exchange", request)


@app.api_route("/api/mono/balance/{account_id}", methods=["GET"])
async def gw_mono_balance(account_id: str, request: Request):
    return await proxy_request(settings.BANKING_SERVICE_URL, f"/balance/{account_id}", request)


@app.api_route("/api/mono/transactions/{account_id}", methods=["GET"])
async def gw_mono_transactions(account_id: str, request: Request):
    return await proxy_request(settings.BANKING_SERVICE_URL, f"/transactions/{account_id}", request)


@app.api_route("/api/mono/linked-accounts/{sme_id}", methods=["GET"])
async def gw_linked_accounts(sme_id: int, request: Request):
    return await proxy_request(settings.BANKING_SERVICE_URL, f"/linked-accounts/{sme_id}", request)


# ========== FRAUD SERVICE ROUTES ==========
@app.api_route("/api/fraud/analyze", methods=["POST"])
async def gw_fraud_analyze(request: Request):
    return await proxy_request(settings.FRAUD_SERVICE_URL, "/analyze", request)


@app.api_route("/api/fraud/flags/{sme_id}", methods=["GET"])
async def gw_fraud_flags(sme_id: int, request: Request):
    return await proxy_request(settings.FRAUD_SERVICE_URL, f"/flags/{sme_id}", request)


@app.api_route("/api/fraud/risk-summary/{sme_id}", methods=["GET"])
async def gw_risk_summary(sme_id: int, request: Request):
    return await proxy_request(settings.FRAUD_SERVICE_URL, f"/risk-summary/{sme_id}", request)


# ========== CREDIT SERVICE ROUTES ==========
@app.api_route("/api/credit/score/{sme_id}", methods=["GET"])
async def gw_credit_score(sme_id: int, request: Request):
    return await proxy_request(settings.CREDIT_SERVICE_URL, f"/score/{sme_id}", request)


# ========== FORECASTING SERVICE ROUTES ==========
@app.api_route("/api/forecast/{account_id}", methods=["GET"])
async def gw_forecast(account_id: str, request: Request):
    return await proxy_request(settings.FORECASTING_SERVICE_URL, f"/forecast/{account_id}", request)


# ========== IDENTITY SERVICE ROUTES ==========
@app.api_route("/api/send-otp", methods=["POST"])
async def gw_send_otp(request: Request):
    return await proxy_request(settings.IDENTITY_SERVICE_URL, "/send-otp", request)


@app.api_route("/api/verify-otp", methods=["POST"])
async def gw_verify_otp(request: Request):
    return await proxy_request(settings.IDENTITY_SERVICE_URL, "/verify-otp", request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.API_GATEWAY_PORT)
