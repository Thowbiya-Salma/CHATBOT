from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# ================= ADMIN =================

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    username = Column(String(100), unique=True)
    email = Column(String(100), unique=True)
    password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)


# ================= STUDENT =================

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    username = Column(String(100), unique=True)
    email = Column(String(100), unique=True)
    password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)


# ================= CHAT SESSION =================

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)
    user_type = Column(String(20))  # 'student'
    user_id = Column(Integer)
    title = Column(String(255), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)


# ================= CHAT MESSAGE =================

class ChatMessage(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    user_type = Column(String(20))  # 'student'
    user_id = Column(Integer)
    session_id = Column(Integer)
    sender = Column(String(20))  # 'user' or 'bot'
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ================= UNANSWERED QUESTIONS =================

class UnansweredQuestion(Base):
    __tablename__ = "unanswered_questions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    question = Column(Text)
    keyword = Column(String(255), nullable=True)   # NEW
    admin_answer = Column(Text, nullable=True)
    answered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student")

# ================= INTENT STATISTICS =================

class IntentStat(Base):
    __tablename__ = "intent_stats"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    count = Column(Integer, default=0)
