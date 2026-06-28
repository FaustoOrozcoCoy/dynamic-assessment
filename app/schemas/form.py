from pydantic import BaseModel, ConfigDict
from app.models.question import QuestionType
from app.models.visibility_rule import VisibilityOperator

# --- VISIBILITY RULES ---
class VisibilityRuleCreate(BaseModel):
    depends_on_assessment_question_id: int
    operator: VisibilityOperator
    expected_value_json: dict | list | str | int | float | bool

class VisibilityRuleRead(BaseModel):
    id: int
    assessment_question_id: int
    depends_on_assessment_question_id: int
    operator: VisibilityOperator
    expected_value_json: dict | list | str | int | float | bool
    
    model_config = ConfigDict(from_attributes=True)

# --- PUBLIC FORM SCHEMAS (without is_correct) ---
class FormOptionRead(BaseModel):
    id: int
    label: str
    value: str
    is_exclusive: bool
    order_index: int
    model_config = ConfigDict(from_attributes=True)

class FormQuestionRead(BaseModel):
    assessment_question_id: int
    question_id: int
    statement: str
    question_type: QuestionType
    image_path: str | None
    config_json: dict | None
    order_index: int
    points: float
    is_required: bool
    options: list[FormOptionRead] = []
    visibility_rule: VisibilityRuleRead | None = None

class FormRead(BaseModel):
    assessment_id: int
    title: str
    description: str | None
    questions: list[FormQuestionRead] = []

class VisibilityPreviewRequest(BaseModel):
    current_answers: dict[int, dict | list | str | int | float | bool]

class VisibilityPreviewResponse(BaseModel):
    visibility_state: dict[int, bool]