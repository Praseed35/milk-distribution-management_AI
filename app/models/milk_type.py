from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class MilkType(Base):

    __tablename__ = "milk_types"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    milk_name = Column(
        String(100),
        unique=True,
        nullable=False
    )

    volume_ml = Column(
        Integer,
        nullable=False
    )

    unit_price = Column(
        Numeric(10, 2),
        default=0,
        nullable=False
    )

    description = Column(
        String(255),
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    deliveries = relationship(
        "DailyDelivery",
        back_populates="milk_type"
    )

    token_book_issues = relationship(
        "TokenBookIssue",
        back_populates="milk_type"
    )

    bill_items = relationship(
        "CustomerBillItem",
        back_populates="milk_type"
    )
