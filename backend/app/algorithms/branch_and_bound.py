"""
Branch and Bound: Traveling Salesperson / Delivery Round-Trip Optimization
--------------------------------------------------------------------------
Algorithm Type: Branch and Bound (Best-First Search with Lower Bound Pruning)
Problem: Given a depot/restaurant and a set of delivery customer stops, find the minimal distance tour
         visiting every stop exactly once and returning to the depot.

Lower Bound Formulation:
------------------------
For any partial tour containing visited nodes and unvisited nodes:
  Lower Bound = (Current Accumulated Cost of partial tour)
              + (Minimum outgoing edge from the last visited node to unvisited set)
              + Sum_{u in unvisited} (Minimum outgoing edge from u to any other node)

Pruning Condition:
------------------
If Lower_Bound(Node) >= Current_Upper_Bound (best completed tour found so far),
the entire subtree rooted at Node is pruned without expanding its children.

Computational Complexity:
-------------------------
- Worst-Case Time Complexity: O(2^N * N^2) or O(N!) if no pruning occurs.
- Average/Pruned Complexity: Sub-exponential in typical metric spaces with strong lower bounding.
- Space Complexity: O(N * 2^N) maximum priority queue memory in worst-case state space expansion.
"""

import heapq
import time
from typing import Any


class BranchAndBoundTSP:
    def __init__(self, distance_matrix: dict[tuple[str, str], float] | None = None) -> None:
        self.dist_matrix = distance_matrix or {}

    def get_dist(self, u: str, v: str) -> float:
        if u == v:
            return 0.0
        if (u, v) in self.dist_matrix:
            return self.dist_matrix[(u, v)]
        if (v, u) in self.dist_matrix:
            return self.dist_matrix[(v, u)]
        return 3.0

    def calculate_lower_bound(
        self, current_path: list[str], all_nodes: list[str], current_cost: float
    ) -> float:
        """Computes admissible lower bound using minimal outgoing edges."""
        unvisited = [n for n in all_nodes if n not in current_path]
        if not unvisited:
            # Return cost back to start node
            return current_cost + self.get_dist(current_path[-1], current_path[0])

        lb = current_cost
        last_node = current_path[-1]

        # Minimum edge from last_node to unvisited
        min_to_unvisited = min(self.get_dist(last_node, u) for u in unvisited)
        lb += min_to_unvisited

        # Minimum outgoing edge for each unvisited node
        for u in unvisited:
            other_nodes = [
                v for v in all_nodes if v != u and (v not in current_path or v == current_path[0])
            ]
            if other_nodes:
                lb += min(self.get_dist(u, v) for v in other_nodes)

        return lb

    def solve_tsp(self, locations: list[str]) -> dict[str, Any]:
        """
        Solves the TSP tour using Branch and Bound.
        """
        start_time = time.perf_counter()
        n = len(locations)

        if n <= 1:
            return {
                "optimal_tour": locations + locations if locations else [],
                "minimum_distance_km": 0.0,
                "nodes_explored": 1,
                "nodes_pruned": 0,
                "execution_time_ms": 0.0,
                "lower_bound_technique": "Trivial single node",
                "theoretical_complexity": "O(1)",
            }

        start_node = locations[0]
        initial_lb = self.calculate_lower_bound([start_node], locations, 0.0)

        # Priority Queue stores: (lower_bound, current_cost, path)
        # We also store an entry counter to break ties deterministically
        counter = 0
        pq: list[tuple[float, int, float, list[str]]] = [(initial_lb, counter, 0.0, [start_node])]

        best_cost = float("inf")
        best_tour: list[str] = []
        nodes_explored = 0
        nodes_pruned = 0

        while pq:
            lb, _, curr_cost, path = heapq.heappop(pq)
            nodes_explored += 1

            if lb >= best_cost:
                nodes_pruned += 1
                continue

            last_node = path[-1]

            if len(path) == n:
                # Complete tour by returning to start_node
                total_cost = curr_cost + self.get_dist(last_node, start_node)
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_tour = path + [start_node]
                continue

            for nxt in locations:
                if nxt not in path:
                    edge_cost = self.get_dist(last_node, nxt)
                    new_cost = curr_cost + edge_cost
                    new_path = path + [nxt]
                    child_lb = self.calculate_lower_bound(new_path, locations, new_cost)

                    if child_lb < best_cost:
                        counter += 1
                        heapq.heappush(pq, (child_lb, counter, new_cost, new_path))
                    else:
                        nodes_pruned += 1

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "optimal_tour": best_tour,
            "minimum_distance_km": round(best_cost, 2) if best_cost != float("inf") else 0.0,
            "nodes_explored": nodes_explored,
            "nodes_pruned": nodes_pruned,
            "execution_time_ms": round(elapsed_ms, 4),
            "lower_bound_technique": "Minimum Outgoing Edge Relaxation",
            "theoretical_complexity": "O(2^N * N^2) worst case, exponential but heavily pruned",
        }
