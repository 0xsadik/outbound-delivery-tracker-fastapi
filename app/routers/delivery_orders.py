from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app import models, schemas
from app.utils import log_status_change, generate_order_number

router = APIRouter(prefix="/api/delivery-orders", tags=["delivery-orders"])


def _load_order(db: Session, order_id: int):
    return (
        db.query(models.DeliveryOrder)
        .options(
            joinedload(models.DeliveryOrder.customer),
            joinedload(models.DeliveryOrder.items).joinedload(models.OrderItem.product),
            joinedload(models.DeliveryOrder.delivery),
        )
        .filter(models.DeliveryOrder.id == order_id)
        .first()
    )


@router.post("", response_model=schemas.DeliveryOrderOut, status_code=201)
def create_delivery_order(payload: schemas.DeliveryOrderCreate, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    try:
        for item in payload.items:
            product = db.get(models.Product, item.product_id)
            if not product:
                raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
            if product.quantity_in_stock < item.qty:
                raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")

        order = models.DeliveryOrder(
            customer_id=payload.customer_id,
            order_number="PENDING",  # placeholder until we have a real id
            status="pending",
        )
        db.add(order)
        db.flush()  # assigns order.id without committing yet

        order.order_number = generate_order_number(order.id)

        for item in payload.items:
            db.add(models.OrderItem(
                delivery_order_id=order.id,
                product_id=item.product_id,
                qty=item.qty,
            ))
            product = db.get(models.Product, item.product_id)
            product.quantity_in_stock -= item.qty

        log_status_change(db, "DeliveryOrder", order.id, None, "pending")
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))

    return _load_order(db, order.id)


@router.get("", response_model=list[schemas.DeliveryOrderOut])
def list_delivery_orders(db: Session = Depends(get_db)):
    return (
        db.query(models.DeliveryOrder)
        .options(
            joinedload(models.DeliveryOrder.customer),
            joinedload(models.DeliveryOrder.items).joinedload(models.OrderItem.product),
            joinedload(models.DeliveryOrder.delivery),
        )
        .all()
    )


@router.get("/{order_id}", response_model=schemas.DeliveryOrderOut)
def get_delivery_order(order_id: int, db: Session = Depends(get_db)):
    order = _load_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/{order_id}/tracking", response_model=schemas.TrackingOut)
def get_delivery_order_tracking(order_id: int, db: Session = Depends(get_db)):
    order = _load_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_history = (
        db.query(models.StatusHistory)
        .filter(models.StatusHistory.entity_type == "DeliveryOrder", models.StatusHistory.entity_id == order_id)
        .order_by(models.StatusHistory.changed_at.asc())
        .all()
    )

    delivery_history = []
    if order.delivery:
        delivery_history = (
            db.query(models.StatusHistory)
            .filter(models.StatusHistory.entity_type == "Delivery", models.StatusHistory.entity_id == order.delivery.id)
            .order_by(models.StatusHistory.changed_at.asc())
            .all()
        )

    timeline = sorted(order_history + delivery_history, key=lambda e: e.changed_at)

    return schemas.TrackingOut(
        order_status=order.status,
        delivery_status=order.delivery.status if order.delivery else None,
        timeline=timeline,
    )


@router.post("/{order_id}/cancel", response_model=schemas.DeliveryOrderOut)
def cancel_delivery_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(models.DeliveryOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order.status
    order.status = "cancelled"
    log_status_change(db, "DeliveryOrder", order_id, old_status, "cancelled")
    db.commit()

    return _load_order(db, order_id)
