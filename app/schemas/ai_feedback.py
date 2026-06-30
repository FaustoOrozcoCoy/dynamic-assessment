from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.ai_feedback import AIFeedbackStatus

class AIFeedbackRead(BaseModel):
    id: int
    question_answer_id: int
    provider: str
    model_name: str
    feedback_text: str | None
    status: AIFeedbackStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)