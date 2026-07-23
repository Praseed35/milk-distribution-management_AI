from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
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
