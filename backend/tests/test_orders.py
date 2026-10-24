import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_complete_order_lifecycle_workflow(
    client: AsyncClient,
    customer_token: str,
    restaurant_token: str,
    agent_token: str,
):
    cust_headers = {"Authorization": f"Bearer {customer_token}"}
    rest_headers = {"Authorization": f"Bearer {restaurant_token}"}
    agent_headers = {"Authorization": f"Bearer {agent_token}"}

    # Step 1: Customer places an order (Bistro items: Truffle Risotto $18.50 x 2 = $37.00)
    order_payload = {
        "restaurant_id": 1,
        "delivery_address": "Apartment 101, Downtown Tower",
        "delivery_node": "Node_C1",
        "special_instructions": "Please leave at door.",
        "items": [
            {"menu_item_id": 1, "quantity": 2},  # 2 x 18.50 = 37.00
            {"menu_item_id": 4, "quantity": 1},  # 1 x 8.50 = 8.50
        ],
    }
    # Expected: subtotal = 45.50, tax = 2.28, delivery = 5.00 -> total = 52.78
    res = await client.post("/api/v1/orders/", json=order_payload, headers=cust_headers)
    assert res.status_code == 201
    order = res.json()
    order_id = order["id"]
    assert order["status"] == "PENDING"
    assert order["total_amount"] == pytest.approx(52.77, abs=0.02)
    assert len(order["items"]) == 2

    # Step 2: Restaurant views incoming order
    rest_orders_res = await client.get("/api/v1/orders/", headers=rest_headers)
    assert rest_orders_res.status_code == 200
    assert any(o["id"] == order_id for o in rest_orders_res.json())

    # Step 3: Restaurant marks order PREPARING
    prep_res = await client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "PREPARING"},
        headers=rest_headers,
    )
    assert prep_res.status_code == 200
    assert prep_res.json()["status"] == "PREPARING"

    # Step 4: Restaurant marks READY_FOR_PICKUP -> System automatically evaluates Greedy Agent & Dijkstra
    ready_res = await client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "READY_FOR_PICKUP"},
        headers=rest_headers,
    )
    assert ready_res.status_code == 200
    ready_data = ready_res.json()
    assert ready_data["status"] == "READY_FOR_PICKUP"
    assert ready_data["delivery_assignment"] is not None
    assert ready_data["delivery_assignment"]["agent_id"] in [1, 2]
    assert len(ready_data["delivery_assignment"]["route_path"]) >= 2

    # Step 5: Delivery Agent views assigned order and marks DELIVERING
    delivering_res = await client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "DELIVERING"},
        headers=agent_headers,
    )
    assert delivering_res.status_code == 200
    assert delivering_res.json()["status"] == "DELIVERING"

    # Step 6: Delivery Agent marks DELIVERED
    delivered_res = await client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "DELIVERED"},
        headers=agent_headers,
    )
    assert delivered_res.status_code == 200
    assert delivered_res.json()["status"] == "DELIVERED"

    # Step 7: Customer inspects final route telemetry
    route_res = await client.get(f"/api/v1/orders/{order_id}/route", headers=cust_headers)
    assert route_res.status_code == 200
    route_data = route_res.json()
    assert route_data["source_node"] == "Node_R1"
    assert route_data["destination_node"] == "Node_C1"
    assert len(route_data["path"]) >= 2
    assert route_data["distance_km"] > 0
