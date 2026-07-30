from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class DeliverySession(Base):
    __tablename__ = "delivery_sessions"
    __table_args__ = (
        UniqueConstraint("route_id", "delivery_date", "shift", name="uq_session_route_date_shift"),
    )

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    delivery_date = Column(Date, nullable=False)
    shift = Column(String(10), nullable=False)
    delivery_partner_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    status = Column(String(20), nullable=False, default="PLANNED")
    total_milk_loaded = Column(Numeric(10, 2), default=0)
    total_token_registered = Column(Numeric(10, 2), default=0)
    total_cash_sales = Column(Numeric(10, 2), default=0)
    total_returned_milk = Column(Numeric(10, 2), default=0)
    reconciliation_status = Column(String(20), default="PENDING")
    reopened_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reopened_at = Column(DateTime(timezone=True), nullable=True)
    reopen_count = Column(Integer, default=0)
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    route = relationship("Route", back_populates="delivery_sessions")
    delivery_partner = relationship("Employee", back_populates="delivery_sessions")
    reopened_by_user = relationship("User", foreign_keys=[reopened_by])
    deliveries = relationship("DailyDelivery", back_populates="session", cascade="all, delete-orphan")
    edits = relationship("SessionEdit", back_populates="session")
