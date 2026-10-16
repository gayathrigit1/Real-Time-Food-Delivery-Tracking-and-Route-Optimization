from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.algorithms.dijkstra_routing import DijkstraRouter, build_default_city_graph
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.order import OrderStatus
from app.models.user import User, UserRole
from app.schemas.delivery import RouteResponse
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate
from app.services.delivery_service import DeliveryService
from app.services.order_service import OrderService
from app.services.restaurant_service import RestaurantService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Customer: Place a new order with backend-verified item pricing."""
    return await OrderService.create_order(db, customer_id=current_user.id, order_in=order_in)


@router.get("/", response_model=list[OrderOut])
async def list_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List orders tailored to current role:
    - Customer: Sees own placed orders
    - Restaurant: Sees incoming orders for owned restaurant
    - Delivery Agent: Sees orders assigned to them
    - Admin: Sees all orders
    """
    if current_user.role == UserRole.CUSTOMER:
        return await OrderService.get_all(db, customer_id=current_user.id)

    elif current_user.role == UserRole.RESTAURANT:
        restaurant = await RestaurantService.get_by_owner_id(db, current_user.id)
        if not restaurant:
            return []
        return await OrderService.get_all(db, restaurant_id=restaurant.id)

    elif current_user.role == UserRole.DELIVERY_AGENT:
        agent = await DeliveryService.get_agent_by_user_id(db, current_user.id)
        if not agent:
            return []
        return await OrderService.get_all(db, agent_id=agent.id)

    elif current_user.role == UserRole.ADMIN:
        return await OrderService.get_all(db)

    return []


@router.get("/{order_id}", response_model=OrderOut)
async def get_order_by_id(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve single order with access protection."""
    order = await OrderService.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    # Authorization checks
    if current_user.role == UserRole.CUSTOMER and order.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this order."
        )

    if current_user.role == UserRole.RESTAURANT:
        restaurant = await RestaurantService.get_by_owner_id(db, current_user.id)
        if not restaurant or order.restaurant_id != restaurant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this order."
            )

    if current_user.role == UserRole.DELIVERY_AGENT:
        agent = await DeliveryService.get_agent_by_user_id(db, current_user.id)
        if not agent or (
            order.delivery_assignment and order.delivery_assignment.agent_id != agent.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this order."
            )

    return order


@router.get("/{order_id}/route", response_model=RouteResponse)
async def get_order_route_details(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculates or retrieves live route between agent, restaurant, and customer."""
    order = await OrderService.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    restaurant_node = order.restaurant.node_id if order.restaurant else "Node_R1"
    customer_node = order.delivery_node or "Node_C1"

    agent_node = "Node_D1"
    if order.delivery_assignment and order.delivery_assignment.agent:
        agent_node = order.delivery_assignment.agent.current_node

    graph = build_default_city_graph()
    router_inst = DijkstraRouter(graph)

    # Route: Restaurant -> Customer
    route_res = router_inst.shortest_path(restaurant_node, customer_node)

    # Steps formatted for UI
    steps = []
    path = route_res.get("path", [restaurant_node, customer_node])
    for idx, node in enumerate(path):
        meta = graph.node_metadata.get(node, {})
        steps.append(
            {
                "step_index": idx + 1,
                "node_id": node,
                "label": meta.get("label", node),
                "type": meta.get("node_type", "INTERSECTION"),
                "lat": meta.get("latitude", 0.0),
                "lon": meta.get("longitude", 0.0),
            }
        )

    return RouteResponse(
        order_id=order.id,
        source_node=restaurant_node,
        destination_node=customer_node,
        agent_node=agent_node,
        path=path,
        distance_km=route_res.get("total_distance_km", 0.0),
        estimated_time_mins=route_res.get("estimated_time_mins", 0.0),
        steps=steps,
        graph_visual={
            "nodes": [{"id": k, **v} for k, v in graph.node_metadata.items()],
            "edges": [
                {"u": u, "v": v, "w": w}
                for u, neighbors in graph.adj_list.items()
                for v, w in neighbors
                if u < v
            ],
        },
    )


@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: int,
    status_in: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Role-protected order state progression:
    - Restaurant: Can set status to PREPARING or READY_FOR_PICKUP
    - Delivery Agent: Can set status to DELIVERING or DELIVERED
    - Admin: Can update any status
    """
    order = await OrderService.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    new_status = status_in.status

    if current_user.role == UserRole.RESTAURANT:
        restaurant = await RestaurantService.get_by_owner_id(db, current_user.id)
        if not restaurant or order.restaurant_id != restaurant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this order's restaurant.",
            )
        if new_status not in [
            OrderStatus.PREPARING,
            OrderStatus.READY_FOR_PICKUP,
            OrderStatus.CANCELLED,
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Restaurants cannot set status to {new_status}.",
            )

    elif current_user.role == UserRole.DELIVERY_AGENT:
        agent = await DeliveryService.get_agent_by_user_id(db, current_user.id)
        if not agent or (
            order.delivery_assignment and order.delivery_assignment.agent_id != agent.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not assigned to this order."
            )
        if new_status not in [OrderStatus.DELIVERING, OrderStatus.DELIVERED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Delivery agents cannot set status to {new_status}.",
            )

    elif current_user.role == UserRole.CUSTOMER:
        if new_status != OrderStatus.CANCELLED or order.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customers can only cancel their own pending orders.",
            )
        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel an order that is already being prepared.",
            )

    return await OrderService.update_status(db, order_id, status_in)
