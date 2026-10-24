from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.delivery import DeliveryAgent
from app.models.menu import MenuItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.restaurant import Restaurant
from app.schemas.order import OrderCreate, OrderStatusUpdate
from app.services.delivery_service import DeliveryService


class OrderService:
    @staticmethod
    async def get_by_id(db: AsyncSession, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.delivery_assignment),
                selectinload(Order.restaurant),
                selectinload(Order.customer),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        customer_id: int | None = None,
        restaurant_id: int | None = None,
        agent_id: int | None = None,
    ) -> list[Order]:
        stmt = (
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.delivery_assignment),
                selectinload(Order.restaurant),
                selectinload(Order.customer),
            )
            .order_by(Order.created_at.desc())
        )

        if customer_id is not None:
            stmt = stmt.where(Order.customer_id == customer_id)
        if restaurant_id is not None:
            stmt = stmt.where(Order.restaurant_id == restaurant_id)
        if agent_id is not None:
            stmt = stmt.join(Order.delivery_assignment).where(
                Order.delivery_assignment.has(agent_id=agent_id)
            )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_order(db: AsyncSession, customer_id: int, order_in: OrderCreate) -> Order:
        """
        Creates an order with strictly server-side price validation.
        """
        restaurant = await db.get(Restaurant, order_in.restaurant_id)
        if not restaurant or not restaurant.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found or inactive.",
            )

        calculated_subtotal = 0.0
        db_order_items: list[OrderItem] = []

        # Validate each item against database
        for item_req in order_in.items:
            stmt_item = select(MenuItem).where(
                MenuItem.id == item_req.menu_item_id,
                MenuItem.restaurant_id == order_in.restaurant_id,
            )
            menu_item = (await db.execute(stmt_item)).scalar_one_or_none()

            if not menu_item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Menu item ID {item_req.menu_item_id} not found in this restaurant.",
                )
            if not menu_item.is_available:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Menu item '{menu_item.name}' is currently unavailable.",
                )

            item_subtotal = round(menu_item.price * item_req.quantity, 2)
            calculated_subtotal += item_subtotal

            db_order_items.append(
                OrderItem(
                    menu_item_id=menu_item.id,
                    item_name=menu_item.name,
                    quantity=item_req.quantity,
                    unit_price=menu_item.price,  # Authoritative DB price
                    subtotal=item_subtotal,
                )
            )

        delivery_fee = 5.00
        tax_amount = round(calculated_subtotal * 0.05, 2)
        total_amount = round(calculated_subtotal + tax_amount + delivery_fee, 2)

        order = Order(
            customer_id=customer_id,
            restaurant_id=order_in.restaurant_id,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            delivery_fee=delivery_fee,
            tax_amount=tax_amount,
            special_instructions=order_in.special_instructions,
            delivery_address=order_in.delivery_address,
            delivery_node=order_in.delivery_node,
        )
        db.add(order)
        await db.flush()  # get order.id

        for oi in db_order_items:
            oi.order_id = order.id
            db.add(oi)

        await db.commit()
        await db.refresh(order)
        return await OrderService.get_by_id(db, order.id)  # type: ignore

    @staticmethod
    async def update_status(
        db: AsyncSession, order_id: int, status_update: OrderStatusUpdate
    ) -> Order:
        """
        Updates order status and triggers delivery assignment or completion workflows.
        """
        order = await OrderService.get_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

        new_status = status_update.status
        order.status = new_status

        # Workflow: When READY_FOR_PICKUP is reached, automatically trigger Greedy + Dijkstra agent assignment
        if new_status == OrderStatus.READY_FOR_PICKUP:
            assignment = await DeliveryService.assign_agent_to_order(db, order.id)
            if assignment:
                order.delivery_assignment = assignment

        # Workflow: When DELIVERING, mark picked_up_at
        elif new_status == OrderStatus.DELIVERING and order.delivery_assignment:
            order.delivery_assignment.picked_up_at = datetime.now(UTC)
            db.add(order.delivery_assignment)

        # Workflow: When DELIVERED, mark delivered_at and release agent workload
        elif new_status == OrderStatus.DELIVERED and order.delivery_assignment:
            order.delivery_assignment.delivered_at = datetime.now(UTC)
            db.add(order.delivery_assignment)

            agent = await db.get(DeliveryAgent, order.delivery_assignment.agent_id)
            if agent:
                agent.current_workload = max(0, agent.current_workload - 1)
                agent.total_deliveries += 1
                db.add(agent)

        db.add(order)
        await db.commit()
        db.expire_all()
        return await OrderService.get_by_id(db, order_id)  # type: ignore
