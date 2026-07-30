from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class TokenBookIssue(Base):

    __tablename__ = "token_book_issues"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    token_identity_id = Column(
        Integer,
        ForeignKey("token_identities.id"),
        nullable=False
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

    book_number = Column(
        String(50),
        nullable=False
    )

    total_sheets = Column(
        Integer,
        nullable=False
    )

    issue_number = Column(
        Integer,
        nullable=False
    )

    issue_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    completion_date = Column(
        DateTime(timezone=True),
        nullable=True
    )

    current_sheet = Column(
        Integer,
        default=0,
        nullable=False
    )

    status = Column(
        String(20),
        default="WAITING",
        nullable=False
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

    token_identity = relationship(
        "TokenIdentity",
        back_populates="book_issues"
    )

    customer = relationship(
        "Customer",
        back_populates="token_book_issues"
    )

    milk_type = relationship(
        "MilkType",
        back_populates="token_book_issues"
    )

    payments = relationship(
        "TokenBookPayment",
        back_populates="token_book_issue"
    )

    deliveries = relationship(
        "DailyDelivery",
        back_populates="token_book_issue"
    )

    warnings = relationship(
        "TokenSheetWarning",
        back_populates="book_issue"
    )