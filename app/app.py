from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.database import Base, engine, get_db
from app.models import User, ChatSession, ChatMessage, UnansweredQuestion, IntentStat
from app.auth import hash_password, verify_password
from app.chat import generate_reply, generate_title
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
def login(request: Request,
          identifier: str = Form(...),
          password: str = Form(...),
          db: Session = Depends(get_db)):

    user = db.query(User).filter(
        or_(User.username == identifier, User.email == identifier)
    ).first()

    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password"}
        )

    request.session["user"] = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }

    return RedirectResponse("/dashboard", status_code=303)


# ================= REGISTER =================

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register(request: Request,
             name: str = Form(...),
             username: str = Form(...),
             email: str = Form(...),
             password: str = Form(...),
             db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        or_(User.username == username, User.email == email)
    ).first()

    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Username or Email already exists"}
        )

    new_user = User(
        name=name,
        username=username,
        email=email,
        password=hash_password(password)
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse("/", status_code=303)


# ================= DASHBOARD =================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):

    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    user_id = request.session["user"]["id"]

    sessions = db.query(ChatSession)\
                 .filter(ChatSession.user_id == user_id)\
                 .order_by(ChatSession.created_at.desc())\
                 .all()

    total_sessions = len(sessions)

    total_messages = db.query(ChatMessage)\
                        .filter(ChatMessage.user_id == user_id)\
                        .count()

    unanswered_count = db.query(UnansweredQuestion).count()

    popular_intents = db.query(IntentStat)\
                        .order_by(IntentStat.count.desc())\
                        .limit(5)\
                        .all()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": request.session["user"],
            "sessions": sessions,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "unanswered_count": unanswered_count,
            "popular_intents": popular_intents
        }
    )

# ================= CHAT =================

@app.get("/chatbot", response_class=HTMLResponse)
def chatbot_page(request: Request,
                 session_id: int | None = None,
                 db: Session = Depends(get_db)):

    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    user_id = request.session["user"]["id"]

    if session_id is None:
        session_id = create_chat_session(db, user_id)

    session = db.query(ChatSession)\
                .filter(ChatSession.id == session_id,
                        ChatSession.user_id == user_id)\
                .first()

    if not session:
        return RedirectResponse("/dashboard", status_code=303)

    sessions = db.query(ChatSession)\
                 .filter(ChatSession.user_id == user_id)\
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

    if "user" not in request.session:
        return JSONResponse({"reply": "Session expired. Please login again."})

    user_id = request.session["user"]["id"]
    session_id = request.session.get("active_chat")

    if not session_id:
        session_id = create_chat_session(db, user_id)

    user_msg = ChatMessage(
        user_id=user_id,
        session_id=session_id,
        sender="user",
        message=message
    )
    db.add(user_msg)
    db.commit()

    history = db.query(ChatMessage)\
                .filter(ChatMessage.session_id == session_id)\
                .order_by(ChatMessage.created_at.asc())\
                .all()

    reply = generate_reply(history)

    bot_msg = ChatMessage(
        user_id=user_id,
        session_id=session_id,
        sender="bot",
        message=reply
    )
    db.add(bot_msg)
    db.commit()

    if len(history) == 1:
        title = generate_title(message)
        session = db.query(ChatSession)\
                    .filter(ChatSession.id == session_id)\
                    .first()
        if session:
            session.title = title
            db.commit()

    return JSONResponse({"reply": reply})


# ================= RENAME =================

@app.post("/rename_chat/{session_id}")
def rename_chat(session_id: int,
                title: str = Form(...),
                request: Request = None,
                db: Session = Depends(get_db)):

    user_id = request.session["user"]["id"]

    session = db.query(ChatSession)\
                .filter(ChatSession.id == session_id,
                        ChatSession.user_id == user_id)\
                .first()

    if session:
        session.title = title
        db.commit()

    return RedirectResponse(f"/chatbot?session_id={session_id}", status_code=303)


# ================= DELETE =================

@app.get("/delete_chat/{session_id}")
def delete_chat(session_id: int,
                request: Request,
                db: Session = Depends(get_db)):

    user_id = request.session["user"]["id"]

    db.query(ChatMessage)\
      .filter(ChatMessage.session_id == session_id)\
      .delete()

    db.query(ChatSession)\
      .filter(ChatSession.id == session_id,
              ChatSession.user_id == user_id)\
      .delete()

    db.commit()

    return RedirectResponse("/dashboard", status_code=303)


# ================= ADMIN =================

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, db: Session = Depends(get_db)):

    if "user" not in request.session or request.session["user"]["role"] != "admin":
        return RedirectResponse("/dashboard", status_code=303)

    unanswered = db.query(UnansweredQuestion)\
                   .order_by(UnansweredQuestion.created_at.desc())\
                   .all()

    popular_intents = db.query(IntentStat)\
                        .order_by(IntentStat.count.desc())\
                        .all()

    total_users = db.query(User).count()
    total_sessions = db.query(ChatSession).count()
    total_messages = db.query(ChatMessage).count()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "unanswered": unanswered,
            "popular_intents": popular_intents,
            "total_users": total_users,
            "total_sessions": total_sessions,
            "total_messages": total_messages
        }
    )

# ================= LOGOUT =================

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
