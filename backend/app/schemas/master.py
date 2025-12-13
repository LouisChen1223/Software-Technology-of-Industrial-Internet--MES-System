from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# UOM Schemas
class UOMBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    precision: Optional[float] = 0
    active: Optional[int] = 1


class UOMCreate(UOMBase):
    pass


class UOMUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    precision: Optional[float] = None
    active: Optional[int] = None


class UOMResponse(UOMBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Warehouse Schemas
class WarehouseBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    location: Optional[str] = None
    warehouse_type: Optional[str] = None
    manager: Optional[str] = None
    description: Optional[str] = None
    active: Optional[int] = 1


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = None
    warehouse_type: Optional[str] = None
    manager: Optional[str] = None
    description: Optional[str] = None
    active: Optional[int] = None


class WarehouseResponse(WarehouseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Material Schemas
class MaterialBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    specification: Optional[str] = None
    material_type: Optional[str] = None
    uom_id: Optional[int] = None
    unit_price: Optional[float] = 0
    safety_stock: Optional[float] = 0
    lead_time: Optional[int] = 0
    supplier: Optional[str] = None
    description: Optional[str] = None
    active: Optional[int] = 1


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    specification: Optional[str] = None
    material_type: Optional[str] = None
    uom_id: Optional[int] = None
    unit_price: Optional[float] = None
    safety_stock: Optional[float] = None
    lead_time: Optional[int] = None
    supplier: Optional[str] = None
    description: Optional[str] = None
    active: Optional[int] = None


class MaterialResponse(MaterialBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# BOM Item Schema
class BOMItemBase(BaseModel):
    material_id: int
    quantity: float
    sequence: Optional[int] = 0
    scrap_rate: Optional[float] = 0
    description: Optional[str] = None


class BOMItemCreate(BOMItemBase):
    pass


class BOMItemResponse(BOMItemBase):
    id: int
    bom_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# BOM Schemas
class BOMBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    product_id: int
    version: Optional[str] = "1.0"
    quantity: Optional[float] = 1
    is_active: Optional[int] = 1
    description: Optional[str] = None


class BOMCreate(BOMBase):
    items: Optional[List[BOMItemCreate]] = []


class BOMUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    product_id: Optional[int] = None
    version: Optional[str] = None
    quantity: Optional[float] = None
    is_active: Optional[int] = None
    description: Optional[str] = None
    items: Optional[List[BOMItemCreate]] = None


class BOMResponse(BOMBase):
    id: int
    items: List[BOMItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Operation Schemas
class OperationBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    operation_type: Optional[str] = None
    standard_time: Optional[float] = 0
    description: Optional[str] = None


class OperationCreate(OperationBase):
    pass


class OperationUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    operation_type: Optional[str] = None
    standard_time: Optional[float] = None
    description: Optional[str] = None


class OperationResponse(OperationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Equipment Schemas
class EquipmentBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    equipment_type: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    capacity: Optional[float] = 0
    status: Optional[str] = "idle"
    location: Optional[str] = None
    description: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    equipment_type: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    capacity: Optional[float] = None
    status: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class EquipmentResponse(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Tooling Schemas
class ToolingBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    tooling_type: Optional[str] = None
    specification: Optional[str] = None
    quantity: Optional[int] = 0
    status: Optional[str] = "available"
    location: Optional[str] = None
    description: Optional[str] = None


class ToolingCreate(ToolingBase):
    pass


class ToolingUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    tooling_type: Optional[str] = None
    specification: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class ToolingResponse(ToolingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Personnel Schemas
class PersonnelBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    department: Optional[str] = None
    position: Optional[str] = None
    skill_level: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    shift_code: Optional[str] = None
    status: Optional[str] = "active"


class PersonnelCreate(PersonnelBase):
    pass


class PersonnelUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = None
    position: Optional[str] = None
    skill_level: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    shift_code: Optional[str] = None
    status: Optional[str] = None


class PersonnelResponse(PersonnelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Shift Schemas
class ShiftBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    start_time: str = Field(..., max_length=10)
    end_time: str = Field(..., max_length=10)
    description: Optional[str] = None
    active: Optional[int] = 1


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    start_time: Optional[str] = Field(None, max_length=10)
    end_time: Optional[str] = Field(None, max_length=10)
    description: Optional[str] = None
    active: Optional[int] = None


class ShiftResponse(ShiftBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Routing Item Schema
class RoutingItemBase(BaseModel):
    operation_id: int
    sequence: int
    equipment_id: Optional[int] = None
    standard_time: Optional[float] = 0
    setup_time: Optional[float] = 0
    description: Optional[str] = None


class RoutingItemCreate(RoutingItemBase):
    pass


class RoutingItemResponse(RoutingItemBase):
    id: int
    routing_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Routing Schemas
class RoutingBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    product_id: int
    version: Optional[str] = "1.0"
    is_active: Optional[int] = 1
    description: Optional[str] = None


class RoutingCreate(RoutingBase):
    items: Optional[List[RoutingItemCreate]] = []


class RoutingUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    product_id: Optional[int] = None
    version: Optional[str] = None
    is_active: Optional[int] = None
    description: Optional[str] = None
    items: Optional[List[RoutingItemCreate]] = None


class RoutingResponse(RoutingBase):
    id: int
    items: List[RoutingItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
