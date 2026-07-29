from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class CustomerBill(Base):

    __tablename__ = "customer_bills"

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

    bill_date = Column(
        Date,
        server_default=func.current_date(),
        nullable=False
    )

    bill_period_start = Column(
        Date,
        nullable=False
    )

    bill_period_end = Column(
        Date,
        nullable=False
    )

    total_amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    paid_amount = Column(
        Numeric(10, 2),
        default=0,
        nullable=False
    )

    balance_amount = Column(
        Numeric(10, 2),
        default=0,
        nullable=False
    )

    status = Column(
        String(20),
        default="PENDING",
        nullable=False
    )

    due_date = Column(
        Date,
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
        back_populates="bills"
    )

    items = relationship(
        "CustomerBillItem",
        back_populates="bill",
        cascade="all, delete-orphan"
    )

    payments = relationship(
        "CustomerPayment",
        back_populates="bill"
    )


class CustomerBillItem(Base):

    __tablename__ = "customer_bill_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    bill_id = Column(
        Integer,
        ForeignKey("customer_bills.id"),
        nullable=False
    )

    milk_type_id = Column(
        Integer,
        ForeignKey("milk_types.id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    unit_price = Column(
        Numeric(10, 2),
        nullable=False
    )

    amount = Column(
        Numeric(10, 2),
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

    bill = relationship(
        "CustomerBill",
        back_populates="items"
    )

    milk_type = relationship(
        "MilkType"
    )

    @property
    def milk_name(self) -> str:
        return self.milk_type.milk_name if self.milk_type else "Unknown"
