"""
Reproducible Benchmark Script: All 6 Core Optimization Algorithms
-----------------------------------------------------------------
Executes empirical benchmarks across all 6 implemented algorithms on the current host machine.
Outputs precise execution times, input sizes, theoretical complexities, and correctness validation summaries.
"""
import platform
import random
import sys
import time
from pathlib import Path
from typing import Any

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.algorithms.backtracking_route import BacktrackingRouteOptimizer  # noqa: E402
from app.algorithms.branch_and_bound import BranchAndBoundTSP  # noqa: E402
from app.algorithms.dijkstra_routing import DijkstraRouter, build_default_city_graph  # noqa: E402
from app.algorithms.divide_and_conquer import DivideAndConquerAnalytics  # noqa: E402
from app.algorithms.dynamic_programming import OrderSelectionDP  # noqa: E402
from app.algorithms.greedy_assignment import GreedyAgentSelector  # noqa: E402

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))



def run_all_algorithm_benchmarks() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    print("\n" + "=" * 80)
    print("  FOOD DELIVERY SYSTEM — ALGORITHM PERFORMANCE BENCHMARK")
    print(f"  System: {platform.system()} {platform.release()} | Python: {platform.python_version()}")
    print("=" * 80 + "\n")

    # 1. Greedy Agent Assignment
    greedy = GreedyAgentSelector(weight_distance=0.5, weight_workload=0.3, weight_rating=0.2)
    agents = [
        {
            "id": i,
            "current_node": f"Node_D{i % 3 + 1}",
            "current_workload": i % 3,
            "max_capacity": 4,
            "rating": round(4.0 + (i % 10) * 0.1, 1),
            "is_available": True,
        }
        for i in range(1, 100)
    ]
    t0 = time.perf_counter()
    best_ag, candidates = greedy.select_best_agent("Node_R1", agents)
    t_greedy = (time.perf_counter() - t0) * 1000
    records.append({
        "Algorithm": "1. Greedy Agent Assignment",
        "Type": "Heuristic Selection",
        "Input Size": f"N = {len(agents)} agents",
        "Time Complexity": "O(N)",
        "Space Complexity": "O(N)",
        "Measured Time (ms)": f"{t_greedy:.4f}",
        "Correctness Summary": f"Selected Agent #{best_ag['agent_id'] if best_ag else None} (Score: {best_ag['composite_score'] if best_ag else None})",
    })

    # 2. Dijkstra Shortest Path
    graph = build_default_city_graph()
    router = DijkstraRouter(graph)
    t0 = time.perf_counter()
    dijk_res = router.shortest_path("Node_R1", "Node_C3")
    t_dijk = (time.perf_counter() - t0) * 1000
    records.append({
        "Algorithm": "2. Dijkstra Shortest Path",
        "Type": "Graph Optimization",
        "Input Size": f"V = {len(graph.adj_list)}, E = 22",
        "Time Complexity": "O((V + E) log V)",
        "Space Complexity": "O(V + E)",
        "Measured Time (ms)": f"{t_dijk:.4f}",
        "Correctness Summary": f"Path: {'->'.join(dijk_res['path'])}, Dist: {dijk_res['total_distance_km']} km",
    })

    # 3. Dynamic Programming 0/1 Knapsack
    dp = OrderSelectionDP(max_time_window_mins=120)
    orders = [
        {"order_id": i, "preparation_time": 10 + (i % 25), "profit_or_priority": 20 + (i * 4)}
        for i in range(1, 30)
    ]
    t0 = time.perf_counter()
    dp_res = dp.optimize_batch(orders, time_window=120)
    t_dp = (time.perf_counter() - t0) * 1000
    records.append({
        "Algorithm": "3. Dynamic Programming",
        "Type": "0/1 Knapsack Batch Selection",
        "Input Size": f"N = {len(orders)}, W = 120",
        "Time Complexity": "O(N * W)",
        "Space Complexity": "O(N * W)",
        "Measured Time (ms)": f"{t_dp:.4f}",
        "Correctness Summary": f"Max Priority: {dp_res['max_profit_or_priority']}, Orders: {len(dp_res['selected_orders'])}, Time: {dp_res['total_time_used']}m",
    })

    # 4. Backtracking Route Permutation
    nodes = ["Node_R1", "Node_C1", "Node_C2", "Node_C3", "Node_C4"]
    dist_matrix = {}
    for u in nodes:
        for v in nodes:
            dist_matrix[(u, v)] = router.shortest_path(u, v).get("total_distance_km", 3.0)
    bt = BacktrackingRouteOptimizer(dist_matrix)
    t0 = time.perf_counter()
    bt_res = bt.find_constrained_tours("Node_R1", ["Node_C1", "Node_C2", "Node_C3", "Node_C4"], 40.0)
    t_bt = (time.perf_counter() - t0) * 1000
    records.append({
        "Algorithm": "4. Backtracking",
        "Type": "Constrained Permutations",
        "Input Size": "4 dropoffs (4! = 24 permutations)",
        "Time Complexity": "O(N!) worst-case",
        "Space Complexity": "O(N)",
        "Measured Time (ms)": f"{t_bt:.4f}",
        "Correctness Summary": f"Valid Tours: {len(bt_res['valid_sequences'])}, Best: {bt_res['best_distance_km']} km (Pruned: {bt_res['pruned_branches_count']})",
    })

    # 5. Branch and Bound TSP
    bb_nodes = ["Node_R1", "Node_C1", "Node_C2", "Node_C3", "Node_C4"]
    bb = BranchAndBoundTSP(dist_matrix)
    t0 = time.perf_counter()
    bb_res = bb.solve_tsp(bb_nodes)
    t_bb = (time.perf_counter() - t0) * 1000
    records.append({
        "Algorithm": "5. Branch & Bound TSP",
        "Type": "State-Space Search + Pruning",
        "Input Size": "5 locations round-trip",
        "Time Complexity": "O(2^N * N^2) worst-case",
        "Space Complexity": "O(N * 2^N)",
        "Measured Time (ms)": f"{t_bb:.4f}",
        "Correctness Summary": f"Min Tour: {bb_res['minimum_distance_km']} km (Explored: {bb_res['nodes_explored']}, Pruned: {bb_res['nodes_pruned']})",
    })

    # 6. Divide and Conquer
    dac = DivideAndConquerAnalytics()
    random.seed(42)
    stream_vals = [round(random.uniform(10.0, 300.0), 2) for _ in range(1000)]
    t0 = time.perf_counter()
    dac_res = dac.analyze_order_values(stream_vals)
    t_dac = (time.perf_counter() - t0) * 1000
    records.append({
        "Algorithm": "6. Divide and Conquer",
        "Type": "MergeSort & Recursive Partition",
        "Input Size": f"N = {len(stream_vals)} stream records",
        "Time Complexity": "O(N log N)",
        "Space Complexity": "O(N)",
        "Measured Time (ms)": f"{t_dac:.4f}",
        "Correctness Summary": f"Rev: ${dac_res['total_revenue']}, Median: ${dac_res['median_order_value']}, Tree Depth: {dac_res['recursion_depth']}",
    })

    # Print Table
    header = f"{'Algorithm':<32} | {'Input Size':<22} | {'Time Comp':<16} | {'Measured (ms)':<14} | {'Output Summary'}"
    print(header)
    print("-" * len(header))
    for r in records:
        print(f"{r['Algorithm']:<32} | {r['Input Size']:<22} | {r['Time Complexity']:<16} | {r['Measured Time (ms)']:<14} | {r['Correctness Summary']}")
    print("-" * len(header))
    print("\nBenchmark completed successfully!\n")

    return records


if __name__ == "__main__":
    run_all_algorithm_benchmarks()
