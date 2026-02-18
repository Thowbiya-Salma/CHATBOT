from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# ================= USER =================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    username = Column(String(100), unique=True)
    email = Column(String(100), unique=True)
    password = Column(String(255))
    role = Column(String(50), default="user")

    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete")


# ================= CHAT SESSION =================

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), default="New Chat")
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete")


# ================= CHAT MESSAGE =================

class ChatMessage(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    sender = Column(String(20))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


# ================= UNANSWERED QUESTIONS =================

class UnansweredQuestion(Base):
    __tablename__ = "unanswered_questions"

    id = Column(Integer, primary_key=True)
    question = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ================= INTENT STATS =================

class IntentStat(Base):
    __tablename__ = "intent_stats"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    count = Column(Integer, default=0)
