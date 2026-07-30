from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc

from app.models.token_identity import TokenIdentity
from app.models.token_book_issue import TokenBookIssue
from app.models.customer import Customer
from app.models.route import Route
from app.models.milk_type import MilkType


def get_token_utilization_report(
    db: Session,
    route_id: int | None = None,
    customer_id: int | None = None,
    low_threshold: int = 20,
    restricted_route_id: int | None = None,
) -> list[dict]:
    if restricted_route_id == -1:
        return []

    query = (
        db.query(
            TokenIdentity.id.label("identity_id"),
            TokenIdentity.token_number,
            TokenIdentity.customer_id,
            TokenIdentity.milk_type_id,
            Customer.customer_name,
            Route.route_name,
            Customer.route_id,
            MilkType.milk_name,
        )
        .join(Customer, TokenIdentity.customer_id == Customer.id)
        .join(Route, Customer.route_id == Route.id)
        .join(MilkType, TokenIdentity.milk_type_id == MilkType.id)
        .filter(TokenIdentity.is_active == True)
        .filter(Customer.is_active == True)
        .filter(Route.is_active == True)
        .filter(MilkType.is_active == True)
    )

    if customer_id:
        query = query.filter(Customer.id == customer_id)
    elif route_id:
        query = query.filter(Customer.route_id == route_id)
    elif restricted_route_id is not None:
        query = query.filter(Customer.route_id == restricted_route_id)

    identities = query.all()

    result = []
    total_books_issued = 0
    total_sheets_used = 0
    total_sheets_remaining = 0

    for ident in identities:
        books = (
            db.query(TokenBookIssue)
            .filter(TokenBookIssue.token_identity_id == ident.identity_id)
            .filter(TokenBookIssue.is_active == True)
            .all()
        )

        num_books = len(books)
        active_books = sum(1 for b in books if b.status in ("WAITING", "ACTIVE"))
        completed_books = sum(1 for b in books if b.status == "COMPLETED")
        sheets_used = sum(b.current_sheet or 0 for b in books)
        sheets_remaining = sum((b.total_sheets or 0) - (b.current_sheet or 0) for b in books)
        total = sheets_used + sheets_remaining
        util_pct = round((sheets_used / total * 100) if total else 0, 2)

        below_threshold = sum(1 for b in books if b.total_sheets > 0 and ((b.current_sheet or 0) / b.total_sheets * 100) >= (100 - low_threshold))

        total_books_issued += num_books
        total_sheets_used += sheets_used
        total_sheets_remaining += sheets_remaining

        result.append({
            "customer_id": ident.customer_id,
            "customer_name": ident.customer_name,
            "route_name": ident.route_name,
            "token_number": ident.token_number,
            "milk_type_name": ident.milk_name,
            "total_books_issued": num_books,
            "active_books": active_books,
            "completed_books": completed_books,
            "total_sheets_used": sheets_used,
            "total_sheets_remaining": sheets_remaining,
            "utilization_percentage": util_pct,
            "books_below_20_percent": below_threshold,
        })

    return result
