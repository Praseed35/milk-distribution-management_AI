from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Subscription(Base):

    __tablename__ = "subscriptions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    milk_type_id = Column(
        Integer,
        ForeignKey("milk_types.id"),
        nullable=False
    )

    morning_quantity = Column(
        Integer,
        default=0,
        nullable=False
    )

    evening_quantity = Column(
        Integer,
        default=0,
        nullable=False
    )

    status = Column(
        String(20),
        default="ACTIVE",
        nullable=False
    )

    start_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    end_date = Column(
        DateTime(timezone=True),
        nullable=True
    )

    remarks = Column(
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

    customer = relationship(
        "Customer",
        back_populates="subscriptions"
    )

    milk_type = relationship(
        "MilkType"
    )
