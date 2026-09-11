from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/delivery-agents", tags=["delivery-agents"])


@router.post("", response_model=schemas.AgentOut, status_code=201)
def create_agent(payload: schemas.AgentCreate, db: Session = Depends(get_db)):
    agent = models.DeliveryAgent(**payload.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.get("", response_model=list[schemas.AgentOut])
def list_agents(db: Session = Depends(get_db)):
    return db.query(models.DeliveryAgent).all()


@router.get("/{agent_id}", response_model=schemas.AgentOut)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.get(models.DeliveryAgent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=schemas.AgentOut)
def update_agent(agent_id: int, payload: schemas.AgentUpdate, db: Session = Depends(get_db)):
    agent = db.get(models.DeliveryAgent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    db.commit()
    db.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=204)
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.get(models.DeliveryAgent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete an agent that has existing deliveries — mark them inactive instead",
        )


@router.get("/{agent_id}/deliveries", response_model=list[schemas.DeliveryWithOrderOut])
def get_deliveries_for_agent(agent_id: int, db: Session = Depends(get_db)):
    return db.query(models.Delivery).filter(models.Delivery.agent_id == agent_id).all()
