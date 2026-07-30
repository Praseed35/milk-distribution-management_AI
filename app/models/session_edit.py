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


class SessionEdit(Base):
    __tablename__ = "session_edits"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("delivery_sessions.id"), nullable=False)
    delivery_id = Column(Integer, ForeignKey("daily_deliveries.id"), nullable=True)
    edited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    edit_type = Column(String(30), nullable=False)
    old_value = Column(JSONB, nullable=False)
    new_value = Column(JSONB, nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("DeliverySession", back_populates="edits")
    delivery = relationship("DailyDelivery", back_populates="edits")
    edited_by_user = relationship("User", foreign_keys=[edited_by])
