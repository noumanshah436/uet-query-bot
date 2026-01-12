import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime
from src.database.config import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))

    question = Column(Text, nullable=False)

    answer = Column(Text, nullable=False)

    source_chunks = Column(Text, nullable=True)  # store JSON as string

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
