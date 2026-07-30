from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict


class ReportEnvelope(BaseModel):
    data: list
    total: int
    page: int
    page_size: int
    generated_at: datetime


class DateRangeFilter(BaseModel):
    preset: str | None = None
    from_date: date | None = None
    to_date: date | None = None
    shift: str | None = None
    group_by: str | None = None


class ReportPagination(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)


class RouteDeliveryItem(BaseModel):
    route_id: int
    route_name: str
    route_code: str
    session_count: int
    delivery_count: int
    total_loaded_quantity: float
    total_delivered_quantity: float
    total_cash_collected: float
    total_token_registered: float
    total_returned_quantity: float
    shortage_surplus: float
    is_balanced: bool
    model_config = ConfigDict(from_attributes=True)


class RouteDeliveryReport(BaseModel):
    route_id: int | None
    date_from: date
    date_to: date
    shift: str | None
    items: list[RouteDeliveryItem]
    summary: RouteDeliveryItem


class RevenueBreakdown(BaseModel):
    source: str
    payment_mode: str | None = None
    route_name: str | None = None
    milk_type_name: str | None = None
    amount: float
    percentage: float
    model_config = ConfigDict(from_attributes=True)


class RevenueReport(BaseModel):
    date_from: date
    date_to: date
    total_revenue: float
    token_book_revenue: float
    customer_bill_revenue: float
    by_source: list[RevenueBreakdown]
    by_payment_mode: list[RevenueBreakdown]
    by_route: list[RevenueBreakdown]
    by_milk_type: list[RevenueBreakdown]


class CustomerCollectionItem(BaseModel):
    customer_id: int
    customer_code: str
    customer_name: str
    route_name: str
    total_billed: float
    total_paid: float
    balance: float
    collection_percentage: float
    last_bill_date: date | None = None
    last_payment_date: date | None = None
    aging_current: float = 0
    aging_31_60: float = 0
    aging_61_90: float = 0
    aging_90_plus: float = 0
    model_config = ConfigDict(from_attributes=True)


class CollectionEfficiencyReport(BaseModel):
    date_from: date
    date_to: date
    route_id: int | None
    total_billed: float
    total_paid: float
    total_balance: float
    overall_collection_percentage: float
    items: list[CustomerCollectionItem]


class ConsumptionDay(BaseModel):
    date: date
    total_quantity: float
    by_milk_type: list[dict]


class ConsumptionTrend(BaseModel):
    period: str
    recent_7day_avg: float | None = None
    preceding_21day_avg: float | None = None
    change_percentage: float | None = None


class CustomerConsumptionReport(BaseModel):
    customer_id: int
    customer_name: str
    date_from: date
    date_to: date
    group_by: str
    total_consumption: float
    average_daily: float
    days_with_data: int
    trend: ConsumptionTrend
    items: list[ConsumptionDay]


class TokenUtilizationItem(BaseModel):
    customer_id: int
    customer_name: str
    route_name: str
    token_number: int
    milk_type_name: str
    total_books_issued: int
    active_books: int
    completed_books: int
    total_sheets_used: int
    total_sheets_remaining: int
    utilization_percentage: float
    books_below_20_percent: int
    model_config = ConfigDict(from_attributes=True)


class TokenUtilizationReport(BaseModel):
    route_id: int | None
    total_customers_with_tokens: int
    total_books_issued: int
    total_sheets_used: int
    total_sheets_remaining: int
    overall_utilization_percentage: float
    items: list[TokenUtilizationItem]


class OperationalDashboard(BaseModel):
    report_date: date
    total_sessions: int
    total_milk_loaded: float
    total_milk_delivered: float
    total_cash_collected: float
    deliveries_by_status: dict
    pending_token_count: int
    unclosed_sessions: int
    unbalanced_sessions: int
    completed_not_closed: int
