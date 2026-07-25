from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.auth import ChangePassword

from app.core.security import (
    verify_password,
    hash_password,
    create_access_token
)


def login(
    db: Session,
    login_data: LoginRequest
):

    user = (
        db.query(User)
        .filter(
            User.username == login_data.username
        )
        .first()
    )

    if not user:
        return None

    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        return None

    access_token = create_access_token(
        {
            "sub": user.username,
            "role": user.role
        }
    )

    return access_token


def change_password(
    db: Session,
    user: User,
    data: ChangePassword
):

    if not verify_password(
        data.current_password,
        user.password_hash
    ):
        return False

    user.password_hash = hash_password(data.new_password)
    db.commit()

    return True