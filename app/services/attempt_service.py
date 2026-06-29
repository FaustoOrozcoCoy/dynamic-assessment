from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone


from app.models import User, Assessment
from app.models.attempt import AssessmentAttempt, AttemptStatus, QuestionAnswer
from app.models.assessment import AssessmentStatus
from app.models.visibility_rule import VisibilityOperator, VisibilityRule
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.schemas.attempt import AssessmentAttemptRead, AnswerListSave, AttemptFormRead, SubmitResponse
from app.services.assessment_service import AssessmentService
from app.services.form_service import FormService


class AttemptService:

    @staticmethod
    def _ensure_student_enrolled_and_published(db: Session, assessment_id: int, student_id: int) -> Assessment:
        assessment = AssessmentRepository.get_by_id(db, assessment_id)
        if not assessment or assessment.status == AssessmentStatus.archived:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
            
        if assessment.status != AssessmentStatus.published:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assessment is not published")

        enrollment = EnrollmentRepository.get_by_course_and_student(db, assessment.course_id, student_id)
        if not enrollment or not enrollment.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not enrolled in this course")

        return assessment

    @staticmethod
    def start_attempt(db: Session, assessment_id: int, current_user: User) -> AssessmentAttemptRead:
        AttemptService._ensure_student_enrolled_and_published(db, assessment_id, current_user.id)

        # Resume
        in_progress = AttemptRepository.get_in_progress_attempt(db, assessment_id, current_user.id)
        if in_progress:
            return AssessmentAttemptRead.model_validate(in_progress)

        # New attempt
        max_attempt = AttemptRepository.get_max_attempt_number(db, assessment_id, current_user.id)
        
        new_attempt = AssessmentAttempt(
            assessment_id=assessment_id,
            student_id=current_user.id,
            attempt_number=max_attempt + 1,
            status=AttemptStatus.in_progress
        )
        
        AttemptRepository.create_attempt(db, new_attempt)
        db.commit()
        db.refresh(new_attempt)
        
        return AssessmentAttemptRead.model_validate(new_attempt)

    @staticmethod
    def get_attempt(db: Session, attempt_id: int, current_user: User) -> AssessmentAttemptRead:
        attempt = AttemptRepository.get_by_id(db, attempt_id)
        if not attempt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
            
        if attempt.student_id != current_user.id:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your attempt")

        return AssessmentAttemptRead.model_validate(attempt)

    @staticmethod
    def save_partial_answers(db: Session, attempt_id: int, data: AnswerListSave, current_user: User):
        attempt = AttemptRepository.get_by_id(db, attempt_id)
        if not attempt or attempt.student_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
            
        if attempt.status != AttemptStatus.in_progress:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot save answers for a submitted attempt")

        for ans_data in data.answers:
            
            existing_ans = AttemptRepository.get_answer(db, attempt.id, ans_data.assessment_question_id)
            if existing_ans:
                existing_ans.answer_json = ans_data.answer_json
            else:
                new_ans = QuestionAnswer(
                    attempt_id=attempt.id,
                    assessment_question_id=ans_data.assessment_question_id,
                    answer_json=ans_data.answer_json
                )
                AttemptRepository.save_answer(db, new_ans)

        db.commit()

    @staticmethod
    def get_attempt_form(db: Session, attempt_id: int, current_user: User) -> AttemptFormRead:
        attempt = AttemptRepository.get_by_id(db, attempt_id)
        if not attempt or attempt.student_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
            
        form_structure = FormService.get_assessment_form(db, attempt.assessment_id, current_user)
        
        saved_answers = {
            ans.assessment_question_id: ans.answer_json 
            for ans in attempt.answers
        }

        return AttemptFormRead(
            attempt_id=attempt.id,
            status=attempt.status,
            form=form_structure,
            saved_answers=saved_answers
        )

    @staticmethod
    def _evaluate_visibility(rule: VisibilityRule, answer_value: any) -> bool:
        if answer_value is None:
            return False
            
        expected = rule.expected_value_json
        op = rule.operator

        try:
            if op == VisibilityOperator.equals:
                return answer_value == expected
            elif op == VisibilityOperator.not_equals:
                return answer_value != expected
            elif op == VisibilityOperator.contains:
                if isinstance(answer_value, list):
                    return expected in answer_value
                elif isinstance(answer_value, str):
                    return str(expected) in answer_value
                return False
            elif op == VisibilityOperator.greater_than:
                return float(answer_value) > float(expected)
            elif op == VisibilityOperator.less_than:
                return float(answer_value) < float(expected)
        except (ValueError, TypeError):
            return False
            
        return False

    @staticmethod
    def submit_attempt(db: Session, attempt_id: int, current_user: User) -> SubmitResponse:
        attempt = AttemptRepository.get_by_id(db, attempt_id)
        if not attempt or attempt.student_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
            
        if attempt.status != AttemptStatus.in_progress:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attempt is already submitted or graded")

        assessment_questions = AssessmentRepository.list_assessment_questions(db, attempt.assessment_id)
        
        answers_map = {ans.assessment_question_id: ans for ans in attempt.answers}
        
        missing_required = []

        for aq in assessment_questions:
            is_visible = True
            
            # Verify visibility rules
            if aq.visibility_rule is not None:
                depends_on_id = aq.visibility_rule.depends_on_assessment_question_id
                parent_ans = answers_map.get(depends_on_id)
                parent_val = parent_ans.answer_json if parent_ans else None
                
                is_visible = AttemptService._evaluate_visibility(aq.visibility_rule, parent_val)

            # Check if the question is required and visible, and if the answer is missing
            if is_visible and aq.is_required:
                ans = answers_map.get(aq.id)

                if not ans or ans.answer_json is None or ans.answer_json == "" or ans.answer_json == []:
                    missing_required.append(aq.id)

        # If there are missing required answers, raise an error  (Atomyc)
        if missing_required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Missing answers for required visible questions: {missing_required}"
            )

        # If everything is fine, close the attempt
        attempt.status = AttemptStatus.submitted
        attempt.submitted_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(attempt)
        
        return SubmitResponse(
            message="Attempt submitted successfully.",
            attempt=AssessmentAttemptRead.model_validate(attempt)
        )