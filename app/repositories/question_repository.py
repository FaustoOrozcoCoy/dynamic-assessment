from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Question, QuestionOption

class QuestionRepository:
    @staticmethod
    def create(db: Session, question: Question) -> Question:
        db.add(question)
        return question

    @staticmethod
    def get_by_id(db: Session, question_id: int) -> Question | None:
        return db.get(Question, question_id)

    @staticmethod
    def list_all_active(db: Session) -> list[Question]:
        statement = select(Question).where(Question.is_active.is_(True)).order_by(Question.id)
        return list(db.execute(statement).scalars().all())

    @staticmethod
    def add_option(db: Session, option: QuestionOption) -> QuestionOption:
        db.add(option)
        return option

    @staticmethod
    def get_option_by_id(db: Session, option_id: int) -> QuestionOption | None:
        return db.get(QuestionOption, option_id)