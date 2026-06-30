import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AIFeedbackStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class AIFeedback(Base):
    __tablename__ = "ai_feedback"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    question_answer_id: Mapped[int] = mapped_column(
        ForeignKey("question_answers.id"), nullable=False, unique=True, index=True
    )

    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column("model", String(100), nullable=False)
    
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[AIFeedbackStatus] = mapped_column(String(50), nullable=False, default=AIFeedbackStatus.pending)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    answer = relationship("QuestionAnswer", back_populates="ai_feedback")