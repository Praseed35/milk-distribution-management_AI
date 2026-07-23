from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.schemas.milk_type import (
    MilkTypeCreate,
    MilkTypeResponse,
    MilkTypeUpdate
)

from app.services import milk_type_service

from app.exceptions.milk_type import (
    DuplicateMilkNameError,
    MilkTypeError
)


router = APIRouter(
    prefix="/milk-types",
    tags=["Milk Types"]
)

@router.post(
    "/",
    response_model=MilkTypeResponse
)
def create_milk_type(
    milk_type: MilkTypeCreate,
    db: Session = Depends(get_db)
):
    try:

        return milk_type_service.create(
            db,
            milk_type
        )

    except DuplicateMilkNameError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get(
    "/",
    response_model=list[MilkTypeResponse]
)
def get_milk_types(
    db: Session = Depends(get_db)
):

    return milk_type_service.get_all(
        db
    )

@router.get(
    "/{milk_type_id}",
    response_model=MilkTypeResponse
)
def get_milk_type(
    milk_type_id: int,
    db: Session = Depends(get_db)
):

    try:

        return milk_type_service.get_by_id(
            db,
            milk_type_id
        )

    except MilkTypeError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

@router.put(
    "/{milk_type_id}",
    response_model=MilkTypeResponse
)
def update_milk_type(
    milk_type_id: int,
    milk_type: MilkTypeUpdate,
    db: Session = Depends(get_db)
):
    try:

        return milk_type_service.update_by_id(
            db,
            milk_type_id,
            milk_type
        )

    except MilkTypeError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except DuplicateMilkNameError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.delete(
    "/{milk_type_id}",
    response_model=MilkTypeResponse
)
def delete_milk_type(
    milk_type_id: int,
    db: Session = Depends(get_db)
):

    try:

        return milk_type_service.delete_by_id(
            db,
            milk_type_id
        )

    except MilkTypeError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
