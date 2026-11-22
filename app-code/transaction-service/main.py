from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI(title="Transaction Service")
engine = create_engine("sqlite:///./transactions.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    from_account = Column(String, index=True)
    to_account = Column(String, index=True)
    amount = Column(Float)
    status = Column(String)  # SUCCESS or FAILED

Base.metadata.create_all(bind=engine)

class TransactionCreate(BaseModel):
    from_account: str
    to_account: str
    amount: float
    status: str

@app.post("/transactions")
def log_transaction(tx: TransactionCreate):
    db = SessionLocal()
    record = Transaction(**tx.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    db.close()
    return record

@app.get("/transactions/{account_id}")
def get_history(account_id: str):
    db = SessionLocal()
    records = db.query(Transaction).filter(
        (Transaction.from_account == account_id) | (Transaction.to_account == account_id)
    ).all()
    db.close()
    return records