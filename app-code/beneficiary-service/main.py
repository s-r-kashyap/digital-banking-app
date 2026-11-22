from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI(title="Beneficiary Service")
engine = create_engine("sqlite:///./beneficiaries.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Beneficiary(Base):
    __tablename__ = "beneficiaries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner = Column(String, index=True)
    name = Column(String)
    target_account_id = Column(String)

Base.metadata.create_all(bind=engine)

class BeneficiaryCreate(BaseModel):
    owner: str
    name: str
    target_account_id: str

@app.post("/beneficiaries")
def add_beneficiary(item: BeneficiaryCreate):
    db = SessionLocal()
    ben = Beneficiary(**item.model_dump())
    db.add(ben)
    db.commit()
    db.refresh(ben)
    db.close()
    return ben

@app.get("/beneficiaries/{owner}")
def list_beneficiaries(owner: str):
    db = SessionLocal()
    items = db.query(Beneficiary).filter(Beneficiary.owner == owner).all()
    db.close()
    return items