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


class TokenBookPayment(Base):

    __tablename__ = "token_book_payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    token_book_issue_id = Column(
        Integer,
        ForeignKey("token_book_issues.id"),
        nullable=False
    )

    payment_mode = Column(
        String(20),
        nullable=False
    )

    payment_status = Column(
        String(20),
        default="PENDING",
        nullable=False
    )

    book_price = Column(
        Numeric(10, 2),
        nullable=False
    )

    amount_paid = Column(
        Numeric(10, 2),
        default=0,
        nullable=False
    )

    balance_amount = Column(
        Numeric(10, 2),
        default=0,
        nullable=False
    )

    payment_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
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

    token_book_issue = relationship(
        "TokenBookIssue",
        back_populates="payments"
    )

    collector = relationship(
        "User"
    )