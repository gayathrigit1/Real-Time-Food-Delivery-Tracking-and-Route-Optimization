"""
Greedy Agent Assignment Module
------------------------------
Algorithm Type: Greedy Heuristic
Problem: Select the most suitable delivery agent for an incoming ready-to-pickup order.

Scoring Function Formulation:
-----------------------------
Let:
  - D = distance from agent's current node to restaurant node (in km)
  - W = current active order workload of the agent
  - R = agent quality rating (scale 1.0 to 5.0)
  - C = maximum agent carrying capacity (default 4)

Formula:
  Score = (w_dist * (D / MAX_DIST)) + (w_load * (W / C)) - (w_rating * (R / 5.0))

Where default weights are:
  - w_dist   = 0.50 (proximity is prioritized for fast pickup)
  - w_load   = 0.30 (load balancing prevents overwhelming single agents)
  - w_rating = 0.20 (customer satisfaction reward)

A lower score indicates a higher suitability rank.

Computational Complexity:
-------------------------
- Time Complexity: O(N) where N is the number of active delivery agents.
  A single pass filters eligible agents (is_available == True and current_workload < max_capacity)
  and calculates the candidate score.
- Auxiliary Space Complexity: O(N) to store candidate evaluation records for transparency.

Limitations:
------------
- Local Optima: Greedy choice makes immediate best decision without forecasting upcoming peak orders.
- No Global Regret Minimization: A single agent might be optimal for Order A, but if Order B comes in 10 seconds later,
  assigning them to A might cause a large penalty for B.
"""

from typing import Any


class GreedyAgentSelector:
    def __init__(
        self,
        weight_distance: float = 0.50,
        weight_workload: float = 0.30,
        weight_rating: float = 0.20,
        max_reference_distance_km: float = 25.0,
    ) -> None:
        self.w_dist = weight_distance
        self.w_load = weight_workload
        self.w_rating = weight_rating
        self.max_dist = max(max_reference_distance_km, 1.0)

    def calculate_score(
        self, distance_km: float, current_workload: int, rating: float, max_capacity: int = 4
    ) -> float:
        """Calculate normalized heuristic score. Lower is better."""
        norm_dist = min(distance_km / self.max_dist, 2.0)
        norm_load = min(current_workload / max(max_capacity, 1), 2.0)
        norm_rating = min(max(rating, 1.0) / 5.0, 1.0)

        score = (
            (self.w_dist * norm_dist) + (self.w_load * norm_load) - (self.w_rating * norm_rating)
        )
        return round(score, 4)

    def select_best_agent(
        self,
        restaurant_node: str,
        available_agents: list[dict[str, Any]],
        distance_matrix_lookup: dict[tuple[str, str], float] | None = None,
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
        """
        Evaluate all candidate agents and select the greedily optimal candidate.

        :param restaurant_node: The road node where the restaurant is located
        :param available_agents: List of agent dictionaries with keys 'id', 'current_node', 'current_workload', 'rating', 'max_capacity'
        :param distance_matrix_lookup: Optional precomputed distance dictionary between node pairs
        :return: (Best Agent Dict or None, Detailed list of all evaluated candidate scores)
        """
        if not available_agents:
            return None, []

        evaluated_candidates: list[dict[str, Any]] = []

        for agent in available_agents:
            # Check availability constraint
            workload = agent.get("current_workload", 0)
            capacity = agent.get("max_capacity", 4)
            if not agent.get("is_available", True) or workload >= capacity:
                continue

            agent_node = agent.get("current_node", "Node_D1")

            # Lookup distance or compute heuristic fallback
            if distance_matrix_lookup and (agent_node, restaurant_node) in distance_matrix_lookup:
                dist = distance_matrix_lookup[(agent_node, restaurant_node)]
            elif distance_matrix_lookup and (restaurant_node, agent_node) in distance_matrix_lookup:
                dist = distance_matrix_lookup[(restaurant_node, agent_node)]
            else:
                # Default estimate based on node difference
                dist = 3.5 if agent_node != restaurant_node else 0.5

            rating = agent.get("rating", 4.5)
            score = self.calculate_score(dist, workload, rating, capacity)

            evaluation = {
                "agent_id": agent["id"],
                "user_id": agent.get("user_id"),
                "current_node": agent_node,
                "distance_to_restaurant_km": dist,
                "current_workload": workload,
                "max_capacity": capacity,
                "rating": rating,
                "composite_score": score,
                "agent_raw": agent,
            }
            evaluated_candidates.append(evaluation)

        if not evaluated_candidates:
            return None, []

        # Find candidate with minimum score (O(N) search)
        best_candidate = min(evaluated_candidates, key=lambda c: c["composite_score"])
        return best_candidate, evaluated_candidates
