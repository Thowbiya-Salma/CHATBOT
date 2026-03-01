# ============================================================
# ADMIN ROUTES - DR. URCW AI
# ============================================================

from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import (
    User,
    StudentProfile,
    AdminProfile,
    ChatSession,
    Message,
    UnansweredQuestion,
    KnowledgeBase,
    Notification
)

router = APIRouter()


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):

    # ---------- SESSION VALIDATION ----------
    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    session_user = request.session["user"]

    if session_user["role"] != "admin":
        return RedirectResponse("/", status_code=303)

    # ---------- STATS ----------
    total_students = db.query(func.count(User.id)).filter(
        User.role == "student"
    ).scalar()

    total_sessions = db.query(func.count(ChatSession.id)).scalar()

    total_messages = db.query(func.count(Message.id)).scalar()

    unanswered_count = db.query(func.count(UnansweredQuestion.id)).filter(
        UnansweredQuestion.status == "pending"
    ).scalar()

    # ---------- DEPARTMENT ANALYTICS ----------
    dept_stats = db.query(
        StudentProfile.department,
        func.count(StudentProfile.id)
    ).filter(
        StudentProfile.department.isnot(None),
        StudentProfile.department != ''
    ).group_by(StudentProfile.department).all()

    dept_labels = [d[0] if d[0] else 'Not Set' for d in dept_stats]
    dept_data = [d[1] for d in dept_stats]

    if not dept_labels:
        dept_labels = ['No Data']
        dept_data = [0]

    # ---------- KEYWORD ANALYTICS ----------
    keyword_stats = db.query(
        KnowledgeBase.keyword,
        func.count(KnowledgeBase.keyword)
    ).group_by(KnowledgeBase.keyword).order_by(
        func.count(KnowledgeBase.keyword).desc()
    ).limit(10).all()

    keyword_labels = [k[0] for k in keyword_stats] if keyword_stats else ['No Data']
    keyword_data = [k[1] for k in keyword_stats] if keyword_stats else [0]

    return request.app.templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": session_user,
            "total_students": total_students,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "unanswered_count": unanswered_count,
            "dept_labels": dept_labels,
            "dept_data": dept_data,
            "keyword_labels": keyword_labels,
            "keyword_data": keyword_data
        }
    )


# ============================================================
# STUDENT LIST PAGE
# ============================================================

@router.get("/admin/students", response_class=HTMLResponse)
def admin_students(
    request: Request,
    search: str = Query(""),
    db: Session = Depends(get_db)
):

    if "user" not in request.session or request.session["user"]["role"] != "admin":
        return RedirectResponse("/", status_code=303)

    query = db.query(User, StudentProfile).outerjoin(
        StudentProfile, User.id == StudentProfile.user_id
    ).filter(User.role == "student")

    if search:
        query = query.filter(User.name.ilike(f"%{search}%"))

    results = query.order_by(User.created_at.desc()).all()
    
    students = results

    return request.app.templates.TemplateResponse(
        "admin/students.html",
        {
            "request": request,
            "user": request.session["user"],
            "students": students,
            "search": search
        }
    )


# ============================================================
# FULL CHAT HISTORY PAGE
# ============================================================

@router.get("/admin/history", response_class=HTMLResponse)
def admin_history(
    request: Request,
    session_id: int = Query(None),
    db: Session = Depends(get_db)
):

    if "user" not in request.session or request.session["user"]["role"] != "admin":
        return RedirectResponse("/", status_code=303)

    if session_id:
        # Show messages for specific session
        messages = db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at.asc()).all()
        
        session = db.query(ChatSession, User).join(
            User, ChatSession.user_id == User.id
        ).filter(ChatSession.id == session_id).first()
        
        return request.app.templates.TemplateResponse(
            "admin/history_detail.html",
            {
                "request": request,
                "user": request.session["user"],
                "messages": messages,
                "session": session[0] if session else None,
                "student": session[1] if session else None
            }
        )
    else:
        # Show all sessions
        sessions = db.query(ChatSession, User).join(
            User, ChatSession.user_id == User.id
        ).filter(User.role == "student").order_by(
            ChatSession.updated_at.desc()
        ).all()

        return request.app.templates.TemplateResponse(
            "admin/history.html",
            {
                "request": request,
                "user": request.session["user"],
                "sessions": sessions
            }
        )


# ============================================================
# UNANSWERED QUESTIONS PAGE
# ============================================================

@router.get("/admin/unanswered", response_class=HTMLResponse)
def admin_unanswered(request: Request, db: Session = Depends(get_db)):

    if "user" not in request.session or request.session["user"]["role"] != "admin":
        return RedirectResponse("/", status_code=303)

    questions = (
        db.query(UnansweredQuestion, User)
        .join(User, UnansweredQuestion.user_id == User.id)
        .filter(UnansweredQuestion.status == "pending")
        .order_by(UnansweredQuestion.created_at.desc())
        .all()
    )

    return request.app.templates.TemplateResponse(
        "admin/unanswered.html",
        {
            "request": request,
            "user": request.session["user"],
            "questions": questions
        }
    )


# ============================================================
# ADMIN ANSWER SUBMISSION
# ============================================================

@router.post("/admin/answer/{question_id}")
def answer_question(
    request: Request,
    question_id: int,
    keyword: str = Form(...),
    answer: str = Form(...),
    db: Session = Depends(get_db)
):

    if "user" not in request.session or request.session["user"]["role"] != "admin":
        return RedirectResponse("/", status_code=303)

    question = db.query(UnansweredQuestion).filter(
        UnansweredQuestion.id == question_id
    ).first()

    if not question:
        return RedirectResponse("/admin/unanswered", status_code=303)

    # Save to Knowledge Base
    knowledge_entry = KnowledgeBase(
        keyword=keyword.lower().strip(),
        answer=answer.strip(),
        created_by=request.session["user"]["id"]
    )

    db.add(knowledge_entry)

    # Mark question as answered
    question.status = "resolved"

    # Create Notification for student
    notification = Notification(
        user_id=question.user_id,
        title="Your Question Has Been Answered",
        message=answer.strip()
    )

    db.add(notification)

    db.commit()

    return RedirectResponse("/admin/unanswered", status_code=303)