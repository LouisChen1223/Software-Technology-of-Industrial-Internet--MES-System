from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Workshop
from app.schemas import WorkshopCreate, WorkshopUpdate, WorkshopResponse

router = APIRouter()

@router.post("/workshops", response_model=WorkshopResponse)
def create_workshop(payload: WorkshopCreate, db: Session = Depends(get_db)):
    exists = db.query(Workshop).filter(Workshop.code == payload.code).first()
    if exists:
        raise HTTPException(status_code=400, detail="Workshop code already exists")
    entity = Workshop(**payload.dict())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity

@router.get("/workshops", response_model=List[WorkshopResponse])
def list_workshops(skip: int = 0, limit: int = 100, active: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Workshop)
    if active is not None:
        q = q.filter(Workshop.active == int(active))
    return q.offset(skip).limit(limit).all()

@router.get("/workshops/{ws_id}", response_model=WorkshopResponse)
def get_workshop(ws_id: int, db: Session = Depends(get_db)):
    entity = db.query(Workshop).filter(Workshop.id == ws_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Workshop not found")
    return entity

@router.put("/workshops/{ws_id}", response_model=WorkshopResponse)
def update_workshop(ws_id: int, payload: WorkshopUpdate, db: Session = Depends(get_db)):
    entity = db.query(Workshop).filter(Workshop.id == ws_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Workshop not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(entity, k, v)
    db.commit()
    db.refresh(entity)
    return entity

@router.delete("/workshops/{ws_id}")
def delete_workshop(ws_id: int, db: Session = Depends(get_db)):
    entity = db.query(Workshop).filter(Workshop.id == ws_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Workshop not found")
    db.delete(entity)
    db.commit()
    return {"message": "Workshop deleted"}
