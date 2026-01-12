import json
from pydantic import BaseModel
from typing import Any, List, Optional
from datetime import datetime
from uuid import UUID


class ChatHistoryCreate(BaseModel):
    question: str
    answer: str
    source_chunks: Optional[Any] = None


class ChatHistoryResponse(BaseModel):
    id: str
    question: str
    answer: str
    source_chunks: Optional[List[str]]
    created_at: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            question=obj.question,
            answer=obj.answer,
            source_chunks=json.loads(obj.source_chunks) if obj.source_chunks else None,
            created_at=obj.created_at,
        )

    class Config:
        from_attributes = True
