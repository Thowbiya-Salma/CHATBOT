# ============================================================
# CHAT ROUTES - DR. URCW AI
# ============================================================

from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.database import get_db
from backend.models import ChatSession, Message, User
from backend.chat_engine import get_bot_response, generate_title
from backend.utils import create_chat_session

router = APIRouter()


# ============================================================
# CHATBOT PAGE
# ============================================================

@router.get("/chatbot", response_class=HTMLResponse)
def chatbot_page(
    request: Request,
    session_id: int | None = Query(None),
    db: Session = Depends(get_db)
):

    # ---------- SESSION VALIDATION ----------
    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    session_user = request.session["user"]

    if session_user["role"] != "student":
        return RedirectResponse("/", status_code=303)

    user_id = session_user["id"]

    # ---------- CREATE NEW SESSION IF NONE ----------
    if session_id is None:
        session_id = create_chat_session(db, user_id)

    # ---------- VERIFY SESSION OWNERSHIP ----------
    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
    ).first()

    if not session:
        return RedirectResponse("/dashboard", status_code=303)

    # ---------- FETCH USER SESSIONS ----------
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == user_id
    ).order_by(ChatSession.updated_at.desc()).all()

    # ---------- FETCH CHAT MESSAGES ----------
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at.asc()).all()

    # Store active session
    request.session["active_chat"] = session_id

    return request.app.templates.TemplateResponse(
        "student/chatbot.html",
        {
            "request": request,
            "user": session_user,
            "sessions": sessions,
            "messages": messages,
            "active_session": session_id
        }
    )


# ============================================================
# SEND CHAT MESSAGE
# ============================================================

@router.post("/chat")
def send_message(
    request: Request,
    message: str = Form(...),
    db: Session = Depends(get_db)
):

    if "user" not in request.session:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    session_user = request.session["user"]

    if session_user["role"] != "student":
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    user_id = session_user["id"]
    session_id = request.session.get("active_chat")

    if not session_id:
        session_id = create_chat_session(db, user_id)

    # ---------- VERIFY SESSION OWNERSHIP ----------
    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
    ).first()

    if not session:
        return JSONResponse({"error": "Invalid session"}, status_code=400)

    # ---------- SAVE USER MESSAGE ----------
    user_message = Message(
        session_id=session_id,
        sender="student",
        message=message.strip()
    )

    db.add(user_message)
    db.commit()

    # ---------- AUTO TITLE GENERATION (FIRST MESSAGE) ----------
    if session.title == "New Chat":
        session.title = generate_title(message)
        db.commit()

    # ---------- GENERATE BOT REPLY ----------
    reply_text = get_bot_response(message, user_id, db)

    bot_message = Message(
        session_id=session_id,
        sender="bot",
        message=reply_text
    )

    db.add(bot_message)
    db.commit()

    return JSONResponse({"reply": reply_text})


# ============================================================
# RENAME CHAT SESSION
# ============================================================

@router.post("/rename-session")
def rename_session(
    request: Request,
    session_id: int = Form(...),
    new_title: str = Form(...),
    db: Session = Depends(get_db)
):

    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    user_id = request.session["user"]["id"]

    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
    ).first()

    if session:
        session.title = new_title.strip()
        db.commit()

    return RedirectResponse(request.headers.get("referer", "/dashboard"), status_code=303)


# ============================================================
# DELETE CHAT SESSION
# ============================================================

@router.post("/delete-session")
def delete_session(
    request: Request,
    session_id: int = Form(...),
    db: Session = Depends(get_db)
):

    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    user_id = request.session["user"]["id"]

    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
    ).first()

    if session:
        db.query(Message).filter(
            Message.session_id == session_id
        ).delete()

        db.delete(session)
        db.commit()

    return RedirectResponse("/dashboard", status_code=303)