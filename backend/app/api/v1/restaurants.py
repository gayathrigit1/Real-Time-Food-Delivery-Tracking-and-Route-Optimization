from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User, UserRole
from app.schemas.restaurant import (
    MenuItemCreate,
    MenuItemOut,
    RestaurantCreate,
    RestaurantOut,
)
from app.services.restaurant_service import RestaurantService

router = APIRouter(prefix="/restaurants", tags=["Restaurants & Menus"])


@router.get("/", response_model=list[RestaurantOut])
async def list_restaurants(db: AsyncSession = Depends(get_db)):
    """Public: Retrieves all active restaurants and their menus."""
    return await RestaurantService.get_all_active(db)


@router.get("/{restaurant_id}", response_model=RestaurantOut)
async def get_restaurant(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    """Public: Retrieves specific restaurant by ID."""
    restaurant = await RestaurantService.get_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found.")
    return restaurant


@router.post("/", response_model=RestaurantOut, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant_in: RestaurantCreate,
    current_user: User = Depends(require_roles([UserRole.RESTAURANT, UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Restricted: Create a restaurant profile for current restaurant owner or admin."""
    # Check if user already owns a restaurant
    existing = await RestaurantService.get_by_owner_id(db, current_user.id)
    if existing and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already owns a registered restaurant.",
        )

    return await RestaurantService.create_restaurant(db, restaurant_in, owner_id=current_user.id)


@router.get("/{restaurant_id}/items", response_model=list[MenuItemOut])
async def get_restaurant_menu_items(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    """Public: Retrieves menu items of a specific restaurant."""
    return await RestaurantService.get_menu_items(db, restaurant_id)


@router.post(
    "/{restaurant_id}/items", response_model=MenuItemOut, status_code=status.HTTP_201_CREATED
)
async def add_menu_item(
    restaurant_id: int,
    item_in: MenuItemCreate,
    current_user: User = Depends(require_roles([UserRole.RESTAURANT, UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Restricted: Add item to restaurant menu (only owner or admin)."""
    restaurant = await RestaurantService.get_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found.")

    if current_user.role != UserRole.ADMIN and restaurant.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to modify this restaurant's menu.",
        )

    return await RestaurantService.add_menu_item(db, restaurant_id, item_in)
