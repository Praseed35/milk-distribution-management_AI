from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class TokenSheetWarning(Base):
    __tablename__ = "token_sheet_warnings"

    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("daily_deliveries.id"), nullable=False)
    warning_code = Column(String(30), nullable=False)
    warning_message = Column(Text, nullable=False)
    sheet_number = Column(Integer, nullable=False)
    expected_sheet = Column(Integer, nullable=True)
    book_issue_id = Column(Integer, ForeignKey("token_book_issues.id"), nullable=True)
    warning_metadata = Column("metadata", JSONB, nullable=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    delivery = relationship("DailyDelivery", back_populates="warnings")
    book_issue = relationship("TokenBookIssue", back_populates="warnings")
    acknowledged_by_user = relationship("User", foreign_keys=[acknowledged_by])
