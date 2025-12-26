# PI: UserAuth - Users API (register, login, logout, me)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import bcrypt
from datetime import datetime
import secrets
from src.db_ops import Database

router = APIRouter(tags=["users"])

db = Database()


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    token: str


@router.post("/api/users/register")
def register_user(payload: UserCreate):
    # Validate password match
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    # Check if email already exists
    existing = db.fetchone(
        "SELECT id FROM users WHERE email = ?",
        (payload.email,),
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )
    # Hash password and create user
    password_bytes = payload.password.encode("utf-8")
    salt = bcrypt.gensalt()
    pwd_hash = bcrypt.hashpw(password_bytes, salt).decode("utf-8")
    db.insert(
        """
        INSERT INTO users (full_name, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (payload.full_name, payload.email, pwd_hash, datetime.utcnow().isoformat()),
    )
    return {"message": "User registered successfully"}


@router.post("/api/users/login")
def login_user(payload: UserLogin):
    user = db.fetchone(
        "SELECT email, password_hash, full_name FROM users WHERE email = ?",
        (payload.email,),
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # sqlite3.Row supports key access
    user_email = user[0] if isinstance(user, tuple) else user["email"]
    pwd_hash = user[1] if isinstance(user, tuple) else user["password_hash"]
    full_name = user[2] if isinstance(user, tuple) else user["full_name"]
    password_bytes = payload.password.encode("utf-8")
    pwd_hash_bytes = pwd_hash.encode("utf-8")
    if not bcrypt.checkpw(password_bytes, pwd_hash_bytes):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = secrets.token_urlsafe(32)
    db.insert(
        """
        INSERT INTO sessions (user_email, token, created_at)
        VALUES (?, ?, ?)
        """,
        (user_email, token, datetime.utcnow().isoformat()),
    )
    return {
        "message": "Login successful",
        "token": token,
        "email": user_email,
        "full_name": full_name,
    }


@router.post("/api/users/logout")
def logout_user(token: Token):
    db.execute("DELETE FROM sessions WHERE token = ?", (token.token,))
    return {"message": "Logged out"}


@router.get("/api/users/me")
def get_me(token: str):
    sess = db.fetchone("SELECT user_email FROM sessions WHERE token = ?", (token,))
    if not sess:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_email = sess[0] if isinstance(sess, tuple) else sess["user_email"]
    user = db.fetchone_dict(
        "SELECT full_name, email, created_at FROM users WHERE email = ?", (user_email,)
    )
    return {"user": user}
