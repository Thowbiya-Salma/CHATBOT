# ============================================================
# STUDENT ROUTES - DR. URCW AI
# ============================================================

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import User, StudentProfile, AdminProfile, ChatSession, Message, Notification
import math

router = APIRouter()


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@router.get("/dashboard", response_class=HTMLResponse)
def student_dashboard(
    request: Request,
    page: int = Query(1, ge=1),
    search: str = Query(""),
    db: Session = Depends(get_db)
):

    # ---------- SESSION VALIDATION ----------
    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    session_user = request.session["user"]

    if session_user["role"] != "student":
        return RedirectResponse("/", status_code=303)

    user_id = session_user["id"]

    # ---------- PAGINATION ----------
    PER_PAGE = 100

    base_query = db.query(ChatSession).filter(
        ChatSession.user_id == user_id
    )

    if search:
        base_query = base_query.filter(
            ChatSession.title.ilike(f"%{search}%")
        )

    total_sessions = base_query.count()

    sessions = (
        base_query
        .order_by(ChatSession.updated_at.desc())
        .offset((page - 1) * PER_PAGE)
        .limit(PER_PAGE)
        .all()
    )

    # ---------- LAST MESSAGE PREVIEW (Optimized) ----------
    session_data = []

    for s in sessions:
        last_message = (
            db.query(Message)
            .filter(Message.session_id == s.id)
            .order_by(Message.created_at.desc())
            .first()
        )

        preview = (
            last_message.message[:60] + "..."
            if last_message else "No messages yet"
        )

        session_data.append({
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at,
            "preview": preview
        })

    # ---------- STATS ----------
    total_messages = db.query(func.count(Message.id)).filter(
        Message.session_id.in_(
            db.query(ChatSession.id).filter(ChatSession.user_id == user_id)
        )
    ).scalar()

    total_pages = math.ceil(total_sessions / PER_PAGE) if total_sessions else 1

    return request.app.templates.TemplateResponse(
        "student/dashboard.html",
        {
            "request": request,
            "user": session_user,
            "sessions": session_data,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "page": page,
            "total_pages": total_pages,
            "search": search
        }
    )


# ============================================================
# NOTIFICATIONS PAGE
# ============================================================

@router.get("/notifications", response_class=HTMLResponse)
def student_notifications(
    request: Request,
    db: Session = Depends(get_db)
):

    # ---------- SESSION VALIDATION ----------
    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    session_user = request.session["user"]

    if session_user["role"] != "student":
        return RedirectResponse("/", status_code=303)

    user_id = session_user["id"]

    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return request.app.templates.TemplateResponse(
        "student/notifications.html",
        {
            "request": request,
            "user": session_user,
            "notifications": notifications
        }
    )