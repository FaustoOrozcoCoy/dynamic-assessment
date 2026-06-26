from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db import get_db
from app.models import User
from app.schemas.user import RoleRead, UserRead
from app.services.role_service import RoleService

router = APIRouter(
    tags=["Roles"],
)


@router.get(
    "/roles",
    response_model=list[RoleRead],
)
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return RoleService.list_roles(db=db)


@router.post(
    "/users/{user_id}/roles/{role_name}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
def assign_role_to_user(
    user_id: int,
    role_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return RoleService.assign_role_to_user(
        db=db,
        user_id=user_id,
        role_name=role_name,
    )


@router.delete(
    "/users/{user_id}/roles/{role_name}",
    response_model=UserRead,
)
def remove_role_from_user(
    user_id: int,
    role_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return RoleService.remove_role_from_user(
        db=db,
        user_id=user_id,
        role_name=role_name,
    )