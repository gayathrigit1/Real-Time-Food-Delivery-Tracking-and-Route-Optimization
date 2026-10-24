from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: str | None = None
    price: float = Field(..., gt=0)
    category: str = "Main Course"
    is_available: bool = True
    preparation_time_mins: int = Field(default=15, ge=1, le=120)
    image_url: str | None = None


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(None, gt=0)
    category: str | None = None
    is_available: bool | None = None
    preparation_time_mins: int | None = None
    image_url: str | None = None


class MenuItemOut(MenuItemBase):
    id: int
    restaurant_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: str | None = None
    cuisine_type: str = "Multi-Cuisine"
    address: str
    node_id: str = "Node_R1"
    latitude: float = 12.9716
    longitude: float = 77.5946
    is_active: bool = True


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    cuisine_type: str | None = None
    address: str | None = None
    node_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    rating: float | None = None
    is_active: bool | None = None


class RestaurantOut(RestaurantBase):
    id: int
    rating: float
    owner_id: int
    created_at: datetime
    updated_at: datetime
    menu_items: list[MenuItemOut] = []

    model_config = ConfigDict(from_attributes=True)
