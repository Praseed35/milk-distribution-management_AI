from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class DeliveryException(Base):

    __tablename__ = "delivery_exceptions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id"),
        nullable=False
    )

    exception_type = Column(
        String(20),
        nullable=False
    )

    start_date = Column(
        DateTime(timezone=True),
        nullable=False
    )

    end_date = Column(
        DateTime(timezone=True),
        nullable=True
    )

    reason = Column(
        String(255),
        nullable=True
    )

    status = Column(
        String(20),
        default="ACTIVE",
        nullable=False
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

    subscription = relationship(
        "Subscription",
        back_populates="delivery_exceptions"
    )