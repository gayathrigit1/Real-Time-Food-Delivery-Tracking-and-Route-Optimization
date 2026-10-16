from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserOut


class DeliveryAgentBase(BaseModel):
    is_available: bool = True
    current_node: str = "Node_D1"
    vehicle_type: str = "BIKE"
    rating: float = 4.8
    current_workload: int = 0
    max_capacity: int = 4


class DeliveryAgentUpdate(BaseModel):
    is_available: bool | None = None
    current_node: str | None = None
    vehicle_type: str | None = None


class DeliveryAgentOut(DeliveryAgentBase):
    id: int
    user_id: int
    total_deliveries: int
    created_at: datetime
    updated_at: datetime
    user: UserOut | None = None

    model_config = ConfigDict(from_attributes=True)


class DeliveryAssignRequest(BaseModel):
    order_id: int
    preferred_algorithm: str = "GREEDY_HEURISTIC"  # or "DIJKSTRA_PROXIMITY"


class DeliveryAssignmentOut(BaseModel):
    id: int
    order_id: int
    agent_id: int
    algorithm_used: str
    assignment_score: float
    route_path: list[str] | None = None
    total_distance: float
    estimated_time_mins: float
    assigned_at: datetime
    picked_up_at: datetime | None = None
    delivered_at: datetime | None = None
    notes: str | None = None
    agent: DeliveryAgentOut | None = None

    model_config = ConfigDict(from_attributes=True)


class RouteResponse(BaseModel):
    order_id: int
    source_node: str
    destination_node: str
    agent_node: str | None = None
    path: list[str]
    distance_km: float
    estimated_time_mins: float
    steps: list[dict[str, Any]]
    graph_visual: dict[str, Any]


class RoadNodeOut(BaseModel):
    id: str
    label: str
    node_type: str
    latitude: float
    longitude: float


class RoadEdgeOut(BaseModel):
    source_node: str
    target_node: str
    distance_km: float
    traffic_factor: float


class RoadGraphData(BaseModel):
    nodes: list[RoadNodeOut]
    edges: list[RoadEdgeOut]
