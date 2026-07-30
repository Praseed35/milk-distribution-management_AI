from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.core.auth import get_current_user
from app.core.roles import require_role
from app.models.user import User

from app.schemas.reports import (
    CollectionEfficiencyReport,
    CustomerCollectionItem,
    CustomerConsumptionReport,
    OperationalDashboard,
    ReportEnvelope,
    RevenueReport,
    RouteDeliveryReport,
    RouteDeliveryItem,
    TokenUtilizationReport,
    TokenUtilizationItem,
    ConsumptionDay,
    ConsumptionTrend,
    RevenueBreakdown,
)

from app.services.reports import route_delivery
from app.services.reports import revenue
from app.services.reports import collection
from app.services.reports import consumption
from app.services.reports import token_utilization
from app.services.reports import dashboard
from app.services.reports.common import resolve_date_range, get_role_restricted_routes, generate_csv_response
from app.services.reports.cache import report_cache

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


def _paginate(items: list, page: int, page_size: int) -> list:
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]


def _envelope(items: list, page: int, page_size: int) -> dict:
    return {
        "data": _paginate(items, page, page_size),
        "total": len(items),
        "page": page,
        "page_size": page_size,
        "generated_at": datetime.now(),
    }


def _csv_or_json(data: list, format: str, filename: str):
    if format == "csv":
        flat = []
        for item in data:
            if isinstance(item, dict):
                flat.append(item)
            else:
                flat.append(item.model_dump())
        return generate_csv_response(flat, filename)
    return None


@router.get("/route-delivery")
def get_route_delivery(
    route_id: int | None = Query(default=None),
    preset: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    shift: str | None = Query(default=None),
    group_by: str | None = Query(default="route"),
    format: str = Query(default="json"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    restricted = get_role_restricted_routes(db, current_user, route_id)
    if restricted == -1:
        raise HTTPException(status_code=403, detail="Access denied")

    date_from, date_to = resolve_date_range(preset, from_date, to_date)
    cache_key = report_cache._make_key("route_delivery", {
        "route_id": route_id or restricted or 0,
        "date_from": str(date_from), "date_to": str(date_to),
        "shift": shift or "", "user": current_user.id,
    })

    if not refresh:
        cached = report_cache.get(cache_key)
        if cached is not None:
            if format == "csv":
                return generate_csv_response(cached, f"route-delivery-report-{date.today()}.csv")
            return _envelope(cached, page, page_size)

    items = route_delivery.get_route_delivery_report(
        db, route_id=route_id, date_from=date_from, date_to=date_to,
        shift=shift, restricted_route_id=restricted,
    )
    report_cache.set(cache_key, items, ttl=60)

    csv_resp = _csv_or_json(items, format, f"route-delivery-report-{date.today()}.csv")
    if csv_resp:
        return csv_resp

    return _envelope(items, page, page_size)


@router.get("/revenue")
def get_revenue(
    preset: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    route_id: int | None = Query(default=None),
    milk_type_id: int | None = Query(default=None),
    payment_mode: str | None = Query(default=None),
    group_by: str = Query(default="source"),
    format: str = Query(default="json"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["OWNER"])),
):
    date_from, date_to = resolve_date_range(preset, from_date, to_date)
    cache_key = report_cache._make_key("revenue", {
        "date_from": str(date_from), "date_to": str(date_to),
        "route_id": route_id or 0, "milk_type_id": milk_type_id or 0,
        "payment_mode": payment_mode or "", "user": current_user.id,
    })

    if not refresh:
        cached = report_cache.get(cache_key)
        if cached is not None:
            if format == "csv":
                flat = []
                for item in cached.get("by_source", []):
                    flat.append(item.model_dump() if not isinstance(item, dict) else item)
                return generate_csv_response(flat, f"revenue-report-{date.today()}.csv")
            return _envelope([], page, page_size)

    report_data = revenue.get_revenue_report(
        db, date_from=date_from, date_to=date_to,
        route_id=route_id, milk_type_id=milk_type_id,
        payment_mode=payment_mode, group_by=group_by,
    )
    report_cache.set(cache_key, report_data, ttl=300)

    if format == "csv":
        flat = []
        for item in report_data.get("by_source", []):
            flat.append(item)
        return generate_csv_response(flat, f"revenue-report-{date.today()}.csv")

    return report_data


@router.get("/collection-efficiency")
def get_collection_efficiency(
    preset: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    route_id: int | None = Query(default=None),
    min_outstanding: float | None = Query(default=None),
    format: str = Query(default="json"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["OWNER", "ADMIN"])),
):
    restricted = get_role_restricted_routes(db, current_user, route_id)
    if restricted == -1:
        raise HTTPException(status_code=403, detail="Access denied")

    date_from, date_to = resolve_date_range(preset, from_date, to_date)
    cache_key = report_cache._make_key("collection", {
        "route_id": route_id or restricted or 0,
        "date_from": str(date_from), "date_to": str(date_to),
        "min_outstanding": str(min_outstanding or 0),
        "user": current_user.id,
    })

    if not refresh:
        cached = report_cache.get(cache_key)
        if cached is not None:
            csv_resp = _csv_or_json(cached, format, f"collection-efficiency-report-{date.today()}.csv")
            if csv_resp:
                return csv_resp
            return _envelope(cached, page, page_size)

    items = collection.get_collection_efficiency_report(
        db, date_from=date_from, date_to=date_to,
        route_id=route_id, min_outstanding=min_outstanding,
        restricted_route_id=restricted,
    )
    report_cache.set(cache_key, items, ttl=60)

    csv_resp = _csv_or_json(items, format, f"collection-efficiency-report-{date.today()}.csv")
    if csv_resp:
        return csv_resp

    return _envelope(items, page, page_size)


@router.get("/customer/{customer_id}/consumption")
def get_customer_consumption(
    customer_id: int,
    preset: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    group_by: str = Query(default="day"),
    format: str = Query(default="json"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["OWNER", "ADMIN", "CHECKER"])),
):
    date_from, date_to = resolve_date_range(preset, from_date, to_date)
    cache_key = report_cache._make_key("consumption", {
        "customer_id": customer_id,
        "date_from": str(date_from), "date_to": str(date_to),
        "group_by": group_by, "user": current_user.id,
    })

    if not refresh:
        cached = report_cache.get(cache_key)
        if cached is not None:
            if format == "csv":
                flat = [{"date": str(i["date"]), "total_quantity": i["total_quantity"]} for i in cached.get("items", [])]
                return generate_csv_response(flat, f"consumption-report-{customer_id}-{date.today()}.csv")
            return cached

    report_data = consumption.get_customer_consumption_report(
        db, customer_id=customer_id, date_from=date_from,
        date_to=date_to, group_by=group_by,
    )
    if report_data is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    report_cache.set(cache_key, report_data, ttl=60)

    if format == "csv":
        flat = [{"date": str(i["date"]), "total_quantity": i["total_quantity"]} for i in report_data.get("items", [])]
        return generate_csv_response(flat, f"consumption-report-{customer_id}-{date.today()}.csv")

    return report_data


@router.get("/token-utilization")
def get_token_utilization(
    route_id: int | None = Query(default=None),
    customer_id: int | None = Query(default=None),
    low_threshold: int = Query(default=20, ge=1, le=100),
    format: str = Query(default="json"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["OWNER", "ADMIN"])),
):
    restricted = get_role_restricted_routes(db, current_user, route_id)
    if restricted == -1:
        raise HTTPException(status_code=403, detail="Access denied")

    cache_key = report_cache._make_key("token_utilization", {
        "route_id": route_id or restricted or 0,
        "customer_id": customer_id or 0,
        "low_threshold": low_threshold,
        "user": current_user.id,
    })

    if not refresh:
        cached = report_cache.get(cache_key)
        if cached is not None:
            csv_resp = _csv_or_json(cached, format, f"token-utilization-report-{date.today()}.csv")
            if csv_resp:
                return csv_resp
            return _envelope(cached, page, page_size)

    items = token_utilization.get_token_utilization_report(
        db, route_id=route_id, customer_id=customer_id,
        low_threshold=low_threshold, restricted_route_id=restricted,
    )
    report_cache.set(cache_key, items, ttl=60)

    csv_resp = _csv_or_json(items, format, f"token-utilization-report-{date.today()}.csv")
    if csv_resp:
        return csv_resp

    return _envelope(items, page, page_size)


@router.get("/dashboard")
def get_dashboard(
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["OWNER", "ADMIN", "CHECKER", "DELIVERY_PARTNER"])),
):
    restricted = get_role_restricted_routes(db, current_user, None)

    if restricted == -1:
        from app.services.reports.dashboard import _empty_dashboard
        from datetime import date as dt_date
        return _empty_dashboard(dt_date.today())

    cache_key = report_cache._make_key("dashboard", {
        "user": current_user.id, "restricted": str(restricted or ""),
    })

    if not refresh:
        cached = report_cache.get(cache_key)
        if cached is not None:
            return cached

    report_data = dashboard.get_operational_dashboard(db, restricted_route_id=restricted)
    report_cache.set(cache_key, report_data, ttl=300)
    return report_data
