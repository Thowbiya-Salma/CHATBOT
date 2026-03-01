# ============================================================
# UTILITY FUNCTIONS - DR. URCW AI
# ============================================================

from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.models import ChatSession, User
from datetime import datetime


# ============================================================
# CREATE NEW CHAT SESSION
# ============================================================

def create_chat_session(db: Session, user_id: int) -> int:
    """
    Creates a new chat session for a student.
    Returns the created session ID.
    """

    new_session = ChatSession(
        user_id=user_id,
        title="New Chat"
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session.id


# ============================================================
# VERIFY SESSION OWNERSHIP
# ============================================================

def verify_chat_session_ownership(db: Session, session_id: int, user_id: int) -> bool:
    """
    Ensures the chat session belongs to the logged-in user.
    Prevents unauthorized access.
    """

    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
    ).first()

    return session is not None


# ============================================================
# UPDATE SESSION TIMESTAMP
# ============================================================

def update_session_timestamp(db: Session, session_id: int):
    """
    Updates the session's updated_at field.
    Ensures proper recent ordering.
    """

    session = db.query(ChatSession).filter(
        ChatSession.id == session_id
    ).first()

    if session:
        session.updated_at = datetime.utcnow()
        db.commit()


# ============================================================
# ROLE VALIDATION HELPER
# ============================================================

def validate_user_role(session_data: dict, required_role: str) -> bool:
    """
    Ensures the logged-in user has the required role.
    """

    if not session_data:
        return False

    return session_data.get("role") == required_role


# ============================================================
# SAFE REDIRECT PATH
# ============================================================

def safe_redirect_path(referer: str, fallback: str) -> str:
    """
    Prevents redirecting to external malicious URLs.
    """

    if not referer:
        return fallback

    if referer.startswith("/"):
        return referer

    return fallback