"""
Dynamic Programming: Delivery Shift Order Batch Selection
---------------------------------------------------------
Algorithm Type: Dynamic Programming (0/1 Knapsack Formulation for Order Selection)
Problem: Given a delivery agent's remaining work shift or bike thermal box capacity / time window W,
         and a candidate set of N incoming orders (each with preparation+delivery time cost c_i and priority/profit p_i),
         select the optimal subset of orders that maximizes total utility/priority without exceeding W.

Theoretical Properties:
-----------------------
1. Optimal Substructure: An optimal solution to a subproblem of capacity `t` containing `i` orders consists of optimal
   solutions to smaller subproblems with `i-1` orders and capacities `t` or `t - c_i`.
2. Overlapping Subproblems: Multiple decision paths evaluate the exact same sub-capacities. Memoization / DP table
   avoids exponential recomputation.

State Definition:
-----------------
Let `dp[i][t]` denote the maximum achievable order priority considering a subset of the first `i` orders
with an available time window / capacity budget of `t` units.

Recurrence Relation:
--------------------
For i = 1 to N, and t = 0 to W:
  If c[i-1] <= t:
    dp[i][t] = max(dp[i-1][t], dp[i-1][t - c[i-1]] + p[i-1])
  Else:
    dp[i][t] = dp[i-1][t]

Base Cases:
-----------
dp[0][t] = 0 for all t in [0, W]
dp[i][0] = 0 for all i in [0, N]

Complexity Analysis:
--------------------
- Time Complexity: O(N * W) where N is number of candidate orders and W is the max time/capacity budget.
- Space Complexity: O(N * W) for the 2D DP matrix (enabling optimal item subset recovery),
  or O(W) if space-optimized when only max value is required.
- Pseudo-polynomial Complexity: The runtime is polynomial in the magnitude of W, not the number of bits.

Limitations:
------------
Requires discrete integer capacities / time quantizations. Cannot handle continuous non-linear cost interactions without discretization.
"""

import time
from typing import Any


class OrderSelectionDP:
    def __init__(self, max_time_window_mins: int = 120) -> None:
        self.max_time_window = max(1, max_time_window_mins)

    def optimize_batch(
        self,
        orders: list[dict[str, Any]],
        time_window: int = 120,
    ) -> dict[str, Any]:
        """
        Solves the 0/1 Knapsack delivery order batch selection problem using Dynamic Programming.

        :param orders: List of dicts, each having 'order_id', 'preparation_time' (mins), 'delivery_deadline' / 'profit_or_priority'
        :param time_window: Total allowed time/capacity budget (integer minutes)
        :return: Dict containing max_profit, selected_orders, time_used, dp_table dimensions, and runtime.
        """
        start_time = time.perf_counter()

        W = max(1, time_window)
        N = len(orders)

        if N == 0:
            return {
                "max_profit_or_priority": 0,
                "selected_orders": [],
                "total_time_used": 0,
                "time_window": W,
                "execution_time_ms": 0.0,
                "state_table_dimensions": [0, W + 1],
                "theoretical_complexity": "O(N * W)",
            }

        # Extract costs (c) and values (p)
        costs: list[int] = []
        values: list[int] = []
        for o in orders:
            c = max(1, int(o.get("preparation_time", 15)))
            p = max(1, int(o.get("profit_or_priority", 10)))
            costs.append(c)
            values.append(p)

        # Initialize DP table (N + 1) x (W + 1)
        dp = [[0 for _ in range(W + 1)] for _ in range(N + 1)]

        # Fill table bottom-up
        for i in range(1, N + 1):
            cost_i = costs[i - 1]
            val_i = values[i - 1]
            for t in range(W + 1):
                if cost_i <= t:
                    dp[i][t] = max(dp[i - 1][t], dp[i - 1][t - cost_i] + val_i)
                else:
                    dp[i][t] = dp[i - 1][t]

        max_profit = dp[N][W]

        # Backtracking on DP table to identify selected items
        selected_indices: list[int] = []
        curr_w = W
        for i in range(N, 0, -1):
            if dp[i][curr_w] != dp[i - 1][curr_w]:
                selected_indices.append(i - 1)
                curr_w -= costs[i - 1]

        selected_indices.reverse()
        selected_orders = [orders[idx] for idx in selected_indices]
        total_time_used = sum(costs[idx] for idx in selected_indices)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "max_profit_or_priority": max_profit,
            "selected_orders": selected_orders,
            "total_time_used": total_time_used,
            "time_window": W,
            "execution_time_ms": round(elapsed_ms, 4),
            "state_table_dimensions": [N + 1, W + 1],
            "theoretical_complexity": "O(N * W)",
        }
