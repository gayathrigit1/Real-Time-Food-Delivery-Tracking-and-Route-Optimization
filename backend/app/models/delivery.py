from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class DeliveryAgent(Base):
    __tablename__ = "delivery_agents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    is_available = Column(Boolean, default=True, nullable=False, index=True)
    current_node = Column(String(50), default="Node_D1", nullable=False)
    vehicle_type = Column(String(50), default="BIKE", nullable=False)  # BIKE, SCOOTER, CAR
    rating = Column(Float, default=4.8, nullable=False)
    current_workload = Column(Integer, default=0, nullable=False)
    max_capacity = Column(Integer, default=4, nullable=False)
    total_deliveries = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="delivery_profile")
    assignments = relationship("DeliveryAssignment", back_populates="agent")


class DeliveryAssignment(Base):
    __tablename__ = "delivery_assignments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(
        Integer, ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    agent_id = Column(Integer, ForeignKey("delivery_agents.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    picked_up_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    algorithm_used = Column(String(50), default="GREEDY_HEURISTIC", nullable=False)
    assignment_score = Column(Float, default=0.0, nullable=False)
    route_path = Column(
        JSON, nullable=True
    )  # List of node IDs e.g. ["Node_D1", "Node_R1", "Node_B", "Node_C1"]
    total_distance = Column(Float, default=0.0, nullable=False)
    estimated_time_mins = Column(Float, default=0.0, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="delivery_assignment", lazy="selectin")
    agent = relationship("DeliveryAgent", back_populates="assignments", lazy="selectin")


class RoadNode(Base):
    __tablename__ = "road_nodes"

    id = Column(String(50), primary_key=True)
    label = Column(String(100), nullable=False)
    node_type = Column(
        String(50), default="INTERSECTION", nullable=False
    )  # RESTAURANT, CUSTOMER, AGENT, INTERSECTION
    latitude = Column(Float, default=0.0, nullable=False)
    longitude = Column(Float, default=0.0, nullable=False)


class RoadEdge(Base):
    __tablename__ = "road_edges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_node = Column(
        String(50), ForeignKey("road_nodes.id", ondelete="CASCADE"), nullable=False
    )
    target_node = Column(
        String(50), ForeignKey("road_nodes.id", ondelete="CASCADE"), nullable=False
    )
    distance_km = Column(Float, nullable=False)
    traffic_factor = Column(Float, default=1.0, nullable=False)  # Multiplier for dynamic traffic
