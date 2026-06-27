from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Course, Enrollment


class EnrollmentRepository:
    @staticmethod
    def create(
        db: Session,
        enrollment: Enrollment,
    ) -> Enrollment:
        db.add(enrollment)
        return enrollment

    @staticmethod
    def get_by_course_and_student(
        db: Session,
        course_id: int,
        student_id: int,
    ) -> Enrollment | None:
        statement = (
            select(Enrollment)
            .where(Enrollment.course_id == course_id)
            .where(Enrollment.student_id == student_id)
        )

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def list_by_course(
        db: Session,
        course_id: int,
    ) -> list[Enrollment]:
        statement = (
            select(Enrollment)
            .where(Enrollment.course_id == course_id)
            .where(Enrollment.is_active.is_(True))
            .order_by(Enrollment.id)
        )

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def list_courses_by_student(
        db: Session,
        student_id: int,
    ) -> list[Course]:
        statement = (
            select(Course)
            .join(Enrollment, Enrollment.course_id == Course.id)
            .where(Enrollment.student_id == student_id)
            .where(Enrollment.is_active.is_(True))
            .where(Course.is_active.is_(True))
            .order_by(Course.id)
        )

        return list(db.execute(statement).scalars().all())