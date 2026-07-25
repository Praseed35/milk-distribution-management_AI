from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.schemas.employee import (
    EmployeeCreate,
    EmployeeCredentialsUpdate,
    EmployeeResponse,
    EmployeeUpdate
)

from app.services import employee_service

from app.core.roles import require_role

from app.exceptions.employee import (
    EmployeeNotFoundError,
    DuplicateEmployeePhoneError,
    EmployeeRouteNotFoundError,
    InactiveRouteError,
    EmployeeUserNotFoundError,
    InactiveUserError,
    DuplicateUsernameError,
    EmployeeNoLinkedUserError
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=201
)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(["OWNER"])
    )
):

    try:

        return employee_service.create(
            db,
            employee
        )

    except DuplicateEmployeePhoneError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except EmployeeRouteNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except InactiveRouteError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except DuplicateUsernameError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=list[EmployeeResponse]
)
def get_all_employees(
    db: Session = Depends(get_db)
):

    return employee_service.get_all(
        db
    )


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def get_employee_by_id(
    employee_id: int,
    db: Session = Depends(get_db)
):

    try:

        return employee_service.get_by_id(
            db,
            employee_id
        )

    except EmployeeNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def update_employee_by_id(
    employee_id: int,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db)
):

    try:

        return employee_service.update_by_id(
            db,
            employee_id,
            employee
        )

    except EmployeeNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except DuplicateEmployeePhoneError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except EmployeeRouteNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except InactiveRouteError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.put(
    "/{employee_id}/credentials",
    response_model=EmployeeResponse
)
def update_employee_credentials(
    employee_id: int,
    credentials: EmployeeCredentialsUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(["OWNER"])
    )
):

    try:

        return employee_service.update_credentials(
            db,
            employee_id,
            credentials
        )

    except EmployeeNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except EmployeeNoLinkedUserError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except EmployeeUserNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except DuplicateUsernameError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def delete_employee_by_id(
    employee_id: int,
    db: Session = Depends(get_db)
):

    try:

        return employee_service.delete_by_id(
            db,
            employee_id
        )

    except EmployeeNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
