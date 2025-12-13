from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DepartmentBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    manager: Optional[str] = None
    description: Optional[str] = None
    active: Optional[int] = 1


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    manager: Optional[str] = None
    description: Optional[str] = None
    active: Optional[int] = None


class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
