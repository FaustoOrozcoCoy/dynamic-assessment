from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db import get_db
from app.models import User
from app.schemas.ai_feedback import AIFeedbackRead
from app.schemas.attempt import AssessmentAttemptRead
from app.services.ai_feedback_service import AIFeedbackService
from app.services.attempt_service import AttemptService

router = APIRouter(
    tags=["Results & Feedback"],
)

@router.get("/attempts/{attempt_id}/results", response_model=AssessmentAttemptRead)
def get_attempt_results(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return AttemptService.get_attempt(db, attempt_id, current_user)

@router.get("/question-answers/{answer_id}/ai-feedback", response_model=AIFeedbackRead)
def get_ai_feedback(
    answer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    feedback = AIFeedbackService.get_feedback(db, answer_id)
    if not feedback:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No feedback found for this answer")
    return feedback