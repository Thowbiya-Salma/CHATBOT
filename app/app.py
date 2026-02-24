from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import Base, engine, get_db
from app.models import (
    Admin,
    Student,
    ChatSession,
    ChatMessage,
    UnansweredQuestion,
    IntentStat
)
from app.auth import hash_password, verify_password
from app.chat import generate_reply
from app.config import SECRET_KEY
from app.utils import create_chat_session

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# ================= LOGIN =================

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(
    request: Request,
    role: str = Form(...),
    identifier: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    if role == "admin":
        user = db.query(Admin).filter(
            or_(Admin.username == identifier, Admin.email == identifier)
        ).first()
    else:
        user = db.query(Student).filter(
            or_(Student.username == identifier, Student.email == identifier)
        ).first()

    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"}
        )

    request.session["user"] = {
        "id": user.id,
        "name": user.name,
        "role": role
    }

    return RedirectResponse(
        "/admin" if role == "admin" else "/dashboard",
        status_code=303
    )


# ================= REGISTER =================

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):

    model = Admin if role == "admin" else Student

    existing = db.query(model).filter(
        or_(model.username == username, model.email == email)
    ).first()

    if existing:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Username or Email already exists"}
        )

    new_user = model(
        name=name,
        username=username,
        email=email,
        password=hash_password(password)
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse("/", status_code=303)


# ================= STUDENT DASHBOARD =================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    page: int = 1,
    search: str = "",
    db: Session = Depends(get_db)
):

    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    if request.session["user"]["role"] != "student":
        return RedirectResponse("/", status_code=303)

    user_data = request.session["user"]
    user_id = user_data["id"]

    PER_PAGE = 5

    # -------- BASE QUERY --------
    query = db.query(ChatSession).filter(
        ChatSession.user_id == user_id,
        ChatSession.user_type == "student"
    )

    # -------- SEARCH FILTER --------
    if search:
        query = query.filter(ChatSession.title.ilike(f"%{search}%"))

    total_sessions = query.count()

    sessions = (
        query
        .order_by(ChatSession.created_at.desc())
        .offset((page - 1) * PER_PAGE)
        .limit(PER_PAGE)
        .all()
    )

    # -------- ATTACH LAST MESSAGE PREVIEW --------
    session_data = []

    for s in sessions:
        last_message = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == s.id)
            .order_by(ChatMessage.created_at.desc())
            .first()
        )

        session_data.append({
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at,
            "last_message": last_message.message[:60] + "..." if last_message else "No messages yet"
        })

    total_messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.user_id == user_id,
            ChatMessage.user_type == "student"
        )
        .count()
    )

    total_pages = (total_sessions + PER_PAGE - 1) // PER_PAGE

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user_data,
            "sessions": session_data,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "page": page,
            "total_pages": total_pages,
            "search": search
        }
    )

# ================= CHATBOT =================

@app.get("/chatbot", response_class=HTMLResponse)
def chatbot_page(request: Request,
                 session_id: int | None = None,
                 db: Session = Depends(get_db)):

    if "user" not in request.session or request.session["user"]["role"] != "student":
        return RedirectResponse("/", status_code=303)

    user_id = request.session["user"]["id"]

    if session_id is None:
        session_id = create_chat_session(db, user_id, "student")

    sessions = db.query(ChatSession)\
        .filter(ChatSession.user_id == user_id,
                ChatSession.user_type == "student")\
        .order_by(ChatSession.created_at.desc())\
        .all()

    messages = db.query(ChatMessage)\
        .filter(ChatMessage.session_id == session_id)\
        .order_by(ChatMessage.created_at.asc())\
        .all()

    request.session["active_chat"] = session_id

    return templates.TemplateResponse(
        "chatbot.html",
        {
            "request": request,
            "user": request.session["user"],
            "sessions": sessions,
            "messages": messages,
            "active_session": session_id
        }
    )


@app.post("/chat")
def chat(request: Request,
         message: str = Form(...),
         db: Session = Depends(get_db)):

    if "user" not in request.session or request.session["user"]["role"] != "student":
        return JSONResponse({"reply": "Unauthorized access."})

    user_id = request.session["user"]["id"]
    session_id = request.session.get("active_chat")

    if not session_id:
        session_id = create_chat_session(db, user_id, "student")

    # -------- SAVE USER MESSAGE --------
    db.add(ChatMessage(
        user_type="student",
        user_id=user_id,
        session_id=session_id,
        sender="user",
        message=message
    ))
    db.commit()

    # -------- CHECK TRAINED KEYWORDS FIRST --------
    cleaned_message = message.lower().strip()

    trained_match = db.query(UnansweredQuestion).filter(
        UnansweredQuestion.keyword == cleaned_message,
        UnansweredQuestion.answered == True
    ).first()

    if trained_match:
        reply = trained_match.admin_answer
    else:
        history = db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.created_at.asc())\
            .all()

        reply = generate_reply(history, db, user_id)

    # -------- SAVE BOT REPLY --------
    db.add(ChatMessage(
        user_type="student",
        user_id=user_id,
        session_id=session_id,
        sender="bot",
        message=reply
    ))
    db.commit()

    return JSONResponse({"reply": reply})


# ================= RENAME SESSION =================

@app.post("/rename-session")
def rename_session(request: Request,
                   session_id: int = Form(...),
                   new_title: str = Form(...),
                   db: Session = Depends(get_db)):

    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == request.session["user"]["id"],
        ChatSession.user_type == "student"
    ).first()

    if session:
        session.title = new_title.strip()
        db.commit()

    return RedirectResponse(request.headers.get("referer", "/dashboard"), status_code=303)


# ================= DELETE SESSION =================

@app.post("/delete-session")
def delete_session(request: Request,
                   session_id: int = Form(...),
                   db: Session = Depends(get_db)):

    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    db.query(ChatMessage)\
        .filter(ChatMessage.session_id == session_id)\
        .delete()

    db.query(ChatSession)\
        .filter(ChatSession.id == session_id)\
        .delete()

    db.commit()

    return RedirectResponse("/dashboard", status_code=303)


# ================= ADMIN DASHBOARD =================

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):

    if "user" not in request.session or request.session["user"]["role"] != "admin":
        return RedirectResponse("/", status_code=303)

    total_students = db.query(Student).count()
    total_sessions = db.query(ChatSession).count()
    total_messages = db.query(ChatMessage).count()
    unanswered_count = db.query(UnansweredQuestion).filter_by(answered=False).count()

    # ✅ Correct join using user_id + user_type
    search_history = (
        db.query(ChatMessage, Student)
        .join(Student, ChatMessage.user_id == Student.id)
        .filter(ChatMessage.user_type == "student")
        .order_by(ChatMessage.created_at.desc())
        .all()
    )

    unanswered = (
        db.query(UnansweredQuestion)
        .filter_by(answered=False)
        .order_by(UnansweredQuestion.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "total_students": total_students,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "unanswered_count": unanswered_count,
            "search_history": search_history,
            "unanswered": unanswered
        }
    )

# ================= ADMIN ANSWER =================

@app.post("/admin/answer/{qid}")
def answer_unanswered(
    qid: int,
    keyword: str = Form(...),
    answer: str = Form(...),
    db: Session = Depends(get_db)
):
    question = db.query(UnansweredQuestion).filter_by(id=qid).first()

    if question:
        question.keyword = keyword.lower().strip()
        question.admin_answer = answer
        question.answered = True
        db.commit()

    return RedirectResponse("/admin", status_code=303)


# ================= LOGOUT =================

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
