import threading
import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import AI_CHAT_MAX_REQUESTS_PER_MINUTE, AI_CHAT_MAX_TOKENS
from app.exceptions.ai import AIRateLimitError, AIUnavailableError
from app.services.ai import client as llm_client
from app.services.ai import llm_payload
from app.services.reports import dashboard
from app.services.reports import revenue
from app.services.reports import route_delivery
from app.services.reports import collection
from app.services.reports.common import resolve_date_range


class RateLimiter:
    def __init__(self, max_requests_per_minute: int):
        self.max_requests = max_requests_per_minute
        self._timestamps: dict[int, list[float]] = {}
        self._lock = threading.Lock()

    def check(self, user_id: int) -> None:
        now = time.monotonic()
        with self._lock:
            recent = [t for t in self._timestamps.get(user_id, []) if now - t < 60]
            if len(recent) >= self.max_requests:
                self._timestamps[user_id] = recent
                raise AIRateLimitError()
            recent.append(now)
            self._timestamps[user_id] = recent


rate_limiter = RateLimiter(AI_CHAT_MAX_REQUESTS_PER_MINUTE)

SOURCES = ["revenue", "route_delivery", "collection_efficiency", "operational"]


def answer_question(
    db: Session,
    user_id: int,
    message: str,
    history: list[dict] | None = None,
) -> dict:
    rate_limiter.check(user_id)

    frm, to = resolve_date_range(None, None, None)

    context = {
        "revenue": revenue.get_revenue_report(db, date_from=frm, date_to=to),
        "route_delivery": route_delivery.get_route_delivery_report(db, date_from=frm, date_to=to),
        "collection_efficiency": collection.get_collection_efficiency_report(db, date_from=frm, date_to=to),
        "operational": dashboard.get_operational_dashboard(db),
    }

    if not llm_client.is_available():
        raise AIUnavailableError()

    messages = llm_payload.build_chat_context(
        context,
        (frm, to),
        question=message,
        history=history,
    )
    reply = llm_client.chat_completion(messages, max_tokens=AI_CHAT_MAX_TOKENS)

    return {
        "reply": reply,
        "data_range": {"from": frm, "to": to},
        "sources": SOURCES,
        "stats_only": False,
    }
