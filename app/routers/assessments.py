from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin_or_teacher, get_current_user
from app.db import get_db
from app.models import User
from app.schemas.assessment import (
    AssessmentCreate, AssessmentRead, AssessmentUpdate,
    AssessmentQuestionCreate, AssessmentQuestionRead, AssessmentQuestionUpdate
)
from app.services.assessment_service import AssessmentService

router = APIRouter(
    tags=["Assessments"],
)

# === 9. ASSESSMENTS ===

@router.post("/courses/{course_id}/assessments", response_model=AssessmentRead, status_code=status.HTTP_201_CREATED)
def create_assessment(
    course_id: int,
    data: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_teacher)
):
    return AssessmentService.create_assessment(db, course_id, data, current_user)

@router.get("/courses/{course_id}/assessments", response_model=list[AssessmentRead])
def list_course_assessments(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Student/Admin/Teacher
):
    return AssessmentService.list_course_assessments(db, course_id)

@router.get("/assessments/{assessment_id}", response_model=AssessmentRead)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_teacher)
):
    return AssessmentService.get_assessment(db, assessment_id, current_user)

@router.patch("/assessments/{assessment_id}", response_model=AssessmentRead)
def update_assessment(
    assessment_id: int,
    data: AssessmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_teacher)
):
    return AssessmentService.update_assessment(db, assessment_id, data, current_user)

@router.delete("/assessments/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_teacher)
):
    AssessmentService.archive_assessment(db, assessment_id, current_user)
    return None

@router.post("/assessments/{assessment_id}/publish", response_model=AssessmentRead)
def publish_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_teacher)
):
    return AssessmentService.publish_assessment(db, assessment_id, current_user)

# === 10. ASSESSMENT QUESTIONS ===

@router.post("/assessments/{assessment_id}/questions", response_model=AssessmentQuestionRead, status_code=status.HTTP_201_CREATED)
def add_assessment_question(
    assessment_id: int,
    data: AssessmentQuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_teacher)
):
    return AssessmentService.add_question(db, assessment_id, data, current_user)

@router.get("/assessments/{assessment_id}/questions", response_model=list[AssessmentQuestionRead])
def list_assessment_questions(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_teacher)
):
    return AssessmentService.list_assessment_questions(db, assessment_id)

@router.patch("/assessments/{assessment_id}/questions/{assessment_question_id}", response_model=AssessmentQuestionRead)
def update_assessment_question(
    assessment_id: int,
    assessment_question_id: int,
    data: AssessmentQuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_teacher)
):
    return AssessmentService.update_assessment_question(db, assessment_id, assessment_question_id, data, current_user)

@router.delete("/assessments/{assessment_id}/questions/{assessment_question_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_assessment_question(
    assessment_id: int,
    assessment_question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_teacher)
):
    AssessmentService.remove_question(db, assessment_id, assessment_question_id, current_user)
    return None