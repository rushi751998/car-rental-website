# PI: Chatbot - OpenAI-backed chatbot API with session tracking and planner endpoint
import os
from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from src.db_ops import Database
from src.utils import config

# Optional OpenAI integration
OPENAI_API_KEY = config.OPENAI_API_KEY
client = None
try:
    if OPENAI_API_KEY:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
except Exception:
    client = None

router = APIRouter(tags=["chatbot"])

db = Database()


class ChatRequest(BaseModel):
    session_id: str
    message: str
    token: Optional[str] = None


class TripPlan(BaseModel):
    name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=6)
    destination: str = Field(..., min_length=1)
    query: str = Field("", description="Extra preferences or questions")
    budget: float = Field(..., gt=0)
    days: int = Field(..., gt=0)
    session_id: Optional[str] = None
    token: Optional[str] = None


@router.post("/api/chat")
def chat(req: ChatRequest):
    user_email = None
    if req.token:
        sess = db.fetchone(
            "SELECT user_email FROM sessions WHERE token = ?", (req.token,)
        )
        if sess:
            user_email = sess[0] if isinstance(sess, tuple) else sess["user_email"]

    # Log user message
    db.insert(
        """
        INSERT INTO chat_logs (session_id, user_email, role, message, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            req.session_id,
            user_email,
            "user",
            req.message,
            datetime.utcnow().isoformat(),
        ),
    )

    # Generate reply using OpenAI if configured, otherwise fallback
    reply_text = (
        generate_ai_reply(req.session_id, req.message)
        if client
        else generate_reply(req.message)
    )

    # Log assistant reply
    db.insert(
        """
        INSERT INTO chat_logs (session_id, user_email, role, message, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            req.session_id,
            user_email,
            "assistant",
            reply_text,
            datetime.utcnow().isoformat(),
        ),
    )

    return {"reply": reply_text, "user_email": user_email}


@router.get("/api/chat/history")
def history(session_id: str, limit: int = 50):
    rows = db.fetchall_dicts(
        "SELECT session_id, user_email, role, message, created_at FROM chat_logs WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit),
    )
    return {"messages": list(reversed(rows))}


@router.post("/api/chat/plan")
def submit_plan(plan: TripPlan):
    user_email = None
    if plan.token:
        sess = db.fetchone(
            "SELECT user_email FROM sessions WHERE token = ?", (plan.token,)
        )
        if sess:
            user_email = sess[0] if isinstance(sess, tuple) else sess["user_email"]

    sid = plan.session_id or f"sess_{datetime.utcnow().timestamp()}"

    # Log a single planner summary message
    summary = (
        "Trip plan received:\n"
        f"• Name: {plan.name}\n"
        f"• Address: {plan.address}\n"
        f"• City: {plan.city}\n"
        f"• Phone: {plan.phone}\n"
        f"• Destination: {plan.destination}\n"
        f"• Query: {plan.query}\n"
        f"• Budget: ₹{plan.budget}\n"
        f"• Days: {plan.days}"
    )

    db.insert(
        """
        INSERT INTO chat_logs (session_id, user_email, role, message, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (sid, user_email, "planner", summary, datetime.utcnow().isoformat()),
    )

    # Create WhatsApp message
    whatsapp_message = (
        f"New Trip Plan Request!\n\n"
        f"Name: {plan.name}\n"
        f"Phone: {plan.phone}\n"
        f"City: {plan.city}\n"
        f"Destination: {plan.destination}\n"
        f"Budget: ₹{plan.budget}\n"
        f"Days: {plan.days}\n"
        f"Query: {plan.query}"
    )
    # Generate WhatsApp URL
    import urllib.parse

    whatsapp_url = f"https://wa.me/{config.WHATSAPP_PHONE.replace('+', '')}?text={urllib.parse.quote(whatsapp_message)}"

    return {
        "session_id": sid,
        "summary": summary,
        "whatsapp_url": whatsapp_url,
        "message": "Trip plan received! Click the WhatsApp link to contact us.",
    }


def generate_ai_reply(session_id: str, last_user_message: str) -> str:
    """Call OpenAI Chat Completions with short conversation context."""
    try:
        # Pull last few messages from history for minimal context
        rows = db.fetchall(
            "SELECT role, message FROM chat_logs WHERE session_id = ? ORDER BY id DESC LIMIT 8",
            (session_id,),
        )
        # Build messages in chronological order
        history: List[dict] = []
        for r in reversed(rows):
            role = r[0] if isinstance(r, tuple) else r["role"]
            content = r[1] if isinstance(r, tuple) else r["message"]
            if role not in ("user", "assistant"):
                continue
            history.append(
                {
                    "role": "assistant" if role == "assistant" else "user",
                    "content": content,
                }
            )
        # System prompt to scope the assistant
        system = {
            "role": "system",
            "content": (
                "You are a helpful travel and car rental assistant for a website. "
                "Help users choose cars and picnic destinations around India. "
                "Be concise and friendly. Prices are in INR unless stated."
            ),
        }
        messages = [system] + history + [{"role": "user", "content": last_user_message}]

        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.4,
            max_tokens=300,
        )
        return (resp.choices[0].message.content or "")[:1200] if resp.choices else ""
    except Exception:
        return generate_reply(last_user_message)


def generate_reply(message: str) -> str:
    text = message.strip().lower()
    if any(k in text for k in ["hello", "hi", "hey"]):
        return "Hi! How can I help you with cars or picnic destinations today?"
    if "car" in text and "price" in text:
        return "Our car prices vary by model; you can view details on the car page."
    if "spot" in text or "destination" in text:
        return "Browse our destinations for photos, descriptions, and starting prices."
    return "Thanks for your message! We'll get back with more details."
