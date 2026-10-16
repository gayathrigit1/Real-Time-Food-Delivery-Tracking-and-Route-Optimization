
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.menu import MenuItem
from app.models.restaurant import Restaurant
from app.schemas.restaurant import (
    MenuItemCreate,
    RestaurantCreate,
    RestaurantUpdate,
)


class RestaurantService:

    @staticmethod
    async def get_all_active(db: AsyncSession) -> list[Restaurant]:
        stmt = (
            select(Restaurant)
            .where(Restaurant.is_active.is_(True))
            .options(selectinload(Restaurant.menu_items))
            .order_by(Restaurant.rating.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(
        db: AsyncSession, restaurant_id: int
    ) -> Restaurant | None:
        stmt = (
            select(Restaurant)
            .where(Restaurant.id == restaurant_id)
            .options(selectinload(Restaurant.menu_items))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_owner_id(
        db: AsyncSession, owner_id: int
    ) -> Restaurant | None:
        stmt = (
            select(Restaurant)
            .where(Restaurant.owner_id == owner_id)
            .options(selectinload(Restaurant.menu_items))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_restaurant(
        db: AsyncSession,
        restaurant_in: RestaurantCreate,
        owner_id: int,
    ) -> Restaurant:
        restaurant = Restaurant(
            name=restaurant_in.name,
            description=restaurant_in.description,
            cuisine_type=restaurant_in.cuisine_type,
            address=restaurant_in.address,
            node_id=restaurant_in.node_id,
            latitude=restaurant_in.latitude,
            longitude=restaurant_in.longitude,
            is_active=restaurant_in.is_active,
            owner_id=owner_id,
        )

        db.add(restaurant)
        await db.commit()
        await db.refresh(restaurant)

        # Reload the restaurant with menu_items eagerly loaded.
        stmt = (
            select(Restaurant)
            .where(Restaurant.id == restaurant.id)
            .options(selectinload(Restaurant.menu_items))
        )
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def update_restaurant(
        db: AsyncSession,
        restaurant: Restaurant,
        update_in: RestaurantUpdate,
    ) -> Restaurant:
        update_data = update_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(restaurant, field, value)

        db.add(restaurant)
        await db.commit()

        # Reload relationships to prevent async lazy-loading errors.
        stmt = (
            select(Restaurant)
            .where(Restaurant.id == restaurant.id)
            .options(selectinload(Restaurant.menu_items))
        )
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def get_menu_items(
        db: AsyncSession, restaurant_id: int
    ) -> list[MenuItem]:
        stmt = (
            select(MenuItem)
            .where(MenuItem.restaurant_id == restaurant_id)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def add_menu_item(
        db: AsyncSession,
        restaurant_id: int,
        item_in: MenuItemCreate,
    ) -> MenuItem:
        menu_item = MenuItem(
            restaurant_id=restaurant_id,
            name=item_in.name,
            description=item_in.description,
            price=item_in.price,
            category=item_in.category,
            is_available=item_in.is_available,
            preparation_time_mins=item_in.preparation_time_mins,
            image_url=item_in.image_url,
        )

        db.add(menu_item)
        await db.commit()
        await db.refresh(menu_item)
        return menu_item

    @staticmethod
    async def get_menu_item_by_id(
        db: AsyncSession, item_id: int
    ) -> MenuItem | None:
        stmt = select(MenuItem).where(MenuItem.id == item_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
