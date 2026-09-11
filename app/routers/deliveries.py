from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app import models, schemas
from app.utils import log_status_change

router = APIRouter(prefix="/api", tags=["deliveries"])

VALID_TRANSITIONS = {
    "assigned": ["picked_up", "failed"],
    "picked_up": ["in_transit", "failed"],
    "in_transit": ["delivered", "failed"],
    "delivered": [],
    "failed": [],
}


@router.post("/delivery-orders/{order_id}/assign", response_model=schemas.DeliveryOut, status_code=201)
def assign_order_to_agent(order_id: int, payload: schemas.AssignAgentIn, db: Session = Depends(get_db)):
    order = db.get(models.DeliveryOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    existing = db.query(models.Delivery).filter(models.Delivery.delivery_order_id == order_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Order already assigned")

    agent = db.get(models.DeliveryAgent, payload.agent_id)
    if not agent or not agent.is_active:
        raise HTTPException(status_code=400, detail="Agent not found or inactive")

    delivery = models.Delivery(
        delivery_order_id=order_id,
        agent_id=payload.agent_id,
        status="assigned",
        dispatched_at=datetime.now(timezone.utc),
    )
    db.add(delivery)

    old_order_status = order.status
    order.status = "assigned"

    db.flush()  # so delivery.id exists for the log entry below

    log_status_change(db, "DeliveryOrder", order_id, old_order_status, "assigned")
    log_status_change(db, "Delivery", delivery.id, None, "assigned")

    db.commit()
    db.refresh(delivery)
    return delivery


@router.patch("/deliveries/{delivery_id}/status", response_model=schemas.DeliveryOut)
def update_delivery_status(delivery_id: int, payload: schemas.DeliveryStatusIn, db: Session = Depends(get_db)):
    delivery = db.get(models.Delivery, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    new_status = payload.status
    allowed = VALID_TRANSITIONS.get(delivery.status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f'Cannot move from "{delivery.status}" to "{new_status}"',
        )

    old_status = delivery.status
    delivery.status = new_status
    if new_status == "delivered":
        delivery.delivered_at = datetime.now(timezone.utc)

    log_status_change(db, "Delivery", delivery_id, old_status, new_status)

    order = db.get(models.DeliveryOrder, delivery.delivery_order_id)

    if new_status in ("delivered", "failed"):
        order_new_status = "delivered" if new_status == "delivered" else "cancelled"
        old_order_status = order.status
        order.status = order_new_status
        log_status_change(db, "DeliveryOrder", order.id, old_order_status, order_new_status)
    elif new_status == "in_transit":
        old_order_status = order.status
        order.status = "out_for_delivery"
        log_status_change(db, "DeliveryOrder", order.id, old_order_status, "out_for_delivery")

    db.commit()
    db.refresh(delivery)
    return delivery
