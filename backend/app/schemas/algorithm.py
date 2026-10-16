from typing import Any

from pydantic import BaseModel


class DijkstraRequest(BaseModel):
    start_node: str = "Node_R1"
    end_node: str = "Node_C1"


class DijkstraResponse(BaseModel):
    start_node: str
    end_node: str
    shortest_path: list[str]
    total_cost_km: float
    nodes_visited_count: int
    execution_time_ms: float
    theoretical_complexity: str = "O((V + E) log V)"


class DPScheduleItem(BaseModel):
    order_id: int
    preparation_time: int
    delivery_deadline: int
    profit_or_priority: int


class DPScheduleRequest(BaseModel):
    max_time_window: int = 120
    orders: list[DPScheduleItem] | None = None


class DPScheduleResponse(BaseModel):
    max_profit_or_priority: int
    selected_orders: list[dict[str, Any]]
    total_time_used: int
    time_window: int
    execution_time_ms: float
    state_table_dimensions: list[int]
    theoretical_complexity: str = "O(N * W) where N=orders, W=time_window"


class BacktrackingRouteRequest(BaseModel):
    delivery_nodes: list[str] = ["Node_C1", "Node_C2", "Node_C3"]
    start_node: str = "Node_R1"
    max_total_distance_km: float = 30.0
    time_windows: dict[str, int] | None = None


class BacktrackingRouteResponse(BaseModel):
    valid_sequences: list[list[str]]
    best_sequence: list[str] | None
    best_distance_km: float | None
    explored_nodes_count: int
    pruned_branches_count: int
    execution_time_ms: float
    theoretical_complexity: str = "O(N!) worst-case, pruned via bounding constraints"


class BranchAndBoundRequest(BaseModel):
    locations: list[str] = ["Node_R1", "Node_C1", "Node_C2", "Node_C3", "Node_C4"]


class BranchAndBoundResponse(BaseModel):
    optimal_tour: list[str]
    minimum_distance_km: float
    nodes_explored: int
    nodes_pruned: int
    execution_time_ms: float
    lower_bound_technique: str = "Reduced Cost Matrix / Minimum Outgoing Edge Sum"
    theoretical_complexity: str = "O(2^N * N^2) worst case, exponential but heavily pruned"


class DivideAndConquerRequest(BaseModel):
    order_values: list[float] | None = None
    sample_size: int = 100


class DivideAndConquerResponse(BaseModel):
    total_orders_analyzed: int
    min_order_value: float
    max_order_value: float
    total_revenue: float
    median_order_value: float
    top_k_orders: list[float]
    recursion_depth: int
    execution_time_ms: float
    theoretical_complexity: str = "O(N log N) for Closest Pair / MergeSort / QuickSelect"


class AlgorithmBenchmarkComparison(BaseModel):
    algorithms: list[dict[str, Any]]
    system_specs: dict[str, Any]
    timestamp: str
