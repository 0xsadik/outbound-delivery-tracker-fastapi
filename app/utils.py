from datetime import datetime
from sqlalchemy.orm import Session
from app import models

def log_status_change(db: Session, entity_type: str, entitiy_id: int, old_status, new_status: str):
    entry = models.StatusHistory(
        entity_type=entity_type, 
        entitiy_id=entitiy_id,
        old_status=old_status,
        new_status=new_status,
    )
    db.add(entry)
    db.flush()
    return entry 


def generate_order_number(order_id: int) -> str:
    year = datetime.utcnow().year 
    return f"ORD-{year}-{order_id:03d}"

