from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext

from database import get_db
from chatbot_data import INTENTS

import re

# ---------------- NLP HELPERS ---------------- #

STOP_WORDS = {
    "the", "is", "are", "a", "an", "about", "me", "you",
    "can", "i", "tell", "please", "what", "how",
    "info", "information", "details"
}


def normalize_text(text: str) -> list[str]:
    """
    Normalize input text:
    - lowercase
    - remove punctuation
    - remove stop words
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    tokens = text.split()
    return [t for t in tokens if t not in STOP_WORDS]


def score_intent(tokens: list[str], intent: dict) -> int:
    """
    Score an intent based on keyword and phrase matches
    """
    score = 0

    for keyword in intent["keywords"]:
        keyword = keyword.lower()

        # Phrase match (higher weight)
        if " " in keyword:
            if keyword in " ".join(tokens):
                score += 5
        else:
            if keyword in tokens:
                score += 2

    return score


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="urcw-secret-key")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

pwd = CryptContext(schemes=["argon2"], deprecated="auto")


def save_message(user_id: int, sender: str, message: str):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO chat_history (user_id, sender, message) VALUES (%s,%s,%s)",
        (user_id, sender, message)
    )
    db.commit()
    cur.close()
    db.close()


def load_chat_history(user_id: int):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(
        "SELECT sender, message, created_at FROM chat_history WHERE user_id=%s ORDER BY created_at",
        (user_id,)
    )
    rows = cur.fetchall()
    cur.close()
    db.close()
    return rows


# ---------------- LOGIN PAGE ----------------
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# ---------------- LOGIN ----------------
@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    identifier: str = Form(...),
    password: str = Form(...)
):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM users WHERE username=%s OR email=%s",
        (identifier, identifier)
    )
    user = cur.fetchone()

    cur.close()
    db.close()

    # ❌ User not found
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Wrong username or password"
            }
        )

    # ❌ Password mismatch
    if not pwd.verify(password, user["password"]):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Wrong username or password"
            }
        )

    # ✅ Success
    request.session["user"] = {
        "id": user["id"],
        "name": user["name"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"]
    }

    return RedirectResponse("/dashboard", status_code=303)



# ---------------- REGISTER ----------------
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register(
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    db = get_db()
    cur = db.cursor()
    hashed = pwd.hash(password)

    cur.execute(
        "INSERT INTO users (name, username, email, password) VALUES (%s,%s,%s,%s)",
        (name, username, email, hashed)
    )
    db.commit()
    cur.close()
    db.close()

    return RedirectResponse("/", status_code=303)


# ---------------- DASHBOARD ----------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": request.session["user"]}
    )


# ---------------- PROFILE ----------------
@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": request.session["user"]}
    )


@app.post("/profile")
def update_profile(
    request: Request,
    name: str = Form(...),
    email: str = Form(...)
):
    user_id = request.session["user"]["id"]

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE users SET name=%s, email=%s WHERE id=%s",
        (name, email, user_id)
    )
    db.commit()
    cur.close()
    db.close()

    request.session["user"]["name"] = name
    request.session["user"]["email"] = email

    return RedirectResponse("/dashboard", status_code=303)


# ---------------- CHATBOT PAGE ----------------
@app.get("/chatbot", response_class=HTMLResponse)
def chatbot_page(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    user_id = request.session["user"]["id"]
    history = load_chat_history(user_id)

    return templates.TemplateResponse(
        "chatbot.html",
        {
            "request": request,
            "user": request.session["user"],
            "history": history
        }
    )


# ---------------- CHAT ----------------
@app.post("/chat")
def chat(request: Request, message: str = Form(...)):
    user_id = request.session["user"]["id"]

    # Save user message
    save_message(user_id, "user", message)

    tokens = normalize_text(message)

    best_intent = None
    best_score = 0

    for intent in INTENTS:
        score = score_intent(tokens, intent)
        if score > best_score:
            best_score = score
            best_intent = intent

    # Confidence threshold (prevents random matches)
    if best_intent and best_score >= 2:
        reply = best_intent["response"]
    else:
        reply = (
        "Sorry 😔 I couldn’t understand that.<br><br>"
        "You can ask about Admissions, Courses, Placements, Hostel, Library, Contact."
    )

    save_message(user_id, "bot", reply)
    return JSONResponse({"reply": reply})



# ---------------- LOGOUT ----------------
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
