from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class DataRange(BaseModel):
    from_: date = Field(alias="from")
    to: date

    model_config = ConfigDict(populate_by_name=True)


class ForecastDay(BaseModel):
    date: date
    predicted_quantity: float
    low: float
    high: float
    actual_quantity: float | None = None
    is_sufficient_history: bool


class DemandForecast(BaseModel):
    route_id: int | None = None
    milk_type_id: int | None = None
    horizon_days: int
    date_from: date
    date_to: date
    method: str = "weekday_seasonal_moving_average"
    is_sufficient_history: bool
    message: str | None = None
    total_expected: float | None = None
    low_range: float | None = None
    high_range: float | None = None
    items: list[ForecastDay]


class AnomalyItem(BaseModel):
    type: str
    severity: Literal["HIGH", "MEDIUM", "LOW"]
    title: str
    description: str
    entity_type: Literal["session", "route", "customer", "payment"]
    entity_id: int
    entity_name: str
    metric: str
    expected: float
    actual: float
    deviation: float
    occurred_on: date
    suggested_action: str


class AnomalyReport(BaseModel):
    generated_at: datetime
    count: int
    items: list[AnomalyItem]


class ChurnFactor(BaseModel):
    factor: str
    weight: int
    contribution: int


class ChurnRiskItem(BaseModel):
    customer_id: int
    customer_code: str
    customer_name: str
    route_name: str
    risk_score: int
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    factors: list[ChurnFactor]
    suggested_action: str


class ChurnRiskReport(BaseModel):
    generated_at: datetime
    count: int
    items: list[ChurnRiskItem]


class AIInsightsResponse(BaseModel):
    generated_at: datetime
    stats_only: bool
    data_range: DataRange
    narrative: str | None = None
    operational: dict
    forecast: DemandForecast
    anomalies: AnomalyReport
    churn_risk: ChurnRiskReport


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=8)


class ChatResponse(BaseModel):
    reply: str
    data_range: DataRange
    sources: list[str]
    stats_only: bool = False
