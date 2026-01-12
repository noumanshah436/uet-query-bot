import uuid
from datetime import UTC, datetime
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
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
        nullable=False,
    )
