from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.dependencies import get_db
from app.schemas.auth import LoginRequest
from app.schemas.auth import ChangePassword
from app.models.user import User
from app.core.auth import get_current_user
from app.core.roles import require_role
from app.services import auth_service


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):

    access_token = auth_service.login(
        db,
        login_data
    )

    if access_token is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role
    }

@router.put("/change-password")
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    success = auth_service.change_password(
        db,
        current_user,
        data
    )

    if not success:

        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect."
        )

    return {
        "message": "Password changed successfully."
    }

@router.get("/owner-dashboard")
def owner_dashboard(
    current_user = Depends(
        require_role(
            ["OWNER"]
        )
    )
):
    return {
        "message": "Welcome Owner"
    }