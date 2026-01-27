from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext

from database import get_db
from chatbot_data import INTENTS


# ---------------- APP INIT ----------------
app = FastAPI()

# ---------------- SESSION ----------------
app.add_middleware(
    SessionMiddleware,
    secret_key="urcw-secret-key"
)

# ---------------- STATIC & TEMPLATES ----------------
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------------- PASSWORD HASHING ----------------
pwd = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# ---------------- LOGIN PAGE ----------------
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# ---------------- LOGIN ----------------
@app.post("/login")
def login(
    request: Request,
    identifier: str = Form(...),   # username OR email
    password: str = Form(...)
):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM users WHERE email=%s OR username=%s",
        (identifier, identifier)
    )
    user = cur.fetchone()

    cur.close()
    db.close()

    if not user:
        return RedirectResponse("/", status_code=303)

    try:
        if not pwd.verify(password, user["password"]):
            return RedirectResponse("/", status_code=303)
    except Exception:
        return RedirectResponse("/", status_code=303)

    request.session["user"] = {
        "name": user["name"],
        "username": user["username"],
        "email": user["email"]
    }

    return RedirectResponse("/dashboard", status_code=303)


# ---------------- REGISTER PAGE ----------------
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# ---------------- REGISTER ----------------
@app.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    db = get_db()
    cur = db.cursor()

    hashed_password = pwd.hash(password)

    try:
        cur.execute(
            """
            INSERT INTO users (name, username, email, password)
            VALUES (%s, %s, %s, %s)
            """,
            (name, username, email, hashed_password)
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        cur.close()
        db.close()

    return RedirectResponse("/", status_code=303)


# ---------------- DASHBOARD ----------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": request.session["user"]
        }
    )


# ---------------- CHAT (NLP MODE) ----------------
@app.post("/chat")
def chat(message: str = Form(...)):
    msg = message.lower().strip()

    for intent in INTENTS:
        for keyword in intent["keywords"]:
            if keyword in msg:
                return JSONResponse({"reply": intent["response"]})

    return JSONResponse({
        "reply": (
            "Sorry 😔 I couldn’t understand that.<br><br>"
            "You can ask about:<br>"
            "• Admissions<br>"
            "• Courses<br>"
            "• Placements<br>"
            "• Hostel<br>"
            "• Library<br>"
            "• Contact details"
        )
    })



# ---------------- LOGOUT ----------------
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
