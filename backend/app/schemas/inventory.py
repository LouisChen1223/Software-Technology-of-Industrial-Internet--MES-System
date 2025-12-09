from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Inventory Schemas
class InventoryBase(BaseModel):
    warehouse_id: int
    material_id: int
    batch_number: Optional[str] = None
    quantity: float
    available_quantity: Optional[float] = 0
    allocated_quantity: Optional[float] = 0
    location: Optional[str] = None
    unit_price: Optional[float] = 0
    production_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    batch_number: Optional[str] = None
    quantity: Optional[float] = None
    available_quantity: Optional[float] = None
    allocated_quantity: Optional[float] = None
    location: Optional[str] = None
    unit_price: Optional[float] = None
    production_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None


class InventoryResponse(InventoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Material Transaction Schemas
class MaterialTransactionBase(BaseModel):
    transaction_type: str  # pick, return, issue, receive, adjust, transfer
    material_id: int
    warehouse_id: int
    work_order_id: Optional[int] = None
    batch_number: Optional[str] = None
    quantity: float
    unit_price: Optional[float] = 0
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    operator_id: Optional[int] = None
    reference_no: Optional[str] = None
    notes: Optional[str] = None
    transaction_date: Optional[datetime] = None


class MaterialTransactionCreate(MaterialTransactionBase):
    pass


class MaterialTransactionResponse(MaterialTransactionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Material Pick Item Schema
class MaterialPickItemBase(BaseModel):
    material_id: int
    batch_number: Optional[str] = None
    required_quantity: float
    picked_quantity: Optional[float] = 0
    location: Optional[str] = None
    notes: Optional[str] = None


class MaterialPickItemCreate(MaterialPickItemBase):
    pass


class MaterialPickItemResponse(MaterialPickItemBase):
    id: int
    pick_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Material Pick Schemas
class MaterialPickBase(BaseModel):
    code: str = Field(..., max_length=50)
    work_order_id: Optional[int] = None
    warehouse_id: int
    pick_type: Optional[str] = "normal"  # normal, bom
    status: Optional[str] = "draft"
    requester_id: Optional[int] = None
    picker_id: Optional[int] = None
    request_date: Optional[datetime] = None
    pick_date: Optional[datetime] = None
    notes: Optional[str] = None


class MaterialPickCreate(MaterialPickBase):
    items: Optional[List[MaterialPickItemCreate]] = []


class MaterialPickUpdate(BaseModel):
    status: Optional[str] = None
    picker_id: Optional[int] = None
    pick_date: Optional[datetime] = None
    notes: Optional[str] = None


class MaterialPickResponse(MaterialPickBase):
    id: int
    items: List[MaterialPickItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Inventory Query Schema
class InventoryQueryParams(BaseModel):
    warehouse_id: Optional[int] = None
    material_id: Optional[int] = None
    batch_number: Optional[str] = None
    location: Optional[str] = None
