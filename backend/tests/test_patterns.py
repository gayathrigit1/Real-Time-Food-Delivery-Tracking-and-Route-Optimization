import time

from app.algorithms.dijkstra_routing import build_default_city_graph
from app.patterns.functional_tools import (
    OrderBatchIterator,
    apply_tax_and_delivery,
    calculate_item_subtotal,
    execution_timer,
    order_event_stream,
    order_filter_factory,
    timed_execution,
    transform_and_aggregate,
)
from app.patterns.oop_domain import (
    DeliveryRouteService,
    DijkstraRoutingStrategy,
    DirectDistanceStrategy,
    OrderDeliveryAggregate,
)


# 1. OOP Pattern Tests
def test_oop_domain_and_strategy_pattern():
    graph = build_default_city_graph()

    # Create service with default Dijkstra Strategy
    route_service = DeliveryRouteService(DijkstraRoutingStrategy(), graph)
    res1 = route_service.plan_delivery_route("Node_R1", "Node_C1")
    assert res1["strategy_name"] == "Dijkstra Shortest Path"
    assert res1["found"] is True

    # Switch Strategy at runtime (Polymorphism)
    route_service.set_strategy(DirectDistanceStrategy())
    res2 = route_service.plan_delivery_route("Node_R1", "Node_C1")
    assert res2["strategy_name"] == "Direct Planar Heuristic"
    assert res2["found"] is True


def test_order_delivery_aggregate():
    graph = build_default_city_graph()
    route_service = DeliveryRouteService(DijkstraRoutingStrategy(), graph)

    aggregate = OrderDeliveryAggregate(
        order_id=99, restaurant_node="Node_R1", customer_node="Node_C1"
    )
    assert aggregate.status == "PENDING"
    assert len(aggregate.history) == 1

    aggregate.assign_agent(agent_id=1, agent_node="Node_D1", route_service=route_service)
    assert aggregate.status == "ASSIGNED"
    assert aggregate.route_record is not None
    assert aggregate.route_record["total_distance_km"] > 0
    assert len(aggregate.history) == 2


# 2. Functional Tools Tests
def test_functional_pure_functions():
    subtotal = calculate_item_subtotal(15.50, 3)
    assert subtotal == 46.50
    total = apply_tax_and_delivery(subtotal, tax_rate=0.10, delivery_fee=4.0)
    assert total == 55.15


def test_functional_higher_order_and_reductions():
    orders = [
        {"order_id": 1, "total_amount": 25.0},
        {"order_id": 2, "total_amount": 55.0},
        {"order_id": 3, "total_amount": 12.0},
        {"order_id": 4, "total_amount": 80.0},
    ]

    # Filter with higher order predicate factory
    is_high_value = order_filter_factory(min_amount=50.0)
    high_value_orders = list(filter(is_high_value, orders))
    assert len(high_value_orders) == 2

    # Reduction using transform_and_aggregate
    total_val = transform_and_aggregate(
        high_value_orders,
        transform_fn=lambda o: o["total_amount"],
        combine_fn=lambda acc, val: acc + val,
        initial_value=0.0,
    )
    assert total_val == 135.0


def test_custom_iterator_and_generator():
    orders = [{"id": i} for i in range(1, 11)]
    batch_iter = OrderBatchIterator(orders, batch_size=4)

    batches = list(batch_iter)
    assert len(batches) == 3
    assert len(batches[0]) == 4
    assert len(batches[1]) == 4
    assert len(batches[2]) == 2

    # Generator test
    events = [{"type": "PLACED"}, {"type": "PREPARED"}, {"type": "DELIVERED"}]
    stream = list(order_event_stream(events))
    assert len(stream) == 3
    assert stream[0]["sequence_number"] == 1
    assert stream[2]["event_type"] == "DELIVERED"


def test_decorator_and_context_manager():
    @timed_execution("test_operation")
    def sample_func(x: int) -> dict:
        time.sleep(0.01)
        return {"result": x * 2}

    output = sample_func(10)
    assert output["result"] == 20
    assert "execution_time_ms" in output
    assert output["execution_time_ms"] > 0

    with execution_timer("Context Block") as timer:
        time.sleep(0.01)
    assert timer["duration_ms"] > 0
