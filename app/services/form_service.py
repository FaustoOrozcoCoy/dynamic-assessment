from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import User, VisibilityRule
from app.models.assessment import AssessmentStatus
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.visibility_repository import VisibilityRuleRepository
from app.schemas.form import (
    VisibilityRuleCreate, VisibilityRuleRead, FormRead, FormQuestionRead, FormOptionRead,
    VisibilityPreviewRequest, VisibilityPreviewResponse
)

class FormService:

    @staticmethod
    def create_visibility_rule(db: Session, aq_id: int, data: VisibilityRuleCreate, current_user: User) -> VisibilityRuleRead:
        target_aq = AssessmentRepository.get_assessment_question(db, aq_id)
        depends_on_aq = AssessmentRepository.get_assessment_question(db, data.depends_on_assessment_question_id)
        
        if not target_aq or not depends_on_aq:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment question not found")
        
        if target_aq.assessment_id != depends_on_aq.assessment_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Questions must belong to the same assessment")
            
        if target_aq.order_index <= depends_on_aq.order_index:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A question can only depend on a previous question")

        rule = VisibilityRule(
            assessment_question_id=target_aq.id,
            depends_on_assessment_question_id=depends_on_aq.id,
            operator=data.operator,
            expected_value_json=data.expected_value_json
        )
        
        try:
            VisibilityRuleRepository.create(db, rule)
            db.commit()
            db.refresh(rule)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Visibility rule already exists for this question")
            
        return VisibilityRuleRead.model_validate(rule)

    @staticmethod
    def get_visibility_rule(db: Session, aq_id: int, current_user: User) -> VisibilityRuleRead:
        rule = VisibilityRuleRepository.get_by_assessment_question(db, aq_id)
        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visibility rule not found")
        return VisibilityRuleRead.model_validate(rule)

    @staticmethod
    def delete_visibility_rule(db: Session, aq_id: int, current_user: User):
        rule = VisibilityRuleRepository.get_by_assessment_question(db, aq_id)
        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visibility rule not found")
        VisibilityRuleRepository.delete(db, rule)
        db.commit()

    @staticmethod
    def get_assessment_form(db: Session, assessment_id: int, current_user: User) -> FormRead:
        assessment = AssessmentRepository.get_by_id(db, assessment_id)
        if not assessment or assessment.status == AssessmentStatus.archived:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

        is_student = RoleRepository.user_has_role(db, current_user.id, "student")
        if is_student and assessment.status != AssessmentStatus.published:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Assessment is not published yet")

        aqs = AssessmentRepository.list_assessment_questions(db, assessment_id)
        
        form_questions = []
        for aq in aqs:
            options = [FormOptionRead.model_validate(opt) for opt in aq.question.options]
            
            fq = FormQuestionRead(
                assessment_question_id=aq.id,
                question_id=aq.question.id,
                statement=aq.question.statement,
                question_type=aq.question.question_type,
                image_path=aq.question.image_path,
                config_json=aq.question.config_json,
                order_index=aq.order_index,
                points=aq.points,
                is_required=aq.is_required,
                options=options,
                visibility_rule=VisibilityRuleRead.model_validate(aq.visibility_rule) if aq.visibility_rule else None
            )
            form_questions.append(fq)
            
        return FormRead(
            assessment_id=assessment.id,
            title=assessment.title,
            description=assessment.description,
            questions=form_questions
        )