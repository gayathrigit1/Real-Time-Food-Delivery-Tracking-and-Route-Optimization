import enum
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(enum.StrEnum):
    CUSTOMER = "CUSTOMER"
    RESTAURANT = "RESTAURANT"
    DELIVERY_AGENT = "DELIVERY_AGENT"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    phone = Column(String(30), nullable=True)
    address = Column(String(255), nullable=True)
    node_id = Column(String(50), default="Node_A", nullable=False)  # Road network node
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    restaurant = relationship("Restaurant", back_populates="owner", uselist=False)
    delivery_profile = relationship("DeliveryAgent", back_populates="user", uselist=False)
