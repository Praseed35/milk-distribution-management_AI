from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.schemas.token_identity import (
    TokenIdentityCreate,
    TokenIdentityResponse,
    TokenIdentityUpdate,
    TokenIdentityListResponse,
    TokenIdentityDetailResponse
)

from app.schemas.token_book import (
    TokenBookIssueCreate,
    TokenBookIssueResponse,
    TokenBookIssueUpdate,
    TokenBookIssueListResponse,
    TokenBookIssueDetailResponse,
    TokenBookPaymentCreate,
    TokenBookPaymentResponse,
    TokenBookPaymentUpdate,
    TokenBookPaymentListResponse,
    TokenBookPaymentDetailResponse
)

from app.services import token_book_service

from app.exceptions.customer import CustomerNotFoundError
from app.exceptions.milk_type import MilkTypeError

from app.exceptions.token_book import (
    TokenIdentityNotFoundError,
    DuplicateTokenIdentityError,
    TokenBookIssueNotFoundError,
    ActiveBookExistsError,
    DuplicateIssueNumberError,
    TokenBookPaymentNotFoundError,
    InvalidPaymentAmountError
)

router = APIRouter(
    prefix="/token-books",
    tags=["Token Books"]
)


# ─── Token Identity Endpoints ───


@router.post(
    "/identities/",
    response_model=TokenIdentityResponse,
    status_code=201
)
def create_token_identity(
    identity: TokenIdentityCreate,
    db: Session = Depends(get_db)
):

    try:

        return token_book_service.create_identity(
            db,
            identity
        )

    except CustomerNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except MilkTypeError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except DuplicateTokenIdentityError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/identities/",
    response_model=list[TokenIdentityListResponse]
)
def get_all_token_identities(
    db: Session = Depends(get_db)
):
    return token_book_service.get_all_identities(
        db
    )


@router.get(
    "/identities/{identity_id}",
    response_model=TokenIdentityDetailResponse
)
def get_token_identity_by_id(
    identity_id: int,
    db: Session = Depends(get_db)
):
    try:
        return token_book_service.get_identity_by_id(
            db,
            identity_id)
    except TokenIdentityNotFoundError as e:
         raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/identities/customer/{customer_id}",
    response_model=list[TokenIdentityResponse]
)
def get_token_identities_by_customer_id(
    customer_id: int,
    db: Session = Depends(get_db)
):
    try:
        return token_book_service.get_identities_by_customer_id(
            db,
            customer_id
        )
    except CustomerNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put(
    "/identities/{identity_id}",
    response_model=TokenIdentityResponse
)
def update_token_identity(
    identity_id: int,
    identity: TokenIdentityUpdate,
    db: Session = Depends(get_db)
):
    try:
        return token_book_service.update_identity(
            db,
            identity_id,
            identity
        )

    except TokenIdentityNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except DuplicateTokenIdentityError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete(
    "/identities/{identity_id}",
    response_model=TokenIdentityResponse
)
def delete_token_identity(
    identity_id: int,
    db: Session = Depends(get_db)
):
    try:
        return token_book_service.deactivate_identity(
            db,
            identity_id
        )
    except TokenIdentityNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ─── Token Book Issue Endpoints ───


@router.post(
    "/issues/",
    response_model=TokenBookIssueResponse,
    status_code=201
)
def create_token_book_issue(
    issue: TokenBookIssueCreate,
    db: Session = Depends(get_db)
):

    try:

        return token_book_service.create_book_issue(
            db,
            issue
        )

    except TokenIdentityNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except ActiveBookExistsError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except DuplicateIssueNumberError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/issues/",
    response_model=list[TokenBookIssueListResponse]
)
def get_all_token_book_issues(
    db: Session = Depends(get_db)
):
    return token_book_service.get_all_book_issues(
        db
    )


@router.get(
    "/issues/{issue_id}",
    response_model=TokenBookIssueDetailResponse
)
def get_token_book_issue_by_id(
    issue_id: int,
    db: Session = Depends(get_db)
):
    try:
        return token_book_service.get_book_issue_by_id(
            db,
            issue_id)
    except TokenBookIssueNotFoundError as e:
         raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/issues/identity/{identity_id}",
    response_model=list[TokenBookIssueResponse]
)
def get_token_book_issues_by_identity_id(
    identity_id: int,
    db: Session = Depends(get_db)
):
    try:
        return token_book_service.get_book_issues_by_identity_id(
            db,
            identity_id
        )
    except TokenIdentityNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put(
    "/issues/{issue_id}",
    response_model=TokenBookIssueResponse
)
def update_token_book_issue(
    issue_id: int,
    issue: TokenBookIssueUpdate,
    db: Session = Depends(get_db)
):
    try:
        return token_book_service.update_book_issue(
            db,
            issue_id,
            issue
        )

    except TokenBookIssueNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.delete(
    "/issues/{issue_id}",
    response_model=TokenBookIssueResponse
)
def delete_token_book_issue(
    issue_id: int,
    db: Session = Depends(get_db)
):
    try:
        return token_book_service.deactivate_book_issue(
            db,
            issue_id
        )
    except TokenBookIssueNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ─── Token Book Payment Endpoints ───


@router.post(
    "/payments/",
    response_model=TokenBookPaymentResponse,
    status_code=201
)
def create_token_book_payment(
    payment: TokenBookPaymentCreate,
    db: Session = Depends(get_db)
):

    try:

        return token_book_service.create_payment(
            db,
            payment
        )

    except TokenBookIssueNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except InvalidPaymentAmountError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/payments/",
    response_model=list[TokenBookPaymentListResponse]
)
def get_all_token_book_payments(
    db: Session = Depends(get_db)
):
    return token_book_service.get_all_payments(
        db
    )


@router.get(
    "/payments/{payment_id}",
    response_model=TokenBookPaymentDetailResponse
)
def get_token_book_payment_by_id(
    payment_id: int,
    db: Session = Depends(get_db)
):
    try:
        return token_book_service.get_payment_by_id(
            db,
            payment_id)
    except TokenBookPaymentNotFoundError as e:
         raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/payments/issue/{issue_id}",
    response_model=list[TokenBookPaymentResponse]
)
def get_token_book_payments_by_issue_id(
    issue_id: int,
    db: Session = Depends(get_db)
):
    try:
        return token_book_service.get_payments_by_issue_id(
            db,
            issue_id
        )
    except TokenBookIssueNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put(
    "/payments/{payment_id}",
    response_model=TokenBookPaymentResponse
)
def update_token_book_payment(
    payment_id: int,
    payment: TokenBookPaymentUpdate,
    db: Session = Depends(get_db)
):
    try:
        return token_book_service.update_payment(
            db,
            payment_id,
            payment
        )

    except TokenBookPaymentNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.delete(
    "/payments/{payment_id}",
    response_model=TokenBookPaymentResponse
)
def delete_token_book_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    try:
        return token_book_service.deactivate_payment(
            db,
            payment_id
        )
    except TokenBookPaymentNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )