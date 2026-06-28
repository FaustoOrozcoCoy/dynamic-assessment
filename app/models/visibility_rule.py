import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class VisibilityOperator(str, enum.Enum):
    equals = "equals"
    not_equals = "not_equals"
    contains = "contains"
    greater_than = "greater_than"
    less_than = "less_than"


class VisibilityRule(Base):
    __tablename__ = "visibility_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    assessment_question_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_questions.id"), nullable=False, unique=True
    )
    
    depends_on_assessment_question_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_questions.id"), nullable=False
    )

    operator: Mapped[VisibilityOperator] = mapped_column(String(50), nullable=False)
    
    expected_value_json: Mapped[dict | list | str | int | float | bool] = mapped_column(
        JSON, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relación hacia la pregunta que es afectada por esta regla
    target_question: Mapped["AssessmentQuestion"] = relationship(
        "AssessmentQuestion",
        foreign_keys=[assessment_question_id],
        back_populates="visibility_rule",
    )