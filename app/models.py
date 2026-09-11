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


