from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class TokenIdentity(Base):

    __tablename__ = "token_identities"

    __table_args__ = (
        UniqueConstraint(
            "customer_id",
            "milk_type_id",
            "token_number",
            name="uq_token_identity_customer_milk_type_number"
        ),
    )

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

    token_number = Column(
        Integer,
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

    customer = relationship(
        "Customer"
    )

    milk_type = relationship(
        "MilkType"
    )

    book_issues = relationship(
        "TokenBookIssue",
        back_populates="token_identity"
    )