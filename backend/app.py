# ============================================================
# DR. URCW AI - MAIN APPLICATION ENTRY
# ============================================================

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# ===============================
# LOAD ENVIRONMENT VARIABLES
# ===============================

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "DR_URCW_AI")
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "True") == "True"

SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "urcw_session")
SESSION_MAX_AGE = int(os.getenv("SESSION_MAX_AGE", 3600))

# ===============================
# INITIALIZE FASTAPI
# ===============================

app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    debug=DEBUG
)

# ===============================
# SESSION MIDDLEWARE
# ===============================

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie=SESSION_COOKIE_NAME,
    max_age=SESSION_MAX_AGE,
    https_only=False if APP_ENV == "development" else True,
    same_site="lax"
)

# ===============================
# STATIC FILES CONFIGURATION
# ===============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(PROJECT_ROOT, "frontend", "static")),
    name="static"
)

# ===============================
# JINJA TEMPLATE CONFIGURATION
# ===============================

templates = Jinja2Templates(
    directory=os.path.join(PROJECT_ROOT, "frontend", "templates")
)
# Attach templates object to app (so routes can use it)
app.templates = templates

# ===============================
# DATABASE INITIALIZATION
# ===============================

from backend.database import Base, engine

# Comment out auto table creation - use bot.sql instead
# Base.metadata.create_all(bind=engine)

# ===============================
# IMPORT ROUTERS
# ===============================

from backend.routes.auth_routes import router as auth_router
from backend.routes.student_routes import router as student_router
from backend.routes.admin_routes import router as admin_router
from backend.routes.chat_routes import router as chat_router
from backend.routes.profile_routes import router as profile_router

# ===============================
# INCLUDE ROUTERS
# ===============================

app.include_router(auth_router)
app.include_router(student_router)
app.include_router(admin_router)
app.include_router(chat_router)
app.include_router(profile_router)

# ===============================
# GLOBAL HEALTH CHECK
# ===============================

@app.get("/health")
def health_check():
    return {
        "status": "running",
        "app": APP_NAME,
        "environment": APP_ENV
    }

# ===============================
# STARTUP EVENT
# ===============================

@app.on_event("startup")
def startup_event():
    print(f"🚀 {APP_NAME} started in {APP_ENV} mode")

# ===============================
# SHUTDOWN EVENT
# ===============================

@app.on_event("shutdown")
def shutdown_event():
    print("🛑 Application shutdown")