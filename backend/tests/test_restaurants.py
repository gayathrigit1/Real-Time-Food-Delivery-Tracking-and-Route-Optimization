import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_restaurants(client: AsyncClient):
    response = await client.get("/api/v1/restaurants/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(r["name"] == "Bistro Gourmet Italiano" for r in data)


@pytest.mark.asyncio
async def test_get_restaurant_and_menu(client: AsyncClient):
    # Get restaurant #1
    response = await client.get("/api/v1/restaurants/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert len(data["menu_items"]) >= 3

    # Get specific items
    items_res = await client.get("/api/v1/restaurants/1/items")
    assert items_res.status_code == 200
    assert len(items_res.json()) >= 3


@pytest.mark.asyncio
async def test_add_menu_item_authorized(client: AsyncClient, restaurant_token: str):
    headers = {"Authorization": f"Bearer {restaurant_token}"}
    item_payload = {
        "name": "Panna Cotta al Caramello",
        "description": "Silky vanilla panna cotta with salted caramel drizzle",
        "price": 7.50,
        "category": "Dessert",
        "is_available": True,
        "preparation_time_mins": 8,
    }
    response = await client.post("/api/v1/restaurants/1/items", json=item_payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Panna Cotta al Caramello"
    assert data["price"] == 7.50


@pytest.mark.asyncio
async def test_add_menu_item_unauthorized_customer(client: AsyncClient, customer_token: str):
    headers = {"Authorization": f"Bearer {customer_token}"}
    item_payload = {
        "name": "Hacked Free Dish",
        "price": 0.01,
        "category": "Main Course",
    }
    response = await client.post("/api/v1/restaurants/1/items", json=item_payload, headers=headers)
    assert response.status_code == 403
