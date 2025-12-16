from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


# Work Order Operation Schema
class WorkOrderOperationBase(BaseModel):
    operation_id: int
    sequence: int
    equipment_id: Optional[int] = None
    planned_quantity: float
    completed_quantity: Optional[float] = 0
    scrapped_quantity: Optional[float] = 0
    status: Optional[str] = "pending"
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None

    @validator('planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', pre=True, always=True)
    def round_to_hour(cls, v):
        if not v:
            return v
        # 支持字符串或 datetime，统一转为整点（分秒归零）
        dt = v if isinstance(v, datetime) else datetime.fromisoformat(v)
        return dt.replace(minute=0, second=0, microsecond=0)


class WorkOrderOperationCreate(WorkOrderOperationBase):
    pass


class WorkOrderOperationResponse(WorkOrderOperationBase):
    id: int
    work_order_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Work Order Schemas
class WorkOrderBase(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    product_id: int
    bom_id: Optional[int] = None
    routing_id: Optional[int] = None
    planned_quantity: float
    completed_quantity: Optional[float] = 0
    scrapped_quantity: Optional[float] = 0
    status: Optional[str] = "draft"
    priority: Optional[int] = 5
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    customer: Optional[str] = None
    sales_order: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None

    @validator('planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', pre=True, always=True)
    def round_to_hour(cls, v):
        if not v:
            return v
        dt = v if isinstance(v, datetime) else datetime.fromisoformat(v)
        return dt.replace(minute=0, second=0, microsecond=0)


class WorkOrderCreate(WorkOrderBase):
    operations: Optional[List[WorkOrderOperationCreate]] = []


class WorkOrderUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    product_id: Optional[int] = None
    bom_id: Optional[int] = None
    routing_id: Optional[int] = None
    planned_quantity: Optional[float] = None
    completed_quantity: Optional[float] = None
    scrapped_quantity: Optional[float] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    customer: Optional[str] = None
    sales_order: Optional[str] = None
    notes: Optional[str] = None

    @validator('planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', pre=True, always=True)
    def round_to_hour(cls, v):
        if not v:
            return v
        dt = v if isinstance(v, datetime) else datetime.fromisoformat(v)
        return dt.replace(minute=0, second=0, microsecond=0)


class WorkOrderResponse(WorkOrderBase):
    id: int
    operations: List[WorkOrderOperationResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Work Report Schemas
class WorkReportBase(BaseModel):
    work_order_id: int
    work_order_operation_id: Optional[int] = None
    report_type: str  # start, complete, pause, resume, scrap
    quantity: Optional[float] = 0
    operator_id: Optional[int] = None
    equipment_id: Optional[int] = None
    shift_id: Optional[int] = None
    barcode: Optional[str] = None
    notes: Optional[str] = None
    report_time: Optional[datetime] = None


class WorkReportCreate(WorkReportBase):
    pass


class WorkReportResponse(WorkReportBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Nested schemas for WIP Tracking
class WorkOrderSimple(BaseModel):
    """工单简化信息"""
    id: int
    code: str
    product_id: int
    planned_quantity: float
    status: str
    
    class Config:
        from_attributes = True


class OperationSimple(BaseModel):
    """工序简化信息"""
    id: int
    code: str
    name: str
    operation_type: Optional[str] = None
    
    class Config:
        from_attributes = True


# WIP Tracking Schemas
class WIPTrackingBase(BaseModel):
    work_order_id: int
    operation_id: int
    material_id: int
    batch_number: Optional[str] = None
    serial_number: Optional[str] = None
    quantity: float
    status: Optional[str] = "wip"
    location: Optional[str] = None
    operator_id: Optional[int] = None
    equipment_id: Optional[int] = None


class WIPTrackingCreate(WIPTrackingBase):
    pass


class WIPTrackingUpdate(BaseModel):
    batch_number: Optional[str] = None
    serial_number: Optional[str] = None
    quantity: Optional[float] = None
    status: Optional[str] = None
    location: Optional[str] = None
    operator_id: Optional[int] = None
    equipment_id: Optional[int] = None


class WIPTrackingResponse(WIPTrackingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # 添加关联对象
    work_order: Optional[WorkOrderSimple] = None
    operation: Optional[OperationSimple] = None

    class Config:
        from_attributes = True
