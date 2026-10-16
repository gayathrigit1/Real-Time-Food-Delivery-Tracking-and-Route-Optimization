"""
Dijkstra's Shortest Path Algorithm Module
----------------------------------------
Algorithm Type: Graph / Single-Source Shortest Path
Problem: Calculate the optimal shortest delivery route from a source node to a destination node on a road network.

Data Structure:
---------------
- Adjacency List: Dict[str, List[Tuple[str, float]]] representing vertices and directed/undirected weighted edges.
- Min-Heap Priority Queue: Python `heapq` storing tuples of (accumulated_distance, current_node).
- Predecessor Map: Dict[str, Optional[str]] for optimal path reconstruction.
- Distance Map: Dict[str, float] tracking the minimal known distance from source to each vertex.

Complexity:
-----------
- Time Complexity: O((V + E) log V) where V is the number of road intersections (vertices)
  and E is the number of road segments (edges). Each vertex is pushed to and popped from the min-heap at most once
  for valid relaxations, requiring log V per operation.
- Space Complexity: O(V + E) to store the adjacency list representation and predecessor tracking structures.

Optimality:
-----------
Guarantees global shortest distance for all non-negative edge weights (road distances in km).
"""

import heapq
import time
from typing import Any


class RoadGraph:
    def __init__(self) -> None:
        self.adj_list: dict[str, list[tuple[str, float]]] = {}
        self.node_metadata: dict[str, dict[str, Any]] = {}

    def add_node(
        self,
        node_id: str,
        label: str = "",
        node_type: str = "INTERSECTION",
        lat: float = 0.0,
        lon: float = 0.0,
    ) -> None:
        if node_id not in self.adj_list:
            self.adj_list[node_id] = []
            self.node_metadata[node_id] = {
                "label": label or node_id,
                "node_type": node_type,
                "latitude": lat,
                "longitude": lon,
            }

    def add_edge(
        self,
        source: str,
        target: str,
        distance_km: float,
        bidirectional: bool = True,
        traffic_factor: float = 1.0,
    ) -> None:
        effective_weight = round(distance_km * traffic_factor, 3)
        self.add_node(source)
        self.add_node(target)

        self.adj_list[source].append((target, effective_weight))
        if bidirectional:
            self.adj_list[target].append((source, effective_weight))

    def get_nodes(self) -> list[str]:
        return list(self.adj_list.keys())


class DijkstraRouter:
    def __init__(self, graph: RoadGraph | None = None) -> None:
        self.graph = graph or RoadGraph()

    def shortest_path(self, start_node: str, target_node: str) -> dict[str, Any]:
        """
        Executes Dijkstra's algorithm to find the minimum distance path between start_node and target_node.

        :return: Dict with keys: 'found', 'path', 'total_distance_km', 'estimated_time_mins',
                                 'visited_nodes_count', 'execution_time_ms', 'distance_table'
        """
        start_time = time.perf_counter()

        if start_node not in self.graph.adj_list or target_node not in self.graph.adj_list:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return {
                "found": False,
                "path": [],
                "total_distance_km": float("inf"),
                "estimated_time_mins": 0.0,
                "visited_nodes_count": 0,
                "execution_time_ms": round(elapsed_ms, 4),
                "error": f"One or both nodes ('{start_node}', '{target_node}') not in graph.",
            }

        # Priority queue stores (distance, node)
        pq: list[tuple[float, str]] = [(0.0, start_node)]
        distances: dict[str, float] = {node: float("inf") for node in self.graph.adj_list}
        distances[start_node] = 0.0
        predecessors: dict[str, str | None] = {node: None for node in self.graph.adj_list}
        visited: set[str] = set()

        while pq:
            curr_dist, curr_node = heapq.heappop(pq)

            if curr_node in visited:
                continue
            visited.add(curr_node)

            if curr_node == target_node:
                break

            if curr_dist > distances[curr_node]:
                continue

            for neighbor, weight in self.graph.adj_list.get(curr_node, []):
                new_dist = curr_dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = curr_node
                    heapq.heappush(pq, (new_dist, neighbor))

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        if distances[target_node] == float("inf"):
            return {
                "found": False,
                "path": [],
                "total_distance_km": float("inf"),
                "estimated_time_mins": 0.0,
                "visited_nodes_count": len(visited),
                "execution_time_ms": round(elapsed_ms, 4),
                "error": "Destination is unreachable from source node.",
            }

        # Reconstruct path
        path: list[str] = []
        curr: str | None = target_node
        while curr is not None:
            path.append(curr)
            curr = predecessors[curr]
        path.reverse()

        total_distance = round(distances[target_node], 2)
        # Average city delivery speed: 25 km/h -> 2.4 mins per km + 3 mins base buffer
        estimated_time = round((total_distance / 25.0) * 60 + 3.0, 1)

        return {
            "found": True,
            "path": path,
            "total_distance_km": total_distance,
            "estimated_time_mins": estimated_time,
            "visited_nodes_count": len(visited),
            "execution_time_ms": round(elapsed_ms, 4),
            "complexity": "O((V + E) log V)",
        }


def build_default_city_graph() -> RoadGraph:
    """Builds a realistic connected city road network."""
    g = RoadGraph()
    # Intersections & Landmarks
    g.add_node(
        "Node_R1",
        label="Bistro Gourmet (Restaurant 1)",
        node_type="RESTAURANT",
        lat=12.9716,
        lon=77.5946,
    )
    g.add_node(
        "Node_R2",
        label="Spice Garden (Restaurant 2)",
        node_type="RESTAURANT",
        lat=12.9750,
        lon=77.5980,
    )
    g.add_node(
        "Node_R3",
        label="Tokyo Ramen (Restaurant 3)",
        node_type="RESTAURANT",
        lat=12.9800,
        lon=77.6010,
    )

    g.add_node("Node_D1", label="Agent Hub North", node_type="AGENT", lat=12.9850, lon=77.5900)
    g.add_node("Node_D2", label="Agent Hub South", node_type="AGENT", lat=12.9600, lon=77.5900)
    g.add_node("Node_D3", label="Agent Hub East", node_type="AGENT", lat=12.9720, lon=77.6200)

    g.add_node(
        "Node_A", label="North Junction A", node_type="INTERSECTION", lat=12.9820, lon=77.5920
    )
    g.add_node(
        "Node_B", label="Central Square B", node_type="INTERSECTION", lat=12.9730, lon=77.5960
    )
    g.add_node(
        "Node_C", label="South Junction C", node_type="INTERSECTION", lat=12.9650, lon=77.5930
    )
    g.add_node(
        "Node_D", label="East Expressway D", node_type="INTERSECTION", lat=12.9740, lon=77.6080
    )
    g.add_node(
        "Node_E", label="West Ring Road E", node_type="INTERSECTION", lat=12.9700, lon=77.5850
    )

    g.add_node(
        "Node_C1",
        label="Customer Apt 101 (Downtown)",
        node_type="CUSTOMER",
        lat=12.9780,
        lon=77.6050,
    )
    g.add_node(
        "Node_C2",
        label="Customer Villa 202 (Green Park)",
        node_type="CUSTOMER",
        lat=12.9620,
        lon=77.5880,
    )
    g.add_node(
        "Node_C3",
        label="Customer Heights 303 (Tech Park)",
        node_type="CUSTOMER",
        lat=12.9760,
        lon=77.6150,
    )
    g.add_node(
        "Node_C4", label="Customer Residency 404", node_type="CUSTOMER", lat=12.9890, lon=77.6020
    )

    # Road Segments (edges with distances in km)
    edges = [
        ("Node_R1", "Node_B", 1.2),
        ("Node_R1", "Node_E", 2.0),
        ("Node_R2", "Node_B", 0.9),
        ("Node_R2", "Node_D", 1.8),
        ("Node_R3", "Node_A", 1.5),
        ("Node_R3", "Node_D", 2.1),
        ("Node_D1", "Node_A", 1.0),
        ("Node_D1", "Node_E", 2.8),
        ("Node_D2", "Node_C", 1.1),
        ("Node_D2", "Node_E", 2.4),
        ("Node_D3", "Node_D", 1.6),
        ("Node_D3", "Node_C3", 1.4),
        ("Node_A", "Node_B", 2.2),
        ("Node_A", "Node_C4", 1.7),
        ("Node_B", "Node_C", 2.5),
        ("Node_B", "Node_D", 2.0),
        ("Node_C", "Node_C2", 1.3),
        ("Node_D", "Node_C1", 1.5),
        ("Node_D", "Node_C3", 2.3),
        ("Node_C1", "Node_C4", 2.0),
        ("Node_C1", "Node_C3", 1.9),
        ("Node_E", "Node_C", 2.6),
    ]

    for u, v, w in edges:
        g.add_edge(u, v, w)

    return g
