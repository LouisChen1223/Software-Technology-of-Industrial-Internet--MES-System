from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


# 库存表
class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    batch_number = Column(String(100))
    quantity = Column(Float, default=0)
    available_quantity = Column(Float, default=0)  # 可用数量
    allocated_quantity = Column(Float, default=0)  # 已分配数量
    location = Column(String(100))  # 库位
    unit_price = Column(Float, default=0)
    production_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    warehouse = relationship("Warehouse", back_populates="inventory_items")
    material = relationship("Material", back_populates="inventory_items")


# 物料交易类型
class TransactionType(str, enum.Enum):
    PICK = "pick"  # 领料
    RETURN = "return"  # 退料
    ISSUE = "issue"  # 发料
    RECEIVE = "receive"  # 收货
    ADJUST = "adjust"  # 调整
    TRANSFER = "transfer"  # 转移


# 物料事务表
class MaterialTransaction(Base):
    __tablename__ = "material_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String(20), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=True)
    batch_number = Column(String(100))
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, default=0)
    from_location = Column(String(100))
    to_location = Column(String(100))
    operator_id = Column(Integer, ForeignKey("personnel.id"), nullable=True)
    reference_no = Column(String(100))  # 参考单号
    notes = Column(Text)
    transaction_date = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    material = relationship("Material")
    warehouse = relationship("Warehouse")
    work_order = relationship("WorkOrder")
    operator = relationship("Personnel")


# 领料单表
class MaterialPick(Base):
    __tablename__ = "material_picks"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    pick_type = Column(String(20), default="normal")  # normal, bom
    status = Column(String(20), default="draft")  # draft, confirmed, completed, cancelled
    requester_id = Column(Integer, ForeignKey("personnel.id"), nullable=True)
    picker_id = Column(Integer, ForeignKey("personnel.id"), nullable=True)
    request_date = Column(DateTime, default=datetime.now)
    pick_date = Column(DateTime, nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    work_order = relationship("WorkOrder", back_populates="material_picks")
    warehouse = relationship("Warehouse")
    requester = relationship("Personnel", foreign_keys=[requester_id])
    picker = relationship("Personnel", foreign_keys=[picker_id])
    items = relationship("MaterialPickItem", back_populates="pick", cascade="all, delete-orphan")


# 领料单明细表
class MaterialPickItem(Base):
    __tablename__ = "material_pick_items"
    
    id = Column(Integer, primary_key=True, index=True)
    pick_id = Column(Integer, ForeignKey("material_picks.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    batch_number = Column(String(100))
    required_quantity = Column(Float, nullable=False)
    picked_quantity = Column(Float, default=0)
    location = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    pick = relationship("MaterialPick", back_populates="items")
    material = relationship("Material")


from app.models.master import Material, Warehouse, Personnel
from app.models.workorder import WorkOrder
