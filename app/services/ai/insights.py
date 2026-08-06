from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.exceptions.ai import AIUnavailableError
from app.services.ai import client as llm_client
from app.services.ai import llm_payload
from app.services.ai import forecast as forecast_service
from app.services.ai import anomaly as anomaly_service
from app.services.ai import churn as churn_service
from app.services.reports import dashboard
from app.services.reports import revenue
from app.services.reports import route_delivery
from app.services.reports.common import resolve_date_range


def get_insights(
    db: Session,
    preset: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> dict:
    frm, to = resolve_date_range(preset, from_date, to_date)

    operational = dashboard.get_operational_dashboard(db)
    revenue_report = revenue.get_revenue_report(db, date_from=frm, date_to=to)
    route_report = route_delivery.get_route_delivery_report(db, date_from=frm, date_to=to)
    forecast = forecast_service.forecast_demand(db)
    anomalies = anomaly_service.get_anomalies(db)
    churn_risk = churn_service.get_churn_risk(db)

    narrative = None
    stats_only = True
    if llm_client.is_available():
        context = {
            "operational": operational,
            "revenue": revenue_report,
            "route_delivery": route_report,
            "forecast": forecast,
            "anomalies": anomalies,
            "churn_risk": churn_risk,
        }
        try:
            messages = llm_payload.build_insights_context(context, (frm, to))
            narrative = llm_client.chat_completion(messages)
            stats_only = False
        except AIUnavailableError:
            narrative = None
            stats_only = True

    return {
        "generated_at": datetime.now(timezone.utc),
        "stats_only": stats_only,
        "data_range": {"from": frm, "to": to},
        "narrative": narrative,
        "operational": operational,
        "forecast": forecast,
        "anomalies": anomalies,
        "churn_risk": churn_risk,
    }
