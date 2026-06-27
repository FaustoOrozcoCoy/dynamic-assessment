from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Course


class CourseRepository:
    @staticmethod
    def create(
        db: Session,
        course: Course,
    ) -> Course:
        db.add(course)
        return course

    @staticmethod
    def get_by_id(
        db: Session,
        course_id: int,
    ) -> Course | None:
        return db.get(Course, course_id)

    @staticmethod
    def list_all_active(
        db: Session,
    ) -> list[Course]:
        statement = (
            select(Course)
            .where(Course.is_active.is_(True))
            .order_by(Course.id)
        )

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def list_by_teacher(
        db: Session,
        teacher_id: int,
    ) -> list[Course]:
        statement = (
            select(Course)
            .where(Course.teacher_id == teacher_id)
            .where(Course.is_active.is_(True))
            .order_by(Course.id)
        )

        return list(db.execute(statement).scalars().all())