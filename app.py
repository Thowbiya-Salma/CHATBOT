from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

from database import get_db
from chatbot_data import CHATBOT_DATA

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

from passlib.context import CryptContext

pwd = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


# ---------- LOGIN PAGE ----------
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# ---------- REGISTER PAGE ----------
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# ---------- REGISTER ----------
@app.post("/register")
def register(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
        (name, email, pwd.hash(password))
    )
    db.commit()
    cur.close()
    db.close()
    return RedirectResponse("/", status_code=302)

# ---------- LOGIN ----------
@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()
    db.close()

    if user and pwd.verify(password, user[3]):
        return RedirectResponse("/dashboard", status_code=302)

    return RedirectResponse("/", status_code=302)

# ---------- DASHBOARD ----------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ---------- CHAT ----------
@app.post("/chat")
def chat(message: str = Form(...)):
    key = message.lower().strip()
    reply = CHATBOT_DATA.get(key, "Invalid option. Try 1, 1.1, etc.")
    return {"reply": reply}
