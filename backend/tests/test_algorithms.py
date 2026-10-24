import pytest

from app.algorithms.backtracking_route import BacktrackingRouteOptimizer
from app.algorithms.branch_and_bound import BranchAndBoundTSP
from app.algorithms.dijkstra_routing import DijkstraRouter, RoadGraph, build_default_city_graph
from app.algorithms.divide_and_conquer import DivideAndConquerAnalytics
from app.algorithms.dynamic_programming import OrderSelectionDP
from app.algorithms.greedy_assignment import GreedyAgentSelector


# 1. Greedy Assignment Tests
def test_greedy_agent_assignment():
    selector = GreedyAgentSelector(weight_distance=0.5, weight_workload=0.3, weight_rating=0.2)
    agents = [
        {
            "id": 1,
            "current_node": "Node_D1",
            "current_workload": 0,
            "max_capacity": 4,
            "rating": 5.0,
            "is_available": True,
        },
        {
            "id": 2,
            "current_node": "Node_D2",
            "current_workload": 3,
            "max_capacity": 4,
            "rating": 4.0,
            "is_available": True,
        },
        {
            "id": 3,
            "current_node": "Node_D3",
            "current_workload": 4,
            "max_capacity": 4,
            "rating": 5.0,
            "is_available": False,
        },  # unavailable
    ]
    dist_lookup = {("Node_D1", "Node_R1"): 1.5, ("Node_D2", "Node_R1"): 5.0}

    best, all_eval = selector.select_best_agent("Node_R1", agents, dist_lookup)
    assert best is not None
    assert best["agent_id"] == 1  # closest and least busy
    assert len(all_eval) == 2  # agent 3 ignored due to availability/capacity


# 2. Dijkstra Shortest Path Tests
def test_dijkstra_shortest_path():
    graph = build_default_city_graph()
    router = DijkstraRouter(graph)

    res = router.shortest_path("Node_R1", "Node_C1")
    assert res["found"] is True
    assert res["path"][0] == "Node_R1"
    assert res["path"][-1] == "Node_C1"
    # Expected route: Node_R1 -> Node_B -> Node_D -> Node_C1 = 1.2 + 2.0 + 1.5 = 4.7 km
    assert res["total_distance_km"] == pytest.approx(4.7, 0.1)


def test_dijkstra_unreachable_node():
    graph = RoadGraph()
    graph.add_node("Isolated_A")
    graph.add_node("Isolated_B")
    router = DijkstraRouter(graph)
    res = router.shortest_path("Isolated_A", "Isolated_B")
    assert res["found"] is False


# 3. Dynamic Programming 0/1 Knapsack Tests
def test_dp_order_selection():
    dp = OrderSelectionDP(max_time_window_mins=50)
    orders = [
        {"order_id": 1, "preparation_time": 10, "profit_or_priority": 60},
        {"order_id": 2, "preparation_time": 20, "profit_or_priority": 100},
        {"order_id": 3, "preparation_time": 30, "profit_or_priority": 120},
    ]
    # Optimal for W=50: Items 2 & 3 (time 50, profit 220)
    res = dp.optimize_batch(orders, time_window=50)
    assert res["max_profit_or_priority"] == 220
    assert len(res["selected_orders"]) == 2
    assert res["total_time_used"] == 50


# 4. Backtracking Route Sequencing Tests
def test_backtracking_route():
    dist_matrix = {
        ("Node_R1", "Node_C1"): 2.0,
        ("Node_R1", "Node_C2"): 4.0,
        ("Node_C1", "Node_C2"): 1.5,
    }
    bt = BacktrackingRouteOptimizer(dist_matrix)
    # Start at Node_R1, visit C1 and C2
    res = bt.find_constrained_tours("Node_R1", ["Node_C1", "Node_C2"], max_total_distance_km=10.0)
    assert len(res["valid_sequences"]) == 2  # [R1, C1, C2] and [R1, C2, C1]
    assert res["best_sequence"] == ["Node_R1", "Node_C1", "Node_C2"]  # 2.0 + 1.5 = 3.5 km
    assert res["best_distance_km"] == 3.5


# 5. Branch and Bound TSP Tests
def test_branch_and_bound_tsp():
    dist_matrix = {
        ("A", "B"): 2.0,
        ("A", "C"): 3.0,
        ("A", "D"): 1.0,
        ("B", "C"): 1.5,
        ("B", "D"): 2.5,
        ("C", "D"): 2.0,
    }
    bb = BranchAndBoundTSP(dist_matrix)
    res = bb.solve_tsp(["A", "B", "C", "D"])
    assert res["minimum_distance_km"] > 0
    assert len(res["optimal_tour"]) == 5  # Returns to start
    assert res["optimal_tour"][0] == "A"
    assert res["optimal_tour"][-1] == "A"
    assert res["nodes_explored"] > 0


# 6. Divide and Conquer Analytics Tests
def test_divide_and_conquer_analytics():
    dac = DivideAndConquerAnalytics()
    data = [45.0, 12.0, 89.0, 23.5, 67.0, 10.0, 100.0]
    res = dac.analyze_order_values(data, top_k=3)

    assert res["total_orders_analyzed"] == 7
    assert res["min_order_value"] == 10.0
    assert res["max_order_value"] == 100.0
    assert res["total_revenue"] == pytest.approx(sum(data), 0.01)
    assert res["median_order_value"] == 45.0
    assert res["top_k_orders"] == [100.0, 89.0, 67.0]
    assert res["recursion_depth"] >= 2
