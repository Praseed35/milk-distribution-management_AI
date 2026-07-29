from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class CustomerPayment(Base):

    __tablename__ = "customer_payments"

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

    payment_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    payment_mode = Column(
        String(20),
        nullable=False
    )

    payment_type = Column(
        String(20),
        nullable=False
    )

    reference_number = Column(
        String(50),
        nullable=True
    )

    bill_id = Column(
        Integer,
        ForeignKey("customer_bills.id"),
        nullable=True
    )

    collected_by = Column(
        Integer,
        ForeignKey("users.id"),
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
        back_populates="payments"
    )

    bill = relationship(
        "CustomerBill",
        back_populates="payments"
    )

    collector = relationship(
        "User"
    )
