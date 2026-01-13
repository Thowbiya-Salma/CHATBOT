from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware


from database import get_db
from chatbot_data import CHATBOT_DATA

app = FastAPI(debug=True)

app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-urcw-key"
)


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

pwd = CryptContext(schemes=["argon2"], deprecated="auto")

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    # 🔐 sanitize password for bcrypt
    password = password.strip()

    if len(password.encode("utf-8")) > 72:
        password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")

    hashed_password = pwd.hash(password)

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
        (name, email, hashed_password)
    )
    db.commit()
    cur.close()
    db.close()

    return RedirectResponse("/", status_code=302)


@app.post("/login")
def login(
    request: Request,
    identifier: str = Form(...),  # username OR email
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

    # ❌ No user found
    if not user:
        return RedirectResponse("/", status_code=303)

    # 🔐 Password check (argon2-safe)
    try:
        if not pwd.verify(password, user["password"]):
            return RedirectResponse("/", status_code=303)
    except Exception:
        return RedirectResponse("/", status_code=303)

    # ✅ Store user in session
    request.session["user"] = {
        "name": user["name"],
        "username": user["username"],
        "email": user["email"]
    }

    return RedirectResponse("/dashboard", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
def chat(message: str = Form(...)):
    return {"reply": CHATBOT_DATA.get(message.lower(), "Invalid option")}
