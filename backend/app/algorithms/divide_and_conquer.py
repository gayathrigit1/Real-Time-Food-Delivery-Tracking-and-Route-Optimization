"""
Divide and Conquer: Large-Scale Order Stream Analytics & Recursive Aggregation
-----------------------------------------------------------------------------
Algorithm Type: Divide and Conquer (MergeSort Partitioning & Recursive Statistical Metric Aggregation)
Problem: Process a high-throughput stream of customer order totals, timestamps, and delivery revenues.
         Divide the dataset recursively into halves, conquer sub-analyses, and combine them to derive:
         - Sorted distribution (MergeSort)
         - Total, Minimum, Maximum, Mean, and Exact Median (via Partition / QuickSelect or Merge combination)
         - Top-K Highest Value Orders

Recurrence Relation & Master Theorem:
-------------------------------------
T(N) = 2 * T(N / 2) + O(N)
Applying Master Theorem Case 2:
  a = 2, b = 2, f(N) = O(N)
  log_b(a) = log_2(2) = 1
  => T(N) = Theta(N * log N)

Complexity Analysis:
--------------------
- Time Complexity: O(N log N) deterministic time for full merge and order statistics.
- Space Complexity: O(N) auxiliary space for recursive merging arrays and stack frames (recursion depth: O(log N)).
"""

import time
from typing import Any


class DivideAndConquerAnalytics:
    def __init__(self) -> None:
        self.max_recursion_depth = 0

    def _merge(self, left: list[float], right: list[float]) -> list[float]:
        """Combines two sorted sublists in O(N) linear time."""
        merged: list[float] = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged

    def _divide_and_conquer_sort(self, data: list[float], depth: int = 0) -> list[float]:
        """Recursively divides array and merges results."""
        self.max_recursion_depth = max(self.max_recursion_depth, depth)
        if len(data) <= 1:
            return data

        mid = len(data) // 2
        left_sorted = self._divide_and_conquer_sort(data[:mid], depth + 1)
        right_sorted = self._divide_and_conquer_sort(data[mid:], depth + 1)

        return self._merge(left_sorted, right_sorted)

    def _recursive_aggregate(self, data: list[float], depth: int = 0) -> tuple[float, float, float]:
        """
        Divide and Conquer to find (min_val, max_val, sum_val) in O(N) steps with O(log N) depth.
        """
        if len(data) == 1:
            return data[0], data[0], data[0]
        if len(data) == 2:
            return min(data[0], data[1]), max(data[0], data[1]), data[0] + data[1]

        mid = len(data) // 2
        min_l, max_l, sum_l = self._recursive_aggregate(data[:mid], depth + 1)
        min_r, max_r, sum_r = self._recursive_aggregate(data[mid:], depth + 1)

        # Combine step
        return min(min_l, min_r), max(max_l, max_r), sum_l + sum_r

    def analyze_order_values(self, values: list[float], top_k: int = 5) -> dict[str, Any]:
        """
        Executes Divide and Conquer analytical pipeline on order values.
        """
        start_time = time.perf_counter()
        self.max_recursion_depth = 0

        if not values:
            return {
                "total_orders_analyzed": 0,
                "min_order_value": 0.0,
                "max_order_value": 0.0,
                "total_revenue": 0.0,
                "median_order_value": 0.0,
                "top_k_orders": [],
                "recursion_depth": 0,
                "execution_time_ms": 0.0,
                "theoretical_complexity": "O(N log N)",
            }

        n = len(values)
        min_val, max_val, total_rev = self._recursive_aggregate(values)
        sorted_vals = self._divide_and_conquer_sort(values)

        # Compute median
        if n % 2 == 1:
            median = sorted_vals[n // 2]
        else:
            median = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0

        top_k_orders = sorted_vals[-top_k:][::-1]

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "total_orders_analyzed": n,
            "min_order_value": round(min_val, 2),
            "max_order_value": round(max_val, 2),
            "total_revenue": round(total_rev, 2),
            "median_order_value": round(median, 2),
            "top_k_orders": [round(x, 2) for x in top_k_orders],
            "recursion_depth": self.max_recursion_depth,
            "execution_time_ms": round(elapsed_ms, 4),
            "theoretical_complexity": "O(N log N)",
        }
