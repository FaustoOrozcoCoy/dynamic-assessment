from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Role, User, UserRole


class RoleRepository:
    @staticmethod
    def create(
        db: Session,
        role: Role,
    ) -> Role:
        db.add(role)
        return role

    @staticmethod
    def get_by_name(
        db: Session,
        name: str,
    ) -> Role | None:
        statement = select(Role).where(Role.name == name)
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def list_all(
        db: Session,
    ) -> list[Role]:
        statement = select(Role).order_by(Role.id)
        return list(db.execute(statement).scalars().all())

    @staticmethod
    def get_user_role_names(
        db: Session,
        user_id: int,
    ) -> list[str]:
        statement = (
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .order_by(Role.name)
        )

        return list(db.execute(statement).scalars().all())

    @staticmethod
    def user_has_role(
        db: Session,
        user_id: int,
        role_name: str,
    ) -> bool:
        statement = (
            select(Role.id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .where(Role.name == role_name)
        )

        return db.execute(statement).scalar_one_or_none() is not None

    @staticmethod
    def assign_role(
        db: Session,
        user: User,
        role: Role,
    ) -> UserRole:
        user_role = UserRole(
            user_id=user.id,
            role_id=role.id,
        )

        db.add(user_role)

        return user_role

    @staticmethod
    def get_user_role(
        db: Session,
        user_id: int,
        role_id: int,
    ) -> UserRole | None:
        statement = (
            select(UserRole)
            .where(UserRole.user_id == user_id)
            .where(UserRole.role_id == role_id)
        )

        return db.execute(statement).scalar_one_or_none()