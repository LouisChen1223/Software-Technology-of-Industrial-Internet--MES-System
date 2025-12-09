from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


# 工单状态枚举
class WorkOrderStatus(str, enum.Enum):
    DRAFT = "draft"  # 草稿
    RELEASED = "released"  # 已下达
    IN_PROGRESS = "in_progress"  # 进行中
    PAUSED = "paused"  # 暂停
    COMPLETED = "completed"  # 完成
    CANCELLED = "cancelled"  # 取消


# 工单表
class WorkOrder(Base):
    __tablename__ = "work_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("materials.id"))
    bom_id = Column(Integer, ForeignKey("boms.id"), nullable=True)
    routing_id = Column(Integer, ForeignKey("routings.id"), nullable=True)
    planned_quantity = Column(Float, nullable=False)
    completed_quantity = Column(Float, default=0)
    scrapped_quantity = Column(Float, default=0)
    status = Column(String(20), default=WorkOrderStatus.DRAFT.value)
    priority = Column(Integer, default=5)  # 1-10, 越小优先级越高
    planned_start_date = Column(DateTime)
    planned_end_date = Column(DateTime)
    actual_start_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)
    customer = Column(String(200))
    sales_order = Column(String(100))
    notes = Column(Text)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    product = relationship("Material")
    bom = relationship("BOM")
    routing = relationship("Routing")
    operations = relationship("WorkOrderOperation", back_populates="work_order", cascade="all, delete-orphan")
    reports = relationship("WorkReport", back_populates="work_order")
    material_picks = relationship("MaterialPick", back_populates="work_order")


# 工单工序表
class WorkOrderOperation(Base):
    __tablename__ = "work_order_operations"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"))
    operation_id = Column(Integer, ForeignKey("operations.id"))
    sequence = Column(Integer, nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    planned_quantity = Column(Float, nullable=False)
    completed_quantity = Column(Float, default=0)
    scrapped_quantity = Column(Float, default=0)
    status = Column(String(20), default="pending")  # pending, in_progress, completed
    planned_start_date = Column(DateTime)
    planned_end_date = Column(DateTime)
    actual_start_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    work_order = relationship("WorkOrder", back_populates="operations")
    operation = relationship("Operation")
    equipment = relationship("Equipment")
    reports = relationship("WorkReport", back_populates="work_order_operation")


# 报工类型枚举
class ReportType(str, enum.Enum):
    START = "start"  # 开工
    COMPLETE = "complete"  # 完工
    PAUSE = "pause"  # 暂停
    RESUME = "resume"  # 恢复
    SCRAP = "scrap"  # 报废


# 报工记录表
class WorkReport(Base):
    __tablename__ = "work_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"))
    work_order_operation_id = Column(Integer, ForeignKey("work_order_operations.id"))
    report_type = Column(String(20), nullable=False)  # start, complete, pause, resume, scrap
    quantity = Column(Float, default=0)
    operator_id = Column(Integer, ForeignKey("personnel.id"), nullable=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True)
    barcode = Column(String(200))  # 扫码内容
    notes = Column(Text)
    report_time = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    work_order = relationship("WorkOrder", back_populates="reports")
    work_order_operation = relationship("WorkOrderOperation", back_populates="reports")
    operator = relationship("Personnel")
    equipment = relationship("Equipment")
    shift = relationship("Shift")


# 在制品追溯表
class WIPTracking(Base):
    __tablename__ = "wip_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"))
    operation_id = Column(Integer, ForeignKey("operations.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    batch_number = Column(String(100))
    serial_number = Column(String(100))
    quantity = Column(Float, nullable=False)
    status = Column(String(20), default="wip")  # wip, completed, scrapped
    location = Column(String(200))
    operator_id = Column(Integer, ForeignKey("personnel.id"), nullable=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    work_order = relationship("WorkOrder")
    operation = relationship("Operation")
    material = relationship("Material")
    operator = relationship("Personnel")
    equipment = relationship("Equipment")


from app.models.master import Material, BOM, Routing, Operation, Equipment, Personnel, Shift
