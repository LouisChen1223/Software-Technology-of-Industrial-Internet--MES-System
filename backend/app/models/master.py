from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


# 单位表
class UOM(Base):
    __tablename__ = "uoms"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    precision = Column(Float, default=0)
    active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# 仓库表
class Warehouse(Base):
    __tablename__ = "warehouses"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200))
    warehouse_type = Column(String(50))  # 原料仓、成品仓、在制品仓等
    manager = Column(String(100))
    description = Column(Text)
    active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    inventory_items = relationship("Inventory", back_populates="warehouse")


# 物料表
class Material(Base):
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    specification = Column(String(200))
    material_type = Column(String(50))  # 原料、半成品、成品等
    uom_id = Column(Integer, ForeignKey("uoms.id"))
    unit_price = Column(Float, default=0)
    safety_stock = Column(Float, default=0)
    lead_time = Column(Integer, default=0)  # 提前期(天)
    supplier = Column(String(200))
    description = Column(Text)
    active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    uom = relationship("UOM")
    bom_items = relationship("BOMItem", back_populates="material", foreign_keys="BOMItem.material_id")
    inventory_items = relationship("Inventory", back_populates="material")


# BOM表头
class BOM(Base):
    __tablename__ = "boms"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    product_id = Column(Integer, ForeignKey("materials.id"))
    version = Column(String(20), default="1.0")
    quantity = Column(Float, default=1)  # 产出数量
    is_active = Column(Integer, default=1)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    product = relationship("Material", foreign_keys=[product_id])
    items = relationship("BOMItem", back_populates="bom", cascade="all, delete-orphan")


# BOM明细
class BOMItem(Base):
    __tablename__ = "bom_items"
    
    id = Column(Integer, primary_key=True, index=True)
    bom_id = Column(Integer, ForeignKey("boms.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    quantity = Column(Float, nullable=False)
    sequence = Column(Integer, default=0)
    scrap_rate = Column(Float, default=0)  # 损耗率
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    bom = relationship("BOM", back_populates="items")
    material = relationship("Material", foreign_keys=[material_id])


# 工序表
class Operation(Base):
    __tablename__ = "operations"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    operation_type = Column(String(50))  # 加工、装配、检验等
    standard_time = Column(Float, default=0)  # 标准工时(分钟)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    routing_items = relationship("RoutingItem", back_populates="operation")


# 设备表
class Equipment(Base):
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    equipment_type = Column(String(50))
    model = Column(String(100))
    manufacturer = Column(String(200))
    capacity = Column(Float, default=0)  # 产能
    status = Column(String(20), default="idle")  # idle, running, maintenance, fault
    location = Column(String(200))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# 工装表
class Tooling(Base):
    __tablename__ = "tooling"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    tooling_type = Column(String(50))
    specification = Column(String(200))
    quantity = Column(Integer, default=0)
    status = Column(String(20), default="available")  # available, in-use, maintenance
    location = Column(String(200))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# 人员表
class Personnel(Base):
    __tablename__ = "personnel"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100))
    position = Column(String(100))
    skill_level = Column(String(50))
    phone = Column(String(20))
    email = Column(String(100))
    shift_code = Column(String(50))
    status = Column(String(20), default="active")  # active, inactive
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# 班次表
class Shift(Base):
    __tablename__ = "shifts"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    start_time = Column(String(10), nullable=False)  # HH:MM
    end_time = Column(String(10), nullable=False)  # HH:MM
    description = Column(Text)
    active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# 工艺路线表头
class Routing(Base):
    __tablename__ = "routings"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    product_id = Column(Integer, ForeignKey("materials.id"))
    version = Column(String(20), default="1.0")
    is_active = Column(Integer, default=1)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    product = relationship("Material")
    items = relationship("RoutingItem", back_populates="routing", cascade="all, delete-orphan")


# 工艺路线明细
class RoutingItem(Base):
    __tablename__ = "routing_items"
    
    id = Column(Integer, primary_key=True, index=True)
    routing_id = Column(Integer, ForeignKey("routings.id"))
    operation_id = Column(Integer, ForeignKey("operations.id"))
    sequence = Column(Integer, nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    standard_time = Column(Float, default=0)  # 标准工时(分钟)
    setup_time = Column(Float, default=0)  # 准备时间(分钟)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    routing = relationship("Routing", back_populates="items")
    operation = relationship("Operation")
    equipment = relationship("Equipment")
