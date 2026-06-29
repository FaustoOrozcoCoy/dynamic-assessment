from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.attempt import AssessmentAttempt, AttemptStatus, QuestionAnswer

class AttemptRepository:
    
    @staticmethod
    def get_by_id(db: Session, attempt_id: int) -> AssessmentAttempt | None:
        return db.get(AssessmentAttempt, attempt_id)

    @staticmethod
    def get_in_progress_attempt(db: Session, assessment_id: int, student_id: int) -> AssessmentAttempt | None:
        statement = (
            select(AssessmentAttempt)
            .where(AssessmentAttempt.assessment_id == assessment_id)
            .where(AssessmentAttempt.student_id == student_id)
            .where(AssessmentAttempt.status == AttemptStatus.in_progress)
        )
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_max_attempt_number(db: Session, assessment_id: int, student_id: int) -> int:
        statement = (
            select(func.max(AssessmentAttempt.attempt_number))
            .where(AssessmentAttempt.assessment_id == assessment_id)
            .where(AssessmentAttempt.student_id == student_id)
        )
        result = db.execute(statement).scalar()
        return result if result is not None else 0

    @staticmethod
    def create_attempt(db: Session, attempt: AssessmentAttempt) -> AssessmentAttempt:
        db.add(attempt)
        return attempt

    @staticmethod
    def get_answer(db: Session, attempt_id: int, assessment_question_id: int) -> QuestionAnswer | None:
        statement = (
            select(QuestionAnswer)
            .where(QuestionAnswer.attempt_id == attempt_id)
            .where(QuestionAnswer.assessment_question_id == assessment_question_id)
        )
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def save_answer(db: Session, answer: QuestionAnswer) -> QuestionAnswer:
        db.add(answer)
        return answer