from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.config import get_db
from src.repository.chat_history import get_all_chat_history
from src.schemas.chat_history import ChatHistoryResponse, ChatHistoryWrapperResponse

router = APIRouter()


@router.get("/")
def get_chat_history(db: Session = Depends(get_db)):
    """
    Get all chat history (latest first)
    """
    records = get_all_chat_history(db)

    return ChatHistoryWrapperResponse(
        success=True,
        history=[ChatHistoryResponse.from_orm(r) for r in records],
    )
