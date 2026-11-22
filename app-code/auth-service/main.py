from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Auth Service")

# Hardcoded demo users for simplicity
USERS = {"alice": "password123", "bob": "password123"}
TOKENS = {"token-alice": "alice", "token-bob": "bob"}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(req: LoginRequest):
    if USERS.get(req.username) != req.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": f"token-{req.username}", "user": req.username}

@app.get("/verify/{token}")
def verify(token: str):
    user = TOKENS.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user": user}