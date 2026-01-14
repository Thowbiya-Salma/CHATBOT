from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware


from database import get_db
from chatbot_data import CHATBOT_DATA, WEBSITE1

app = FastAPI(debug=True)

app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-urcw-key"
)


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

pwd = CryptContext(schemes=["argon2"], deprecated="auto")

def get_bot_response(message: str):
    message = message.lower().strip()

    for keyword, response in CHATBOT_DATA.items():
        if keyword in message:
            return response

    return WEBSITE1

@app.post("/chat")
def chat(message: str = Form(...)):
    reply = get_bot_response(message)
    return {"reply": reply}


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

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

    cur.execute(
        "INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)",
        (name, username, email, hashed_password)
    )

    db.commit()
    cur.close()
    db.close()

    return RedirectResponse("/", status_code=303)



@app.post("/login")
def login(
    request: Request,
    identifier: str = Form(...),
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

    if not pwd.verify(password, user["password"]):
        return RedirectResponse("/", status_code=303)

    # ✅ SAVE SESSION FIRST
    request.session["user"] = {
        "id": user["id"],
        "name": user["name"],
        "username": user["username"],
        "email": user["email"]
    }

    # ✅ THEN redirect to dashboard
    return RedirectResponse("/dashboard", status_code=303)



@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = request.session.get("user")

    if not user:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user
        }
    )




@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

