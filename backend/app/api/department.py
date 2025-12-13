from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Department
from app.schemas import DepartmentCreate, DepartmentUpdate, DepartmentResponse

router = APIRouter()

@router.post("/departments", response_model=DepartmentResponse)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    exists = db.query(Department).filter(Department.code == payload.code).first()
    if exists:
        raise HTTPException(status_code=400, detail="Department code already exists")
    entity = Department(**payload.dict())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity

@router.get("/departments", response_model=List[DepartmentResponse])
def list_departments(skip: int = 0, limit: int = 100, active: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Department)
    if active is not None:
        q = q.filter(Department.active == int(active))
    return q.offset(skip).limit(limit).all()

@router.get("/departments/{dept_id}", response_model=DepartmentResponse)
def get_department(dept_id: int, db: Session = Depends(get_db)):
    entity = db.query(Department).filter(Department.id == dept_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Department not found")
    return entity

@router.put("/departments/{dept_id}", response_model=DepartmentResponse)
def update_department(dept_id: int, payload: DepartmentUpdate, db: Session = Depends(get_db)):
    entity = db.query(Department).filter(Department.id == dept_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Department not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(entity, k, v)
    db.commit()
    db.refresh(entity)
    return entity

@router.delete("/departments/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    entity = db.query(Department).filter(Department.id == dept_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Department not found")
    db.delete(entity)
    db.commit()
    return {"message": "Department deleted"}
