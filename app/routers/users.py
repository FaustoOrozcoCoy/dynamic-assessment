from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db import get_db
from app.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return UserService.create_user(
        db=db,
        user_data=user_data,
    )


@router.get(
    "",
    response_model=list[UserRead],
)
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return UserService.list_users(db=db)


@router.get(
    "/{user_id}",
    response_model=UserRead,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return UserService.get_user(
        db=db,
        user_id=user_id,
    )


@router.patch(
    "/{user_id}",
    response_model=UserRead,
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return UserService.update_user(
        db=db,
        user_id=user_id,
        user_data=user_data,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    UserService.deactivate_user(
        db=db,
        user_id=user_id,
    )

    return None