from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI(title="Account Service")
engine = create_engine("sqlite:///./accounts.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(String, primary_key=True)
    owner = Column(String, index=True)
    balance = Column(Float, default=0.0)

Base.metadata.create_all(bind=engine)

# Seed initial accounts on startup
@app.on_event("startup")
def seed():
    db = SessionLocal()
    if not db.query(Account).first():
        db.add_all([
            Account(account_id="ACC1001", owner="alice", balance=5000.0),
            Account(account_id="ACC1002", owner="bob", balance=2500.0),
        ])
        db.commit()
    db.close()

class BalanceUpdate(BaseModel):
    amount: float  # Positive to credit, negative to debit

@app.get("/accounts/{owner}")
def get_account(owner: str):
    db = SessionLocal()
    acc = db.query(Account).filter(Account.owner == owner).first()
    db.close()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": acc.account_id, "owner": acc.owner, "balance": acc.balance}

@app.post("/accounts/{account_id}/adjust")
def adjust_balance(account_id: str, update: BalanceUpdate):
    db = SessionLocal()
    acc = db.query(Account).filter(Account.account_id == account_id).first()
    if not acc:
        db.close()
        raise HTTPException(status_code=404, detail="Account not found")
    if acc.balance + update.amount < 0:
        db.close()
        raise HTTPException(status_code=400, detail="Insufficient funds")
    acc.balance += update.amount
    db.commit()
    new_balance = acc.balance
    db.close()
    return {"account_id": account_id, "new_balance": new_balance}