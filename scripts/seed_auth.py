from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db import SessionLocal
from app.models import Role, User, UserRole
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository


def create_role_if_not_exists(
    db: Session,
    name: str,
    description: str,
) -> Role:
    role = RoleRepository.get_by_name(
        db=db,
        name=name,
    )

    if role is not None:
        return role

    role = Role(
        name=name,
        description=description,
    )

    db.add(role)
    db.flush()

    return role


def create_user_if_not_exists(
    db: Session,
    email: str,
    password: str,
    full_name: str,
) -> User:
    user = UserRepository.get_by_email(
        db=db,
        email=email,
    )

    if user is not None:
        return user

    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        is_active=True,
    )

    db.add(user)
    db.flush()

    return user


def assign_role_if_not_exists(
    db: Session,
    user: User,
    role: Role,
) -> None:
    existing_user_role = RoleRepository.get_user_role(
        db=db,
        user_id=user.id,
        role_id=role.id,
    )

    if existing_user_role is not None:
        return

    user_role = UserRole(
        user_id=user.id,
        role_id=role.id,
    )

    db.add(user_role)


def main():
    db = SessionLocal()

    try:
        admin_role = create_role_if_not_exists(
            db=db,
            name="admin",
            description="System administrator",
        )

        teacher_role = create_role_if_not_exists(
            db=db,
            name="teacher",
            description="Course teacher",
        )

        student_role = create_role_if_not_exists(
            db=db,
            name="student",
            description="Course student",
        )

        admin_user = create_user_if_not_exists(
            db=db,
            email="admin@example.com",
            password="admin12345",
            full_name="Admin User",
        )

        teacher_user = create_user_if_not_exists(
            db=db,
            email="teacher@example.com",
            password="teacher12345",
            full_name="Teacher User",
        )

        student_user = create_user_if_not_exists(
            db=db,
            email="student@example.com",
            password="student12345",
            full_name="Student User",
        )

        assign_role_if_not_exists(
            db=db,
            user=admin_user,
            role=admin_role,
        )

        assign_role_if_not_exists(
            db=db,
            user=teacher_user,
            role=teacher_role,
        )

        assign_role_if_not_exists(
            db=db,
            user=student_user,
            role=student_role,
        )

        db.commit()

        print("Auth seed completed successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()