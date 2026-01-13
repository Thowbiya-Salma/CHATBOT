from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext

from database import get_db
from chatbot_data import CHATBOT_DATA

app = FastAPI(debug=True)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


pwd = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

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

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
def chat(message: str = Form(...)):
    return {"reply": CHATBOT_DATA.get(message.lower(), "Invalid option")}
