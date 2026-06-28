from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Assessment, AssessmentQuestion, User, Course
from app.models.assessment import AssessmentStatus
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.role_repository import RoleRepository
from app.schemas.assessment import (
    AssessmentCreate, AssessmentRead, AssessmentUpdate, 
    AssessmentQuestionCreate, AssessmentQuestionRead, AssessmentQuestionUpdate
)

class AssessmentService:
    
    @staticmethod
    def _ensure_course_manager(db: Session, course_id: int, current_user: User) -> Course:
        course = CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
            
        is_admin = RoleRepository.user_has_role(db, current_user.id, "admin")
        if not is_admin and course.teacher_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not manage this course")
        return course

    @staticmethod
    def _ensure_assessment_manager(db: Session, assessment_id: int, current_user: User) -> Assessment:
        assessment = AssessmentRepository.get_by_id(db, assessment_id)
        if not assessment or assessment.status == AssessmentStatus.archived:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found or archived")
            
        # Reutilizamos la lógica del curso para asegurar que sea dueño del curso
        AssessmentService._ensure_course_manager(db, assessment.course_id, current_user)
        return assessment

    # --- ASSESSMENTS ---

    @staticmethod
    def create_assessment(db: Session, course_id: int, data: AssessmentCreate, current_user: User) -> AssessmentRead:
        AssessmentService._ensure_course_manager(db, course_id, current_user)
        
        assessment = Assessment(
            course_id=course_id,
            created_by_id=current_user.id,
            assessment_type=data.assessment_type,
            title=data.title,
            description=data.description,
            status=AssessmentStatus.draft
        )
        
        AssessmentRepository.create(db, assessment)
        db.commit()
        db.refresh(assessment)
        return AssessmentRead.model_validate(assessment)

    @staticmethod
    def update_assessment(db: Session, assessment_id: int, data: AssessmentUpdate, current_user: User) -> AssessmentRead:
        assessment = AssessmentService._ensure_assessment_manager(db, assessment_id, current_user)
        
        if data.title is not None:
            assessment.title = data.title
        if data.description is not None:
            assessment.description = data.description
            
        db.commit()
        db.refresh(assessment)
        return AssessmentRead.model_validate(assessment)

    @staticmethod
    def archive_assessment(db: Session, assessment_id: int, current_user: User):
        assessment = AssessmentService._ensure_assessment_manager(db, assessment_id, current_user)
        assessment.status = AssessmentStatus.archived
        db.commit()

    @staticmethod
    def publish_assessment(db: Session, assessment_id: int, current_user: User) -> AssessmentRead:
        assessment = AssessmentService._ensure_assessment_manager(db, assessment_id, current_user)
        
        if assessment.status == AssessmentStatus.published:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assessment is already published")
            
        assessment.status = AssessmentStatus.published
        assessment.published_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(assessment)
        return AssessmentRead.model_validate(assessment)

    @staticmethod
    def get_assessment(db: Session, assessment_id: int, current_user: User) -> AssessmentRead:
        assessment = AssessmentRepository.get_by_id(db, assessment_id)
        if not assessment or assessment.status == AssessmentStatus.archived:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
        return AssessmentRead.model_validate(assessment)

    @staticmethod
    def list_course_assessments(db: Session, course_id: int) -> list[AssessmentRead]:
        assessments = AssessmentRepository.list_by_course(db, course_id)
        return [AssessmentRead.model_validate(a) for a in assessments]

    # --- ASSESSMENT QUESTIONS ---

    @staticmethod
    def add_question(db: Session, assessment_id: int, data: AssessmentQuestionCreate, current_user: User) -> AssessmentQuestionRead:
        AssessmentService._ensure_assessment_manager(db, assessment_id, current_user)
        
        question = QuestionRepository.get_by_id(db, data.question_id)
        if not question or not question.is_active:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or inactive question from bank")
             
        aq = AssessmentQuestion(
            assessment_id=assessment_id,
            question_id=data.question_id,
            order_index=data.order_index,
            points=data.points,
            is_required=data.is_required
        )
        
        try:
            AssessmentRepository.add_question(db, aq)
            db.commit()
            db.refresh(aq)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Question already added or order_index duplicated in this assessment"
            )
            
        return AssessmentQuestionRead.model_validate(aq)

    @staticmethod
    def list_assessment_questions(db: Session, assessment_id: int) -> list[AssessmentQuestionRead]:
        questions = AssessmentRepository.list_assessment_questions(db, assessment_id)
        return [AssessmentQuestionRead.model_validate(q) for q in questions]

    @staticmethod
    def update_assessment_question(db: Session, assessment_id: int, aq_id: int, data: AssessmentQuestionUpdate, current_user: User) -> AssessmentQuestionRead:
        AssessmentService._ensure_assessment_manager(db, assessment_id, current_user)
        
        aq = AssessmentRepository.get_assessment_question(db, aq_id)
        if not aq or aq.assessment_id != assessment_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment question not found")
            
        if data.order_index is not None:
            aq.order_index = data.order_index
        if data.points is not None:
            aq.points = data.points
        if data.is_required is not None:
            aq.is_required = data.is_required
            
        try:
            db.commit()
            db.refresh(aq)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order index duplicated")
            
        return AssessmentQuestionRead.model_validate(aq)

    @staticmethod
    def remove_question(db: Session, assessment_id: int, aq_id: int, current_user: User):
        AssessmentService._ensure_assessment_manager(db, assessment_id, current_user)
        aq = AssessmentRepository.get_assessment_question(db, aq_id)
        if not aq or aq.assessment_id != assessment_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment question not found")
            
        db.delete(aq)
        db.commit()