# ============================================================
# DATABASE CONFIGURATION - DR. URCW AI
# ============================================================

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# ===============================
# LOAD ENV VARIABLES
# ===============================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables.")

# ===============================
# SQLALCHEMY ENGINE
# ===============================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,          # Prevents stale connections
    pool_recycle=3600,           # Recycle connections every hour
    pool_size=10,                # Production-safe pool size
    max_overflow=20,             # Extra burst capacity
    future=True
)

# ===============================
# SESSION LOCAL
# ===============================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ===============================
# BASE DECLARATIVE CLASS
# ===============================

Base = declarative_base()

# ===============================
# DEPENDENCY (FOR ROUTES)
# ===============================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()