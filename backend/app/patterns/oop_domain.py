"""
Object-Oriented Programming (OOP) Domain Architecture & Design Patterns
-----------------------------------------------------------------------
Demonstrates:
- Abstract Base Classes (ABC) and Interface Contracts
- Encapsulation, Composition, and Polymorphism
- Strategy Pattern for Route Optimization Algorithm Interchangeability
- Domain Entities (Value Objects, Entities, and Aggregates)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.algorithms.dijkstra_routing import DijkstraRouter, RoadGraph


# 1. Domain Entities & Value Objects (Encapsulation)
@dataclass(frozen=True)
class GeoCoordinate:
    latitude: float
    longitude: float
    node_id: str

    def distance_heuristic(self, other: "GeoCoordinate") -> float:
        """Euclidean approximate planar distance for heuristics in km."""
        dlat = (self.latitude - other.latitude) * 111.0
        dlon = (self.longitude - other.longitude) * 85.0
        return round((dlat**2 + dlon**2) ** 0.5, 3)


@dataclass
class DeliveryStop:
    stop_id: str
    location: GeoCoordinate
    recipient_name: str
    estimated_arrival: datetime | None = None
    is_completed: bool = False

    def mark_completed(self) -> None:
        self.is_completed = True


# 2. Strategy Pattern for Route Calculation
class RouteOptimizationStrategy(ABC):
    """Abstract Strategy interface for route computation."""

    @abstractmethod
    def calculate_route(
        self, source_node: str, destination_node: str, graph: RoadGraph
    ) -> dict[str, Any]:
        pass


class DijkstraRoutingStrategy(RouteOptimizationStrategy):
    """Concrete Strategy: Dijkstra Algorithm."""

    def calculate_route(
        self, source_node: str, destination_node: str, graph: RoadGraph
    ) -> dict[str, Any]:
        router = DijkstraRouter(graph)
        result = router.shortest_path(source_node, destination_node)
        result["strategy_name"] = "Dijkstra Shortest Path"
        return result


class DirectDistanceStrategy(RouteOptimizationStrategy):
    """Concrete Strategy: Direct Euclidean Fallback Route."""

    def calculate_route(
        self, source_node: str, destination_node: str, graph: RoadGraph
    ) -> dict[str, Any]:
        meta_src = graph.node_metadata.get(source_node, {})
        meta_dst = graph.node_metadata.get(destination_node, {})
        c1 = GeoCoordinate(
            meta_src.get("latitude", 0.0), meta_src.get("longitude", 0.0), source_node
        )
        c2 = GeoCoordinate(
            meta_dst.get("latitude", 0.0), meta_dst.get("longitude", 0.0), destination_node
        )
        dist = c1.distance_heuristic(c2)
        return {
            "found": True,
            "path": [source_node, destination_node],
            "total_distance_km": dist,
            "estimated_time_mins": round((dist / 25.0) * 60 + 3.0, 1),
            "visited_nodes_count": 2,
            "execution_time_ms": 0.05,
            "strategy_name": "Direct Planar Heuristic",
        }


# 3. Context / Route Service using Strategy (Composition & Polymorphism)
class DeliveryRouteService:
    def __init__(
        self, strategy: RouteOptimizationStrategy | None = None, graph: RoadGraph | None = None
    ) -> None:
        self.strategy = strategy or DijkstraRoutingStrategy()
        self.graph = graph or RoadGraph()

    def set_strategy(self, strategy: RouteOptimizationStrategy) -> None:
        """Switch strategy dynamically at runtime."""
        self.strategy = strategy

    def plan_delivery_route(self, start_node: str, end_node: str) -> dict[str, Any]:
        return self.strategy.calculate_route(start_node, end_node, self.graph)


# 4. Domain Aggregate demonstrating Composition & Business Logic
class OrderDeliveryAggregate:
    def __init__(self, order_id: int, restaurant_node: str, customer_node: str) -> None:
        self.order_id = order_id
        self.restaurant_node = restaurant_node
        self.customer_node = customer_node
        self.assigned_agent_id: int | None = None
        self.status: str = "PENDING"
        self.route_record: dict[str, Any] | None = None
        self.history: list[dict[str, Any]] = []
        self._record_event("ORDER_CREATED", f"Order {order_id} initialized.")

    def assign_agent(
        self, agent_id: int, agent_node: str, route_service: DeliveryRouteService
    ) -> None:
        self.assigned_agent_id = agent_id
        self.status = "ASSIGNED"
        # Calculate multi-leg route: Agent -> Restaurant -> Customer
        leg1 = route_service.plan_delivery_route(agent_node, self.restaurant_node)
        leg2 = route_service.plan_delivery_route(self.restaurant_node, self.customer_node)

        total_path = leg1.get("path", []) + leg2.get("path", [self.customer_node])[1:]
        total_dist = round(
            leg1.get("total_distance_km", 0.0) + leg2.get("total_distance_km", 0.0), 2
        )
        total_time = round(
            leg1.get("estimated_time_mins", 0.0) + leg2.get("estimated_time_mins", 0.0), 1
        )

        self.route_record = {
            "full_path": total_path,
            "total_distance_km": total_dist,
            "estimated_time_mins": total_time,
            "leg1_agent_to_restaurant": leg1,
            "leg2_restaurant_to_customer": leg2,
        }
        self._record_event(
            "AGENT_ASSIGNED", f"Agent {agent_id} assigned. Total distance: {total_dist} km."
        )

    def transition_status(self, new_status: str, notes: str = "") -> None:
        self.status = new_status
        self._record_event(new_status, notes)

    def _record_event(self, action: str, details: str) -> None:
        self.history.append(
            {
                "action": action,
                "timestamp": datetime.now(UTC).isoformat(),
                "details": details,
            }
        )
