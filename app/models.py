from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base 

def utcnow():
    return datetime.now(timezone.utc)


class Product(Base):
    __tablename__= "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    quantity_in_stock = Column(Integer, default=0, nullable=False)
    order_items = relationship("OrderItem", back_populates="product")









class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    delivery_orders = relationship("DeliveryOrder", back_populates="customer")


class DeliveryOrder(Base):
    __tablename__ = "delivery_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    # pending -> confirmed -> assigned -> out_for_delivery -> delivered / cancelled
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    customer = relationship("Customer", back_populates="delivery_orders")
    items = relationship(
        "OrderItem", back_populates="delivery_order", cascade="all, delete-orphan"
    )
    delivery = relationship(
        "Delivery", back_populates="delivery_order", uselist=False,
        cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    delivery_order_id = Column(Integer, ForeignKey("delivery_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    qty = Column(Integer, nullable=False)

    delivery_order = relationship("DeliveryOrder", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class DeliveryAgent(Base):
    __tablename__ = "delivery_agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    vehicle_info = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    deliveries = relationship("Delivery", back_populates="agent")


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    delivery_order_id = Column(
        Integer, ForeignKey("delivery_orders.id"), nullable=False, unique=True
    )
    agent_id = Column(Integer, ForeignKey("delivery_agents.id"), nullable=True)
    # assigned -> picked_up -> in_transit -> delivered / failed
    status = Column(String, default="assigned", nullable=False)
    dispatched_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    delivery_order = relationship("DeliveryOrder", back_populates="delivery")
    agent = relationship("DeliveryAgent", back_populates="deliveries")


class StatusHistory(Base):
    """Generic audit trail used by every status change across the domain."""
    __tablename__ = "status_history"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)  # "DeliveryOrder" | "Delivery"
    entity_id = Column(Integer, nullable=False)
    old_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False)
    changed_at = Column(DateTime(timezone=True), default=utcnow)
