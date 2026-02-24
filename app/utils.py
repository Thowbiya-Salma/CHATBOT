from app.models import ChatSession

def create_chat_session(db, user_id, user_type):
    session = ChatSession(
        user_id=user_id,
        user_type=user_type
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session.id
