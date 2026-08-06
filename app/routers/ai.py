from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.core.roles import require_role
from app.models.user import User
from app.models.milk_type import MilkType
from app.schemas.ai import DemandForecast, AnomalyReport, ChurnRiskReport, AIInsightsResponse, ChatRequest, ChatResponse
from app.services.ai import forecast as forecast_service
from app.services.ai import anomaly as anomaly_service
from app.services.ai import churn as churn_service
from app.services.ai import insights as insights_service
from app.services.ai import chat as chat_service
from app.exceptions.ai import AIRateLimitError, AIUnavailableError
from app.services.reports.cache import report_cache
from app.services.reports.common import resolve_date_range


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


def _cache_key(report_type: str, params: dict) -> str:
    return report_cache._make_key(report_type, params)


@router.get("/forecast", response_model=DemandForecast)
def get_forecast(
    route_id: int | None = Query(default=None),
    milk_type_id: int | None = Query(default=None),
    horizon_days: int = Query(default=7, ge=1, le=30),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["OWNER", "ADMIN"])),
):
    if milk_type_id is not None:
        exists = (
            db.query(MilkType)
            .filter(MilkType.id == milk_type_id, MilkType.is_active == True)
            .first()
        )
        if not exists:
            raise HTTPException(status_code=404, detail="Milk type not found")

    cache_key = _cache_key("ai_forecast", {
        "route_id": route_id or 0,
        "milk_type_id": milk_type_id or 0,
        "horizon_days": horizon_days,
        "user": current_user.id,
    })

    if not refresh:
        cached = report_cache.get(cache_key)
        if cached is not None:
            return cached

    result = forecast_service.forecast_demand(
        db,
        route_id=route_id,
        milk_type_id=milk_type_id,
        horizon_days=horizon_days,
    )
    report_cache.set(cache_key, result, ttl=300)
    return result


@router.get("/churn-risk", response_model=ChurnRiskReport)
def get_churn_risk(
    route_id: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["OWNER", "ADMIN"])),
):
    cache_key = _cache_key("ai_churn_risk", {
        "route_id": route_id or 0,
        "limit": limit,
        "user": current_user.id,
    })

    if not refresh:
        cached = report_cache.get(cache_key)
        if cached is not None:
            return cached

    result = churn_service.get_churn_risk(
        db,
        route_id=route_id,
        limit=limit,
    )
    report_cache.set(cache_key, result, ttl=300)
    return result


@router.get("/insights", response_model=AIInsightsResponse)
def get_insights(
    preset: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["OWNER"])),
):
    frm, to = resolve_date_range(preset, from_date, to_date)

    cache_key = _cache_key("ai_insights", {
        "from": frm,
        "to": to,
        "user": current_user.id,
    })

    if not refresh:
        cached = report_cache.get(cache_key)
        if cached is not None:
            return cached

    result = insights_service.get_insights(
        db,
        preset=preset,
        from_date=from_date,
        to_date=to_date,
    )
    report_cache.set(cache_key, result, ttl=300)
    return result


@router.post("/chat", response_model=ChatResponse)
def post_chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["OWNER"])),
):
    try:
        return chat_service.answer_question(
            db,
            user_id=current_user.id,
            message=body.message,
            history=[{"role": m.role, "content": m.content} for m in body.history],
        )
    except AIRateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except AIUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/anomalies", response_model=AnomalyReport)
def get_anomalies(
    route_id: int | None = Query(default=None),
    days_back: int = Query(default=7, ge=1, le=30),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["OWNER", "ADMIN"])),
):
    cache_key = _cache_key("ai_anomalies", {
        "route_id": route_id or 0,
        "days_back": days_back,
        "user": current_user.id,
    })

    if not refresh:
        cached = report_cache.get(cache_key)
        if cached is not None:
            return cached

    result = anomaly_service.get_anomalies(
        db,
        route_id=route_id,
        days_back=days_back,
    )
    report_cache.set(cache_key, result, ttl=300)
    return result
