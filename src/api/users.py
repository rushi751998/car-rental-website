# PI: UserAuth - Users API (register, login, logout, me)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime
import secrets
from src.db_ops import Database

router = APIRouter(tags=["users"])

db = Database()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    token: str

@router.post("/api/users/register")
def register_user(payload: UserCreate):
    # Check if exists
    existing = db.fetchone("SELECT id FROM users WHERE username = ? OR email = ?", (payload.username, payload.email))
    if existing:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")
    pwd_hash = pwd_context.hash(payload.password)
    db.insert(
        """
        INSERT INTO users (username, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (payload.username, payload.email, pwd_hash, datetime.utcnow().isoformat()),
    )
    return {"message": "User registered successfully"}

@router.post("/api/users/login")
def login_user(payload: UserLogin):
    user = db.fetchone("SELECT id, password_hash FROM users WHERE username = ?", (payload.username,))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # sqlite3.Row supports key access
    user_id = user[0] if isinstance(user, tuple) else user["id"]
    pwd_hash = user[1] if isinstance(user, tuple) else user["password_hash"]
    if not pwd_context.verify(payload.password, pwd_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = secrets.token_urlsafe(32)
    db.insert(
        """
        INSERT INTO sessions (user_id, token, created_at)
        VALUES (?, ?, ?)
        """,
        (user_id, token, datetime.utcnow().isoformat()),
    )
    return {"message": "Login successful", "token": token}

@router.post("/api/users/logout")
def logout_user(token: Token):
    deleted = db.execute("DELETE FROM sessions WHERE token = ?", (token.token,))
    return {"message": "Logged out"}

@router.get("/api/users/me")
def get_me(token: str):
    sess = db.fetchone("SELECT user_id FROM sessions WHERE token = ?", (token,))
    if not sess:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_id = sess[0] if isinstance(sess, tuple) else sess["user_id"]
    user = db.fetchone_dict("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,))
    return {"user": user}
