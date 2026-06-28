import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.visibility_rule import VisibilityRule


class AssessmentType(str, enum.Enum):
    quiz = "quiz"
    workshop = "workshop"
    exam = "exam"
    form = "form"


class AssessmentStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False, index=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    assessment_type: Mapped[AssessmentType] = mapped_column("type", String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    status: Mapped[AssessmentStatus] = mapped_column(
        String(50), nullable=False, default=AssessmentStatus.draft
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    course = relationship("Course", back_populates="assessments")
    creator = relationship("User")
    assessment_questions: Mapped[list["AssessmentQuestion"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"
    
    __table_args__ = (
        UniqueConstraint("assessment_id", "question_id", name="uq_assessment_question"),
        UniqueConstraint("assessment_id", "order_index", name="uq_assessment_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False, index=True)

    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    assessment: Mapped["Assessment"] = relationship(back_populates="assessment_questions")
    question = relationship("Question")

    visibility_rule: Mapped["VisibilityRule"] = relationship(
        "VisibilityRule",
        foreign_keys="[VisibilityRule.assessment_question_id]",
        back_populates="target_question",
        cascade="all, delete-orphan",
        uselist=False
    )