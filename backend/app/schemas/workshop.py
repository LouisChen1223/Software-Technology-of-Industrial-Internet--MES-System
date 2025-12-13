from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WorkshopBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    supervisor: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    active: Optional[int] = 1


class WorkshopCreate(WorkshopBase):
    pass


class WorkshopUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    supervisor: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    active: Optional[int] = None


class WorkshopResponse(WorkshopBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
