from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.attempt import AssessmentAttempt, AttemptStatus
from app.models.question import QuestionType
from app.services.ai_feedback_service import AIFeedbackService


class GradingService:
    @staticmethod
    def grade_attempt(db: Session, attempt: AssessmentAttempt):
        total_score = 0.0

        for answer in attempt.answers:
            aq = answer.assessment_question
            question = aq.question
            points_available = aq.points

            if question.question_type in [QuestionType.single_choice, QuestionType.boolean]:
                correct_option = next((opt for opt in question.options if opt.is_correct), None)
                
                if correct_option and str(correct_option.value).lower() == str(answer.answer_json).lower():
                    answer.score = points_available
                else:
                    answer.score = 0.0

            elif question.question_type == QuestionType.open_text:
                AIFeedbackService.generate_feedback_for_answer(db, answer)
                answer.score = None

            if answer.score is not None:
                total_score += answer.score

        attempt.score = total_score
        attempt.status = AttemptStatus.graded
        attempt.graded_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(attempt)