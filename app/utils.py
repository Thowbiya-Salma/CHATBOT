from app.models import ChatSession

def create_chat_session(db, user_id: int) -> int:
    """
    Create a new chat session for a user.
    """
    session = ChatSession(user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session.id
