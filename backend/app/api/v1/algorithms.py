import platform
import random
import time
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter

from app.algorithms.backtracking_route import BacktrackingRouteOptimizer
from app.algorithms.branch_and_bound import BranchAndBoundTSP
from app.algorithms.dijkstra_routing import DijkstraRouter, build_default_city_graph
from app.algorithms.divide_and_conquer import DivideAndConquerAnalytics
from app.algorithms.dynamic_programming import OrderSelectionDP
from app.algorithms.greedy_assignment import GreedyAgentSelector
from app.schemas.algorithm import (
    AlgorithmBenchmarkComparison,
    BacktrackingRouteRequest,
    BacktrackingRouteResponse,
    BranchAndBoundRequest,
    BranchAndBoundResponse,
    DijkstraRequest,
    DijkstraResponse,
    DivideAndConquerRequest,
    DivideAndConquerResponse,
    DPScheduleRequest,
    DPScheduleResponse,
)

router = APIRouter(prefix="/algorithms", tags=["Algorithms & Optimization"])


@router.post("/dijkstra", response_model=DijkstraResponse)
async def run_dijkstra_endpoint(req: DijkstraRequest):
    """Calculates shortest path using Dijkstra's algorithm with Min-Heap Priority Queue."""
    graph = build_default_city_graph()
    router_inst = DijkstraRouter(graph)
    res = router_inst.shortest_path(req.start_node, req.end_node)

    return DijkstraResponse(
        start_node=req.start_node,
        end_node=req.end_node,
        shortest_path=res.get("path", []),
        total_cost_km=res.get("total_distance_km", 0.0),
        nodes_visited_count=res.get("visited_nodes_count", 0),
        execution_time_ms=res.get("execution_time_ms", 0.0),
        theoretical_complexity="O((V + E) log V)",
    )


@router.post("/dp-schedule", response_model=DPScheduleResponse)
async def run_dp_schedule_endpoint(req: DPScheduleRequest):
    """Executes 0/1 Knapsack Dynamic Programming for order selection."""
    orders = (
        [o.model_dump() for o in req.orders]
        if req.orders
        else [
            {"order_id": 101, "preparation_time": 25, "profit_or_priority": 50},
            {"order_id": 102, "preparation_time": 20, "profit_or_priority": 40},
            {"order_id": 103, "preparation_time": 30, "profit_or_priority": 70},
            {"order_id": 104, "preparation_time": 15, "profit_or_priority": 30},
            {"order_id": 105, "preparation_time": 45, "profit_or_priority": 90},
            {"order_id": 106, "preparation_time": 10, "profit_or_priority": 25},
        ]
    )

    dp_solver = OrderSelectionDP(req.max_time_window)
    res = dp_solver.optimize_batch(orders, req.max_time_window)
    return DPScheduleResponse(**res)


@router.post("/backtracking-route", response_model=BacktrackingRouteResponse)
async def run_backtracking_endpoint(req: BacktrackingRouteRequest):
    """Executes Backtracking with constraint checks and bounding."""
    # Build distance matrix from city graph
    graph = build_default_city_graph()
    router_inst = DijkstraRouter(graph)
    all_nodes = list(set([req.start_node] + req.delivery_nodes))
    dist_matrix = {}
    for u in all_nodes:
        for v in all_nodes:
            if u != v:
                sp = router_inst.shortest_path(u, v)
                dist_matrix[(u, v)] = sp.get("total_distance_km", 3.0)

    bt_optimizer = BacktrackingRouteOptimizer(dist_matrix)
    res = bt_optimizer.find_constrained_tours(
        req.start_node,
        req.delivery_nodes,
        req.max_total_distance_km,
        req.time_windows,
    )
    return BacktrackingRouteResponse(**res)


@router.post("/branch-and-bound", response_model=BranchAndBoundResponse)
async def run_branch_and_bound_endpoint(req: BranchAndBoundRequest):
    """Executes Branch and Bound TSP route optimization."""
    graph = build_default_city_graph()
    router_inst = DijkstraRouter(graph)
    dist_matrix = {}
    for u in req.locations:
        for v in req.locations:
            if u != v:
                sp = router_inst.shortest_path(u, v)
                dist_matrix[(u, v)] = sp.get("total_distance_km", 3.0)

    bb_solver = BranchAndBoundTSP(dist_matrix)
    res = bb_solver.solve_tsp(req.locations)
    return BranchAndBoundResponse(**res)


@router.post("/divide-and-conquer", response_model=DivideAndConquerResponse)
async def run_divide_and_conquer_endpoint(req: DivideAndConquerRequest):
    """Executes Divide and Conquer analytical pipeline."""
    if req.order_values:
        vals = req.order_values
    else:
        random.seed(42)
        vals = [round(random.uniform(15.0, 150.0), 2) for _ in range(req.sample_size)]

    dac = DivideAndConquerAnalytics()
    res = dac.analyze_order_values(vals)
    return DivideAndConquerResponse(**res)


@router.get("/benchmark-all", response_model=AlgorithmBenchmarkComparison)
async def benchmark_all_algorithms():
    """Runs a live reproducible benchmark across all 6 implemented algorithms."""
    benchmarks: list[dict[str, Any]] = []

    # 1. Greedy Assignment
    greedy = GreedyAgentSelector()
    sample_agents = [
        {
            "id": i,
            "user_id": i,
            "current_node": f"Node_D{i % 3 + 1}",
            "current_workload": i % 3,
            "max_capacity": 4,
            "rating": 4.0 + (i % 10) * 0.1,
            "is_available": True,
        }
        for i in range(1, 50)
    ]
    t0 = time.perf_counter()
    best_ag, _ = greedy.select_best_agent("Node_R1", sample_agents)
    t_greedy = (time.perf_counter() - t0) * 1000
    benchmarks.append(
        {
            "algorithm": "1. Greedy Agent Assignment",
            "category": "Heuristic Selection",
            "input_size": f"{len(sample_agents)} candidate agents",
            "time_complexity": "O(N)",
            "space_complexity": "O(N)",
            "execution_time_ms": round(t_greedy, 4),
            "result_summary": f"Selected Agent #{best_ag['agent_id'] if best_ag else None} (Score: {best_ag['composite_score'] if best_ag else None})",
        }
    )

    # 2. Dijkstra Shortest Path
    graph = build_default_city_graph()
    router_inst = DijkstraRouter(graph)
    t0 = time.perf_counter()
    dijk_res = router_inst.shortest_path("Node_R1", "Node_C3")
    t_dijk = (time.perf_counter() - t0) * 1000
    benchmarks.append(
        {
            "algorithm": "2. Dijkstra Shortest Path",
            "category": "Graph Optimization",
            "input_size": f"{len(graph.adj_list)} nodes, 22 edges",
            "time_complexity": "O((V + E) log V)",
            "space_complexity": "O(V + E)",
            "execution_time_ms": round(t_dijk, 4),
            "result_summary": f"Path: {' -> '.join(dijk_res['path'])}, Distance: {dijk_res['total_distance_km']} km",
        }
    )

    # 3. Dynamic Programming
    dp_solver = OrderSelectionDP(120)
    dp_sample = [
        {"order_id": i, "preparation_time": 10 + (i % 20), "profit_or_priority": 15 + (i * 3)}
        for i in range(1, 20)
    ]
    t0 = time.perf_counter()
    dp_res = dp_solver.optimize_batch(dp_sample, 120)
    t_dp = (time.perf_counter() - t0) * 1000
    benchmarks.append(
        {
            "algorithm": "3. Dynamic Programming (Order Selection)",
            "category": "0/1 Knapsack Optimization",
            "input_size": "20 orders, W=120 mins budget",
            "time_complexity": "O(N * W)",
            "space_complexity": "O(N * W)",
            "execution_time_ms": round(t_dp, 4),
            "result_summary": f"Max Priority: {dp_res['max_profit_or_priority']}, Selected {len(dp_res['selected_orders'])} orders",
        }
    )

    # 4. Backtracking
    bt_matrix = {}
    nodes = ["Node_R1", "Node_C1", "Node_C2", "Node_C3"]
    for u in nodes:
        for v in nodes:
            bt_matrix[(u, v)] = router_inst.shortest_path(u, v).get("total_distance_km", 3.0)
    bt = BacktrackingRouteOptimizer(bt_matrix)
    t0 = time.perf_counter()
    bt_res = bt.find_constrained_tours("Node_R1", ["Node_C1", "Node_C2", "Node_C3"], 35.0)
    t_bt = (time.perf_counter() - t0) * 1000
    benchmarks.append(
        {
            "algorithm": "4. Backtracking Route Sequencing",
            "category": "Constraint Satisfaction",
            "input_size": "3 customer dropoffs (3! permutations)",
            "time_complexity": "O(N!) worst-case",
            "space_complexity": "O(N)",
            "execution_time_ms": round(t_bt, 4),
            "result_summary": f"Found {len(bt_res['valid_sequences'])} valid tours, Best Dist: {bt_res['best_distance_km']} km (Pruned: {bt_res['pruned_branches_count']})",
        }
    )

    # 5. Branch and Bound
    bb_nodes = ["Node_R1", "Node_C1", "Node_C2", "Node_C3", "Node_C4"]
    bb_matrix = {}
    for u in bb_nodes:
        for v in bb_nodes:
            bb_matrix[(u, v)] = router_inst.shortest_path(u, v).get("total_distance_km", 3.0)
    bb = BranchAndBoundTSP(bb_matrix)
    t0 = time.perf_counter()
    bb_res = bb.solve_tsp(bb_nodes)
    t_bb = (time.perf_counter() - t0) * 1000
    benchmarks.append(
        {
            "algorithm": "5. Branch and Bound TSP",
            "category": "State-Space Search with Pruning",
            "input_size": "5 locations (TSP round-trip)",
            "time_complexity": "O(2^N * N^2) worst-case",
            "space_complexity": "O(N * 2^N)",
            "execution_time_ms": round(t_bb, 4),
            "result_summary": f"Min Tour Dist: {bb_res['minimum_distance_km']} km, Nodes Explored: {bb_res['nodes_explored']}, Pruned: {bb_res['nodes_pruned']}",
        }
    )

    # 6. Divide and Conquer
    dac = DivideAndConquerAnalytics()
    dac_sample = [round(random.uniform(10.0, 200.0), 2) for _ in range(500)]
    t0 = time.perf_counter()
    dac_res = dac.analyze_order_values(dac_sample)
    t_dac = (time.perf_counter() - t0) * 1000
    benchmarks.append(
        {
            "algorithm": "6. Divide and Conquer Order Analytics",
            "category": "MergeSort & Recursive Partitioning",
            "input_size": "500 stream order records",
            "time_complexity": "O(N log N)",
            "space_complexity": "O(N)",
            "execution_time_ms": round(t_dac, 4),
            "result_summary": f"Total Rev: ${dac_res['total_revenue']}, Median: ${dac_res['median_order_value']}, Recursion Depth: {dac_res['recursion_depth']}",
        }
    )

    return AlgorithmBenchmarkComparison(
        algorithms=benchmarks,
        system_specs={
            "python_version": platform.python_version(),
            "os": platform.system(),
            "processor": platform.processor() or "Multi-Core CPU",
        },
        timestamp=datetime.now(UTC).isoformat(),
    )
