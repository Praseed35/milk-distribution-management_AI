from sqlalchemy.orm import Session

from app.models.milk_type import MilkType
from app.schemas.milk_type import MilkTypeCreate, MilkTypeUpdate

from app.exceptions.milk_type import (
    DuplicateMilkNameError,
    MilkTypeError
)


def create(
    db: Session,
    milk_type: MilkTypeCreate
) -> MilkType:

    existing_milk_name = (
        db.query(MilkType)
        .filter(
            MilkType.milk_name == milk_type.milk_name
        )
        .first()
    )

    if existing_milk_name:
        raise DuplicateMilkNameError(
            milk_type.milk_name
        )

    new_milk_type = MilkType(
        milk_name=milk_type.milk_name,
        volume_ml=milk_type.volume_ml,
        description=milk_type.description
    )

    db.add(new_milk_type)

    db.commit()

    db.refresh(new_milk_type)

    return new_milk_type

def get_all(
    db: Session
) -> list[MilkType]:

    milk_types = (
        db.query(MilkType)
        .filter(
            MilkType.is_active == True
        )
        .all()
    )

    return milk_types

def get_by_id(
    db: Session,
    milk_type_id: int
) -> MilkType:

    milk_type = (
        db.query(MilkType)
        .filter(
            MilkType.id == milk_type_id,
            MilkType.is_active == True
        )
        .first()
    )

    if not milk_type:
        raise MilkTypeError()

    return milk_type

def update_by_id(
        db: Session,
        milk_type_id: int,
        milk_type: MilkTypeUpdate
) -> MilkType:

    milk_type_to_update = (
        db.query(MilkType)
        .filter(
            MilkType.id == milk_type_id,
            MilkType.is_active == True
        )
        .first()
    )

    if not milk_type_to_update:
        raise MilkTypeError()

    existing_milk_name = (
        db.query(MilkType)
        .filter(
            MilkType.milk_name == milk_type.milk_name,
            MilkType.id != milk_type_id
        )
        .first()
    )

    if existing_milk_name:
        raise DuplicateMilkNameError(
            milk_type.milk_name
        )

    milk_type_to_update.milk_name = milk_type.milk_name
    milk_type_to_update.volume_ml = milk_type.volume_ml
    milk_type_to_update.description = milk_type.description

    db.commit()
    db.refresh(milk_type_to_update)

    return milk_type_to_update

def delete_by_id(
    db: Session,
    milk_type_id: int
) -> MilkType:

    milk_type_to_delete = (
        db.query(MilkType)
        .filter(
            MilkType.id == milk_type_id,
            MilkType.is_active == True
        )
        .first()
    )

    if not milk_type_to_delete:
        raise MilkTypeError()

    milk_type_to_delete.is_active = False

    db.commit()
    db.refresh(milk_type_to_delete)

    return milk_type_to_delete
