from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.route import Route
from app.models.user import User

from app.schemas.employee import EmployeeCreate
from app.schemas.employee import EmployeeUpdate
from app.schemas.employee import EmployeeCredentialsUpdate

from app.core.security import hash_password

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


def create(
        db: Session,
        employee: EmployeeCreate
) -> Employee:

    if employee.route_id is not None:
        existing_route = (
            db.query(Route)
            .filter(
                Route.id == employee.route_id
            )
            .first()
        )

        if not existing_route:
            raise EmployeeRouteNotFoundError()

        if not existing_route.is_active:
            raise InactiveRouteError()

    existing_phone = (
        db.query(Employee)
        .filter(
            Employee.phone == employee.phone
        )
        .first()
    )

    if existing_phone:
        raise DuplicateEmployeePhoneError(
            employee.phone
        )

    user_id = None

    if employee.username is not None:
        existing_user = (
            db.query(User)
            .filter(
                User.username == employee.username
            )
            .first()
        )

        if existing_user:
            raise DuplicateUsernameError(employee.username)

        new_user = User(
            username=employee.username,
            password_hash=hash_password(employee.password),
            role=employee.role,
            is_active=True
        )

        db.add(new_user)
        db.flush()

        user_id = new_user.id

    last_employee = (
        db.query(Employee)
        .order_by(Employee.id.desc())
        .first()
    )

    if last_employee:
        next_number = int(last_employee.employee_code[1:]) + 1
    else:
        next_number = 1

    employee_code = f"E{next_number:05d}"

    new_employee = Employee(
        employee_code=employee_code,
        name=employee.name,
        phone=employee.phone,
        address=employee.address,
        role=employee.role,
        route_id=employee.route_id,
        user_id=user_id
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee


def get_all(
        db: Session
) -> list[Employee]:

    employees = (
        db.query(Employee)
        .filter(
            Employee.is_active == True
        )
        .all()
    )

    return employees


def get_by_id(
        db: Session,
        employee_id: int
) -> Employee:

    employee = (
        db.query(Employee)
        .filter(
            Employee.id == employee_id,
            Employee.is_active == True
        )
        .first()
    )

    if not employee:
        raise EmployeeNotFoundError()

    return employee


def update_by_id(
        db: Session,
        employee_id: int,
        employee: EmployeeUpdate
) -> Employee:

    employee_to_update = (
        db.query(Employee)
        .filter(
            Employee.id == employee_id,
            Employee.is_active == True
        )
        .first()
    )

    if not employee_to_update:
        raise EmployeeNotFoundError()

    if employee.route_id is not None:
        existing_route = (
            db.query(Route)
            .filter(
                Route.id == employee.route_id
            )
            .first()
        )

        if not existing_route:
            raise EmployeeRouteNotFoundError()

        if not existing_route.is_active:
            raise InactiveRouteError()

    if employee.phone is not None:
        existing_phone = (
            db.query(Employee)
            .filter(
                Employee.phone == employee.phone,
                Employee.id != employee_id
            )
            .first()
        )

        if existing_phone:
            raise DuplicateEmployeePhoneError(
                employee.phone
            )

    if employee.name is not None:
        employee_to_update.name = employee.name

    if employee.phone is not None:
        employee_to_update.phone = employee.phone

    if employee.address is not None:
        employee_to_update.address = employee.address

    if employee.role is not None:
        employee_to_update.role = employee.role

    if employee.route_id is not None:
        employee_to_update.route_id = employee.route_id

    db.commit()
    db.refresh(employee_to_update)

    return employee_to_update


def update_credentials(
        db: Session,
        employee_id: int,
        credentials: EmployeeCredentialsUpdate
) -> Employee:

    employee = (
        db.query(Employee)
        .filter(
            Employee.id == employee_id,
            Employee.is_active == True
        )
        .first()
    )

    if not employee:
        raise EmployeeNotFoundError()

    if not employee.user_id:
        raise EmployeeNoLinkedUserError()

    user = (
        db.query(User)
        .filter(
            User.id == employee.user_id,
            User.is_active == True
        )
        .first()
    )

    if not user:
        raise EmployeeUserNotFoundError()

    if credentials.username is not None:
        existing_user = (
            db.query(User)
            .filter(
                User.username == credentials.username,
                User.id != user.id
            )
            .first()
        )

        if existing_user:
            raise DuplicateUsernameError(credentials.username)

        user.username = credentials.username

    if credentials.password is not None:
        user.password_hash = hash_password(credentials.password)

    db.commit()
    db.refresh(employee)

    return employee


def delete_by_id(
        db: Session,
        employee_id: int
) -> Employee:

    employee = (
        db.query(Employee)
        .filter(
            Employee.id == employee_id,
            Employee.is_active == True
        )
        .first()
    )

    if not employee:
        raise EmployeeNotFoundError()

    employee.is_active = False

    db.commit()
    db.refresh(employee)

    return employee
