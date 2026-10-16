from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.delivery import DeliveryAgent
from app.models.menu import MenuItem
from app.models.order import Order, OrderStatus
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole
from app.utils.seed_data import seed_initial_data

router = APIRouter(prefix="/admin", tags=["Admin & System"])


@router.get("/summary", dependencies=[Depends(require_roles([UserRole.ADMIN]))])
async def get_system_summary(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Admin: Overview of total users, restaurants, menu items, orders, and delivery agent statuses."""
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_restaurants = (await db.execute(select(func.count(Restaurant.id)))).scalar() or 0
    total_menu_items = (await db.execute(select(func.count(MenuItem.id)))).scalar() or 0
    total_orders = (await db.execute(select(func.count(Order.id)))).scalar() or 0

    # Orders grouped by status
    status_counts = {}
    for st in OrderStatus:
        cnt = (
            await db.execute(select(func.count(Order.id)).where(Order.status == st))
        ).scalar() or 0
        status_counts[st.value] = cnt

    total_agents = (await db.execute(select(func.count(DeliveryAgent.id)))).scalar() or 0
    available_agents = (
        await db.execute(
            select(func.count(DeliveryAgent.id)).where(DeliveryAgent.is_available.is_(True))
        )
    ).scalar() or 0

    return {
        "total_users": total_users,
        "total_restaurants": total_restaurants,
        "total_menu_items": total_menu_items,
        "total_orders": total_orders,
        "orders_by_status": status_counts,
        "total_delivery_agents": total_agents,
        "available_delivery_agents": available_agents,
    }


@router.post("/seed-reset", dependencies=[Depends(require_roles([UserRole.ADMIN]))])
async def reset_and_seed_database(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Admin: Triggers re-seeding of standard demo accounts, restaurants, and menu catalog."""
    await seed_initial_data(db)
    return {"message": "Database successfully re-seeded with demo records."}
