import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="Digital Banking Frontend")

AUTH_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
ACCOUNT_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://localhost:8002")
BENEFICIARY_URL = os.getenv("BENEFICIARY_SERVICE_URL", "http://localhost:8003")
PAYMENT_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8004")
TRANSACTION_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://localhost:8005")

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open(os.path.join(os.path.dirname(__file__), "index.html"), "r", encoding="utf-8") as f:
        return f.read()

async def forward(method: str, url: str, payload: dict = None):
    async with httpx.AsyncClient() as client:
        res = await client.request(method, url, json=payload)
        if res.status_code >= 400:
            detail = res.json().get("detail", "Service error")
            raise HTTPException(status_code=res.status_code, detail=detail)
        return res.json()

@app.post("/api/login")
async def login(req: Request):
    return await forward("POST", f"{AUTH_URL}/login", await req.json())

@app.get("/api/dashboard/{user}")
async def dashboard(user: str):
    account = await forward("GET", f"{ACCOUNT_URL}/accounts/{user}")
    beneficiaries = await forward("GET", f"{BENEFICIARY_URL}/beneficiaries/{user}")
    transactions = await forward("GET", f"{TRANSACTION_URL}/transactions/{account['account_id']}")
    return {"account": account, "beneficiaries": beneficiaries, "transactions": transactions}

@app.post("/api/beneficiaries")
async def add_beneficiary(req: Request):
    return await forward("POST", f"{BENEFICIARY_URL}/beneficiaries", await req.json())

@app.post("/api/transfer")
async def transfer(req: Request):
    return await forward("POST", f"{PAYMENT_URL}/transfer", await req.json())