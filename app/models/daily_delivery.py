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
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class DailyDelivery(Base):
    __tablename__ = "daily_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("delivery_sessions.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    milk_type_id = Column(Integer, ForeignKey("milk_types.id"), nullable=False)
    planned_quantity = Column(Integer, nullable=False)
    delivered_quantity = Column(Integer, default=0)
    delivery_status = Column(String(20), nullable=False)
    delivery_source = Column(String(20), nullable=False, default="PLANNED")
    token_sheet_number = Column(Integer, nullable=True)
    token_book_issue_id = Column(Integer, ForeignKey("token_book_issues.id"), nullable=True)
    added_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    added_reason = Column(String(500), nullable=True)
    cash_amount = Column(Numeric(10, 2), nullable=True)
    is_edited = Column(Boolean, default=False)
    last_edited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_edited_at = Column(DateTime(timezone=True), nullable=True)
    shift = Column(String(10), nullable=False)
    delivery_date = Column(Date, nullable=False)
    remarks = Column(String(500), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    session = relationship("DeliverySession", back_populates="deliveries")
    customer = relationship("Customer", back_populates="deliveries")
    milk_type = relationship("MilkType", back_populates="deliveries")
    token_book_issue = relationship("TokenBookIssue", back_populates="deliveries")
    added_by_user = relationship("User", foreign_keys=[added_by])
    last_edited_by_user = relationship("User", foreign_keys=[last_edited_by])
    edits = relationship("SessionEdit", back_populates="delivery")
    warnings = relationship("TokenSheetWarning", back_populates="delivery")
