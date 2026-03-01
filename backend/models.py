# ============================================================
# DATABASE MODELS - DR. URCW AI
# ============================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Enum,
    ForeignKey,
    DateTime,
    func
)
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


# ============================================================
# ROLE ENUM
# ============================================================

class UserRole(str, enum.Enum):
    admin = "admin"
    student = "student"


# ============================================================
# USERS TABLE
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    student_profile = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete"
    )

    admin_profile = relationship(
        "AdminProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete"
    )

    chat_sessions = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete"
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete"
    )


# ============================================================
# PROFILES TABLE
# ============================================================

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    full_name = Column(String(150))
    phone = Column(String(20))
    department = Column(String(150))
    student_id = Column(String(50))
    profile_image = Column(String(255))

    user = relationship("User", back_populates="student_profile")


class AdminProfile(Base):
    __tablename__ = "admin_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    full_name = Column(String(150))
    phone = Column(String(20))
    department = Column(String(150))
    profile_image = Column(String(255))

    user = relationship("User", back_populates="admin_profile")


# ============================================================
# CHAT SESSIONS TABLE
# ============================================================

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), default="New Chat")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete"
    )


# ============================================================
# MESSAGES TABLE
# ============================================================

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)

    sender = Column(String(20))  # 'student' or 'bot'
    message = Column(Text, nullable=False)
    is_answered = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


# ============================================================
# UNANSWERED QUESTIONS TABLE
# ============================================================

class UnansweredQuestion(Base):
    __tablename__ = "unanswered_questions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)

    question = Column(Text, nullable=False)
    status = Column(String(20), default="pending")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================
# KNOWLEDGE BASE TABLE
# ============================================================

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True)
    keyword = Column(String(255), nullable=False)
    answer = Column(Text, nullable=False)

    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================
# NOTIFICATIONS TABLE
# ============================================================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(255))
    message = Column(Text)
    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")


# ============================================================
# INTENT STATS TABLE (Analytics)
# ============================================================

class IntentStat(Base):
    __tablename__ = "intent_stats"

    id = Column(Integer, primary_key=True)
    keyword = Column(String(255))
    match_score = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())