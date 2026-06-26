from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    @staticmethod
    def create(
        db: Session,
        user: User,
    ) -> User:
        db.add(user)
        return user

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int,
    ) -> User | None:
        return db.get(User, user_id)

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> User | None:
        statement = select(User).where(User.email == email)
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def list_all(
        db: Session,
    ) -> list[User]:
        statement = select(User).order_by(User.id)
        return list(db.execute(statement).scalars().all())