from sqlalchemy.orm import Session

from app.core.config import settings
from app.integrations.llm_client import LLMClient, LLMClientError
from app.models import QuestionAnswer
from app.models.ai_feedback import AIFeedback, AIFeedbackStatus
from app.repositories.ai_feedback_repository import AIFeedbackRepository
from app.schemas.ai_feedback import AIFeedbackRead


class AIFeedbackService:
    @staticmethod
    def generate_feedback_for_answer(db: Session, answer: QuestionAnswer) -> AIFeedback | None:
        """
        Generates and saves feedback for a response.
        Catches exceptions to prevent an AI failure from interrupting the submission process.
        """
        question = answer.assessment_question.question
        
        system_prompt = (
            "Eres un profesor universitario experto, constructivo y amable. "
            f"Evalúa la siguiente respuesta de un estudiante a esta pregunta: '{question.statement}'. "
            "Proporciona una retroalimentación concisa de máximo un párrafo indicando si el razonamiento "
            "es correcto o en qué puede mejorar. No asumas nada más allá de lo que el estudiante escribió."
        )

        user_answer = str(answer.answer_json)

        feedback = AIFeedback(
            question_answer_id=answer.id,
            provider="openrouter",
            model_name=settings.openrouter_model,
            prompt=system_prompt,
            status=AIFeedbackStatus.pending
        )
        AIFeedbackRepository.create(db, feedback)
        db.commit()

        try:
            feedback_text, raw_response = LLMClient.generate_feedback(system_prompt, user_answer)
            feedback.feedback_text = feedback_text
            feedback.raw_response = raw_response
            feedback.status = AIFeedbackStatus.completed
            
        except LLMClientError as e:
            feedback.raw_response = str(e)
            feedback.status = AIFeedbackStatus.failed
            
        db.commit()
        db.refresh(feedback)
        
        return feedback

    @staticmethod
    def get_feedback(db: Session, answer_id: int) -> AIFeedbackRead | None:
        feedback = AIFeedbackRepository.get_by_answer_id(db, answer_id)
        if not feedback:
            return None
        return AIFeedbackRead.model_validate(feedback)