from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., gt=0, le=50)


class OrderItemOut(BaseModel):
    id: int
    menu_item_id: int
    item_name: str
    quantity: int
    unit_price: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    restaurant_id: int
    delivery_address: str = Field(..., min_length=3)
    delivery_node: str = "Node_C1"
    special_instructions: str | None = None
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class DeliveryAssignmentBrief(BaseModel):
    id: int
    agent_id: int
    algorithm_used: str
    assignment_score: float
    route_path: list[str] | None = None
    total_distance: float
    estimated_time_mins: float
    assigned_at: datetime
    picked_up_at: datetime | None = None
    delivered_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class OrderOut(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    status: OrderStatus
    total_amount: float
    delivery_fee: float
    tax_amount: float
    special_instructions: str | None = None
    delivery_address: str
    delivery_node: str
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemOut] = []
    delivery_assignment: DeliveryAssignmentBrief | None = None

    model_config = ConfigDict(from_attributes=True)
