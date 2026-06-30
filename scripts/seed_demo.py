from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import SessionLocal
from app.core.security import hash_password
from app.models import (
    User, Role, UserRole, Course, Enrollment, 
    Question, QuestionOption, Assessment, AssessmentQuestion, VisibilityRule
)
from app.models.question import QuestionType
from app.models.assessment import AssessmentType, AssessmentStatus
from app.models.visibility_rule import VisibilityOperator


def get_or_create_role(db: Session, name: str, description: str):
    role = db.query(Role).filter_by(name=name).first()
    if not role:
        role = Role(name=name, description=description)
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


def get_or_create_user(db: Session, email: str, full_name: str, role: Role):
    user = db.query(User).filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password("password123"),  # Generic password for demo purposes
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Assign role to user
        user_role = UserRole(user_id=user.id, role_id=role.id)
        db.add(user_role)
        db.commit()
    return user


def run_seed():
    db: Session = SessionLocal()
    try:
        print("Starting demo data generation...")

        # 1. ROLES
        admin_role = get_or_create_role(db, "admin", "System Administrator")
        teacher_role = get_or_create_role(db, "teacher", "Course Teacher")
        student_role = get_or_create_role(db, "student", "Enrolled Student")

        # 2. USERS
        get_or_create_user(db, "admin@demo.com", "Main Admin", admin_role)
        teacher_user = get_or_create_user(db, "profe@demo.com", "Teacher Fausto", teacher_role)
        student_user = get_or_create_user(db, "estudiante@demo.com", "Diligent Student", student_role)
        print("✅ Users created (Password for all: password123)")

        # 3. COURSE AND ENROLLMENT
        course = db.query(Course).filter_by(name="Automatic Control I").first()
        if not course:
            course = Course(
                teacher_id=teacher_user.id,
                name="Automatic Control I",
                description="Introduction to modeling and control of dynamic systems."
            )
            db.add(course)
            db.commit()
            db.refresh(course)
            
            enrollment = Enrollment(course_id=course.id, student_id=student_user.id, is_active=True)
            db.add(enrollment)
            db.commit()
            print("✅ Course 'Automatic Control I' created and student enrolled.")

        # Check if assessment already exists to avoid duplicating demo data
        existing_assessment = db.query(Assessment).filter_by(title="Midterm 1: PID Controllers").first()
        if existing_assessment:
            print("⚠️ Demo data already exists in the database. Demo is ready.")
            return

        # 4. QUESTION BANK
        print("Creating Question Bank...")
        q1 = Question(
            created_by_id=teacher_user.id,
            question_type=QuestionType.single_choice,
            statement="What is the main objective of the Integral (I) action in a PID controller?",
            is_active=True
        )
        q1.options = [
            QuestionOption(label="Increase the error", value="increase_error", is_correct=False, order_index=1),
            QuestionOption(label="Eliminate steady-state error", value="eliminate_ss_error", is_correct=True, order_index=2),
            QuestionOption(label="Accelerate the system to infinity", value="accelerate", is_correct=False, order_index=3),
        ]
        db.add(q1)

        q2 = Question(
            created_by_id=teacher_user.id,
            question_type=QuestionType.boolean,
            statement="A system is stable if all poles of its closed-loop transfer function have negative real parts.",
            is_active=True
        )
        q2.options = [
            QuestionOption(label="True", value="true", is_correct=True, order_index=1),
            QuestionOption(label="False", value="false", is_correct=False, order_index=2),
        ]
        db.add(q2)

        q3 = Question(
            created_by_id=teacher_user.id,
            question_type=QuestionType.single_choice,
            statement="Do you have previous experience tuning PID controllers on real hardware?",
            is_active=True
        )
        q3.options = [
            QuestionOption(label="Yes", value="yes", is_correct=False, order_index=1),
            QuestionOption(label="No", value="no", is_correct=False, order_index=2),
        ]
        db.add(q3)

        q4 = Question(
            created_by_id=teacher_user.id,
            question_type=QuestionType.open_text,
            statement="Briefly describe which tuning method you used (e.g., Ziegler-Nichols, empirical) and how the result was.",
            is_active=True
        )
        db.add(q4)
        db.commit()
        
        # 5. CREATE EVALUATIVE ACTIVITY (ASSESSMENT)
        assessment = Assessment(
            course_id=course.id,
            created_by_id=teacher_user.id,
            assessment_type=AssessmentType.exam,
            title="Midterm 1: PID Controllers",
            description="Test exam to validate theoretical knowledge and practical experience.",
            status=AssessmentStatus.published,  # Publish it immediately for the demo
            published_at=func.now()
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        # 6. ASSIGN QUESTIONS TO THE ASSESSMENT AND SET POINTS
        aq1 = AssessmentQuestion(assessment_id=assessment.id, question_id=q1.id, order_index=1, points=5.0, is_required=True)
        aq2 = AssessmentQuestion(assessment_id=assessment.id, question_id=q2.id, order_index=2, points=5.0, is_required=True)
        # Filter question grants no points (0.0)
        aq3 = AssessmentQuestion(assessment_id=assessment.id, question_id=q3.id, order_index=3, points=0.0, is_required=True)
        aq4 = AssessmentQuestion(assessment_id=assessment.id, question_id=q4.id, order_index=4, points=10.0, is_required=True)
        
        db.add_all([aq1, aq2, aq3, aq4])
        db.commit()
        db.refresh(aq3)
        db.refresh(aq4)

        # 7. VISIBILITY RULE (Dynamic Form)
        # Question 4 (aq4) is ONLY shown if Question 3 (aq3) is answered with "yes"
        rule = VisibilityRule(
            assessment_question_id=aq4.id,
            depends_on_assessment_question_id=aq3.id,
            operator=VisibilityOperator.equals,
            expected_value_json="yes"
        )
        db.add(rule)
        db.commit()

        print("✅ Question bank, assessment, and dynamic rules created successfully.")
        print(f"\n🎉 DEMO READY!")
        print(f"-> Course ID: {course.id}")
        print(f"-> Assessment ID: {assessment.id}")
        print("\nTo test the student flow in Swagger:")
        print("1. Login with: estudiante@demo.com / password123")
        print(f"2. Execute POST /assessments/{assessment.id}/attempts/start")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()