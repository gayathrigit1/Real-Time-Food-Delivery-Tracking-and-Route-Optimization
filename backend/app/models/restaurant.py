from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), index=True, nullable=False)
    description = Column(Text, nullable=True)
    cuisine_type = Column(String(100), default="Multi-Cuisine", nullable=False)
    address = Column(String(255), nullable=False)
    node_id = Column(String(50), default="Node_R1", nullable=False)  # Road network node
    latitude = Column(Float, default=12.9716, nullable=False)
    longitude = Column(Float, default=77.5946, nullable=False)
    rating = Column(Float, default=4.5, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    owner = relationship("User", back_populates="restaurant")
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="restaurant", cascade="all, delete-orphan")
