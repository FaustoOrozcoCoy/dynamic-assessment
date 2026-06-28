from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin_or_teacher, get_current_user
from app.db import get_db
from app.models import User
from app.schemas.form import VisibilityRuleCreate, VisibilityRuleRead, FormRead
from app.services.form_service import FormService

router = APIRouter(
    tags=["Forms & Visibility"],
)

# === 11. VISIBILITY RULES ===

@router.post("/assessment-questions/{assessment_question_id}/visibility-rule", response_model=VisibilityRuleRead, status_code=status.HTTP_201_CREATED)
def create_visibility_rule(
    assessment_question_id: int,
    data: VisibilityRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_teacher)
):
    return FormService.create_visibility_rule(db, assessment_question_id, data, current_user)

@router.get("/assessment-questions/{assessment_question_id}/visibility-rule", response_model=VisibilityRuleRead)
def get_visibility_rule(
    assessment_question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_teacher)
):
    return FormService.get_visibility_rule(db, assessment_question_id, current_user)

@router.delete("/assessment-questions/{assessment_question_id}/visibility-rule", status_code=status.HTTP_204_NO_CONTENT)
def delete_visibility_rule(
    assessment_question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_teacher)
):
    FormService.delete_visibility_rule(db, assessment_question_id, current_user)
    return None

# === 12. FORMS ===

@router.get("/assessments/{assessment_id}/form", response_model=FormRead)
def get_assessment_form(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Alumnos también pueden ver el form
):
    return FormService.get_assessment_form(db, assessment_id, current_user)