from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.schemas.chat_history import ChatHistoryCreate
from src.database.models import ChatHistory


def get_all_chat_history(db: Session) -> list[ChatHistory]:
    return db.query(ChatHistory).order_by(ChatHistory.created_at.desc()).all()


def create_chat_history(request: ChatHistoryCreate, db: Session):
    history = ChatHistory(
        question=request.question,
        answer=request.answer,
        source_chunks=request.source_chunks,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history
