import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Payment Service")

ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://localhost:8002")
TRANSACTION_SERVICE_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://localhost:8005")

class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: float

@app.post("/transfer")
async def transfer_funds(req: TransferRequest):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    async with httpx.AsyncClient() as client:
        # 1. Debit sender
        debit = await client.post(
            f"{ACCOUNT_SERVICE_URL}/accounts/{req.from_account}/adjust",
            json={"amount": -req.amount}
        )
        if debit.status_code != 200:
            await client.post(f"{TRANSACTION_SERVICE_URL}/transactions", json={
                "from_account": req.from_account, "to_account": req.to_account,
                "amount": req.amount, "status": "FAILED"
            })
            raise HTTPException(status_code=400, detail=debit.json().get("detail", "Debit failed"))

        # 2. Credit receiver (with simple rollback if credit fails)
        credit = await client.post(
            f"{ACCOUNT_SERVICE_URL}/accounts/{req.to_account}/adjust",
            json={"amount": req.amount}
        )
        if credit.status_code != 200:
            await client.post(
                f"{ACCOUNT_SERVICE_URL}/accounts/{req.from_account}/adjust",
                json={"amount": req.amount}
            )
            await client.post(f"{TRANSACTION_SERVICE_URL}/transactions", json={
                "from_account": req.from_account, "to_account": req.to_account,
                "amount": req.amount, "status": "FAILED"
            })
            raise HTTPException(status_code=400, detail="Credit failed, funds refunded")

        # 3. Record successful transaction
        tx = await client.post(f"{TRANSACTION_SERVICE_URL}/transactions", json={
            "from_account": req.from_account, "to_account": req.to_account,
            "amount": req.amount, "status": "SUCCESS"
        })
        return {"message": "Transfer completed", "transaction": tx.json()}