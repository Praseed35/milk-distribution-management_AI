from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.sql import func

from app.database import Base
from sqlalchemy.orm import relationship



class Route(Base):

    __tablename__ = "routes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    route_code = Column(
        String,
        unique=True,
        nullable=False
    )

    route_name = Column(
        String,
        unique=True,
        nullable=False
    )

    description = Column(
        String,
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

    customers = relationship(
        "Customer",
        back_populates="route"
    )

    employees = relationship(
        "Employee",
        back_populates="route"
    )