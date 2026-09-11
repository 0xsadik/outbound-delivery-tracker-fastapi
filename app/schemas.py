from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

def to_camel(snake: str) -> str:
    parts = snake.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


# ----- product --------

class ProductCreate(CamelModel):
    sku: str
    name: str
    quantity_in_stock: int =  0 

class ProductUpdate(CamelModel):
    sku: Optional[str] = None
    name: Optional[str] = None 
    quantity_in_stock: Optional[int] = None 

class ProductOut(CamelModel):
    id: int 
    sku: str 
    name: str 
    quantity_in_stock: int 
    created_at: datetime 


# ----- customer ----------- 

class CustomerCreate(CamelModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomerUpdate(CamelModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomerOut(CamelModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime




# ------- delivery agent ---------


class AgentCreate(CamelModel):
    name: str
    phone: Optional[str] = None
    vehicle_info: Optional[str] = None


class AgentUpdate(CamelModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    vehicle_info: Optional[str] = None
    is_active: Optional[bool] = None


class AgentOut(CamelModel):
    id: int
    name: str
    phone: Optional[str] = None
    vehicle_info: Optional[str] = None
    is_active: bool



# ----- order items ----------


class OrderItemIn(CamelModel):
    product_id: int
    qty: int


class OrderItemOut(CamelModel):
    id: int
    delivery_order_id: int
    product_id: int
    qty: int
    product: Optional[ProductOut] = None







# ------- Delivery -------


class DeliveryOut(CamelModel):
    id: int
    delivery_order_id: int
    agent_id: Optional[int] = None
    status: str
    dispatched_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class DeliveryWithOrderOut(DeliveryOut):
    delivery_order: Optional["DeliveryOrderOut"] = None


class AssignAgentIn(CamelModel):
    agent_id: int


class DeliveryStatusIn(CamelModel):
    status: str



# ------- delivery order ----------


class DeliveryOrderCreate(CamelModel):
    customer_id: int
    items: List[OrderItemIn]


class DeliveryOrderOut(CamelModel):
    id: int
    order_number: str
    customer_id: int
    status: str
    created_at: datetime
    customer: Optional[CustomerOut] = None
    items: List[OrderItemOut] = []
    delivery: Optional[DeliveryOut] = None






# ------- status history ------------


class StatusHistoryOut(CamelModel):
    id: int
    entity_type: str
    entity_id: int
    old_status: Optional[str] = None
    new_status: str
    changed_at: datetime


class TrackingOut(CamelModel):
    order_status: str
    delivery_status: Optional[str] = None
    timeline: List[StatusHistoryOut]


