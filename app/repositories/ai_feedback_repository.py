from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.ai_feedback import AIFeedback

class AIFeedbackRepository:
    @staticmethod
    def create(db: Session, feedback: AIFeedback) -> AIFeedback:
        db.add(feedback)
        return feedback

    @staticmethod
    def get_by_answer_id(db: Session, answer_id: int) -> AIFeedback | None:
        statement = select(AIFeedback).where(AIFeedback.question_answer_id == answer_id)
        return db.execute(statement).scalar_one_or_none()