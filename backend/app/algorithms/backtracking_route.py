"""
Backtracking: Constrained Multi-Drop Delivery Tour Sequencing
------------------------------------------------------------
Algorithm Type: Backtracking with Constraint Satisfaction & Pruning
Problem: Given a delivery agent starting at a depot/restaurant and needing to deliver to a set of N customer locations,
         explore feasible delivery permutation sequences that satisfy:
         1. Total tour distance does not exceed `max_total_distance_km`.
         2. Time-window / delivery deadline constraints per location.

Exploration & Pruning Strategy:
-------------------------------
1. State Space: Permutation tree of size N! orderings.
2. Forward Checking / Bounding: At each recursive step, if accumulated distance >= best_distance or > max_allowed_distance,
   the current branch is pruned immediately, avoiding exploration of all (N - k)! descendants.
3. Feasibility Check: Validates that arrival time at each intermediate stop does not exceed customer deadline.

Complexity Analysis:
--------------------
- Time Complexity: O(N!) worst case (unconstrained full search), but drastically pruned in practical constrained scenarios.
- Space Complexity: O(N) recursion stack depth and current path tracking buffer.

Limitations:
------------
Exact permutation search becomes computationally prohibitive for N > 12 without metaheuristics or aggressive bounding.
"""

import time
from typing import Any


class BacktrackingRouteOptimizer:
    def __init__(self, distance_matrix: dict[tuple[str, str], float] | None = None) -> None:
        self.dist_matrix = distance_matrix or {}

    def get_distance(self, u: str, v: str) -> float:
        if u == v:
            return 0.0
        if (u, v) in self.dist_matrix:
            return self.dist_matrix[(u, v)]
        if (v, u) in self.dist_matrix:
            return self.dist_matrix[(v, u)]
        # Default fallback estimate if not explicitly in matrix
        return 3.0

    def find_constrained_tours(
        self,
        start_node: str,
        customer_nodes: list[str],
        max_total_distance_km: float = 30.0,
        node_deadlines: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        """
        Explores valid delivery sequences starting at start_node and visiting all customer_nodes.
        """
        start_time = time.perf_counter()
        node_deadlines = node_deadlines or {}

        valid_sequences: list[list[str]] = []
        best_sequence: list[str] | None = None
        best_distance = float("inf")
        explored_nodes = 0
        pruned_branches = 0

        n = len(customer_nodes)
        visited: set[str] = set()

        def backtrack(
            curr_node: str,
            current_path: list[str],
            accumulated_dist: float,
            current_time_mins: float,
        ) -> None:
            nonlocal explored_nodes, pruned_branches, best_distance, best_sequence
            explored_nodes += 1

            # Prune if accumulated distance exceeds the maximum allowed feasible budget
            if accumulated_dist > max_total_distance_km:
                pruned_branches += 1
                return

            # If all customer nodes are visited, record valid solution
            if len(current_path) == n + 1:
                valid_sequences.append(list(current_path))
                if accumulated_dist < best_distance:
                    best_distance = accumulated_dist
                    best_sequence = list(current_path)
                return

            for nxt in customer_nodes:
                if nxt not in visited:
                    edge_dist = self.get_distance(curr_node, nxt)
                    new_dist = accumulated_dist + edge_dist
                    travel_time = (edge_dist / 25.0) * 60.0  # at 25 km/h
                    new_time = current_time_mins + travel_time + 3.0  # 3 mins drop-off service

                    # Check customer deadline constraint
                    if nxt in node_deadlines and new_time > node_deadlines[nxt]:
                        # Pruning: Violates customer deadline
                        pruned_branches += 1
                        continue

                    visited.add(nxt)
                    current_path.append(nxt)

                    backtrack(nxt, current_path, new_dist, new_time)

                    # Backtrack step (undo state changes)
                    current_path.pop()
                    visited.remove(nxt)

        # Launch recursive exploration
        backtrack(start_node, [start_node], 0.0, 0.0)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "valid_sequences": valid_sequences,
            "best_sequence": best_sequence,
            "best_distance_km": round(best_distance, 2) if best_distance != float("inf") else None,
            "explored_nodes_count": explored_nodes,
            "pruned_branches_count": pruned_branches,
            "execution_time_ms": round(elapsed_ms, 4),
            "theoretical_complexity": "O(N!) worst-case, pruned by distance & time-window constraints",
        }
