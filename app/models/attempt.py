import enum
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, JSON, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.ai_feedback import AIFeedback
from app.models.base import Base


class AttemptStatus(str, enum.Enum):
    in_progress = "in_progress"
    submitted = "submitted"
    graded = "graded"


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    __table_args__ = (
        UniqueConstraint("assessment_id", "student_id", "attempt_number", name="uq_attempt_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), nullable=False, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    status: Mapped[AttemptStatus] = mapped_column(String(50), nullable=False, default=AttemptStatus.in_progress)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    score: Mapped[float | None] = mapped_column(Float, nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    graded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    assessment = relationship("Assessment")
    student = relationship("User")
    answers: Mapped[list["QuestionAnswer"]] = relationship(
        back_populates="attempt", cascade="all, delete-orphan"
    )


class QuestionAnswer(Base):
    __tablename__ = "question_answers"

    __table_args__ = (
        UniqueConstraint("attempt_id", "assessment_question_id", name="uq_attempt_answer"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    attempt_id: Mapped[int] = mapped_column(ForeignKey("assessment_attempts.id"), nullable=False, index=True)
    assessment_question_id: Mapped[int] = mapped_column(ForeignKey("assessment_questions.id"), nullable=False)

    # answer_json permite guardar "A", ["A", "C"], 3.14, true, etc.
    answer_json: Mapped[dict | list | str | int | float | bool] = mapped_column(JSON, nullable=False)
    
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    attempt: Mapped["AssessmentAttempt"] = relationship(back_populates="answers")
    assessment_question = relationship("AssessmentQuestion")

    ai_feedback: Mapped["AIFeedback"] = relationship(
        "AIFeedback", 
        back_populates="answer", 
        uselist=False, 
        cascade="all, delete-orphan"
    )