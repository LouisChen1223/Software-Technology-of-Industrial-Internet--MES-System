from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List
from datetime import datetime
from app.database import get_db
import logging

logger = logging.getLogger(__name__)
from app.models.inventory import (
    Inventory, MaterialTransaction, MaterialPick, MaterialPickItem
)
from app.models.master import Material, Warehouse, BOM, BOMItem
from app.models.workorder import WorkOrder
from app.schemas.inventory import (
    InventoryCreate, InventoryUpdate, InventoryResponse,
    MaterialTransactionCreate, MaterialTransactionResponse,
    MaterialPickCreate, MaterialPickUpdate, MaterialPickResponse,
    InventoryQueryParams
)

router = APIRouter()


def _zone_prefix(wh: Warehouse) -> str:
    """从仓库表推断所属区的前缀字母，例如 'A区' -> 'A'。默认 'A'。"""
    if wh and wh.location:
        s = str(wh.location).strip()
        if s:
            return s[0].upper()
    return "A"


def _get_or_assign_location(db: Session, warehouse_id: int, material_id: int) -> str:
    """按规则分配库位：
    - 若同仓库+同物料已有任一记录带库位，则复用该库位（同物料同库位）。
    - 否则，根据仓库所在区生成新库位：'<区>-NN'，NN 为该区在本仓库现有最大编号+1。
    """
    # 先查已有库位
    existing = (
        db.query(Inventory.location)
        .filter(
            Inventory.warehouse_id == warehouse_id,
            Inventory.material_id == material_id,
            Inventory.location.isnot(None),
            func.trim(Inventory.location) != ""
        )
        .first()
    )
    if existing and existing[0]:
        return existing[0]

    # 没有则根据区生成新库位
    wh = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    prefix = _zone_prefix(wh)

    # 找该仓库当前该区已使用的编号最大值
    rows = (
        db.query(Inventory.location)
        .filter(
            Inventory.warehouse_id == warehouse_id,
            Inventory.location.like(f"{prefix}-%")
        )
        .all()
    )

    max_no = 0
    for (loc,) in rows:
        try:
            part = str(loc).split("-", 1)[1]
            num = int(part)
            if num > max_no:
                max_no = num
        except Exception:
            continue

    return f"{prefix}-{max_no + 1:02d}"


# ==================== Inventory APIs ====================
@router.post("/inventory", response_model=InventoryResponse, tags=["Inventory"])
def create_inventory(inventory: InventoryCreate, db: Session = Depends(get_db)):
    """创建库存记录"""
    db_inventory = Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


@router.get("/inventory", response_model=List[InventoryResponse], tags=["Inventory"])
def get_inventory(
    skip: int = 0,
    limit: int = 100,
    warehouse_id: int = None,
    material_id: int = None,
    batch_number: str = None,
    location: str = None,
    db: Session = Depends(get_db)
):
    """查询库存"""
    query = db.query(Inventory)
    
    if warehouse_id:
        query = query.filter(Inventory.warehouse_id == warehouse_id)
    if material_id:
        query = query.filter(Inventory.material_id == material_id)
    if batch_number:
        query = query.filter(Inventory.batch_number == batch_number)
    if location:
        query = query.filter(Inventory.location.like(f"%{location}%"))
    
    return query.offset(skip).limit(limit).all()


@router.get("/inventory/{inventory_id}", response_model=InventoryResponse, tags=["Inventory"])
def get_inventory_detail(inventory_id: int, db: Session = Depends(get_db)):
    """获取库存详情"""
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


@router.put("/inventory/{inventory_id}", response_model=InventoryResponse, tags=["Inventory"])
def update_inventory(inventory_id: int, inventory: InventoryUpdate, db: Session = Depends(get_db)):
    """更新库存"""
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    for key, value in inventory.dict(exclude_unset=True).items():
        setattr(db_inventory, key, value)
    
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


@router.get("/inventory/summary/by-warehouse", tags=["Inventory"])
def get_inventory_summary_by_warehouse(db: Session = Depends(get_db)):
    """按仓库汇总库存"""
    from sqlalchemy import func
    
    result = db.query(
        Inventory.warehouse_id,
        Warehouse.name.label("warehouse_name"),
        func.count(Inventory.id).label("item_count"),
        func.sum(Inventory.quantity).label("total_quantity")
    ).join(Warehouse).group_by(Inventory.warehouse_id, Warehouse.name).all()
    
    return [
        {
            "warehouse_id": r.warehouse_id,
            "warehouse_name": r.warehouse_name,
            "item_count": r.item_count,
            "total_quantity": float(r.total_quantity) if r.total_quantity else 0
        }
        for r in result
    ]


@router.get("/inventory/summary/by-material", tags=["Inventory"])
def get_inventory_summary_by_material(db: Session = Depends(get_db)):
    """按物料汇总库存"""
    from sqlalchemy import func
    
    result = db.query(
        Inventory.material_id,
        Material.code.label("material_code"),
        Material.name.label("material_name"),
        func.sum(Inventory.quantity).label("total_quantity"),
        func.sum(Inventory.available_quantity).label("total_available")
    ).join(Material).group_by(
        Inventory.material_id, Material.code, Material.name
    ).all()
    
    return [
        {
            "material_id": r.material_id,
            "material_code": r.material_code,
            "material_name": r.material_name,
            "total_quantity": float(r.total_quantity) if r.total_quantity else 0,
            "total_available": float(r.total_available) if r.total_available else 0
        }
        for r in result
    ]


# ==================== Material Transaction APIs ====================
@router.post("/material-transactions", response_model=MaterialTransactionResponse, tags=["Inventory"])
def create_material_transaction(transaction: MaterialTransactionCreate, db: Session = Depends(get_db)):
    """创建物料事务"""
    logger.info(f"物料事务: 类型={transaction.transaction_type}, 物料ID={transaction.material_id}, 数量={transaction.quantity}")
    
    # 创建事务记录
    trans_data = transaction.dict()
    if not trans_data.get('transaction_date'):
        trans_data['transaction_date'] = datetime.now()
    
    # 对于入库类事务（receive/return），若未指定库位：
    # 1) 同仓库+同物料已有库位 -> 复用
    # 2) 否则按仓库所属区生成新库位（如 A-06）
    if transaction.transaction_type in ["return", "receive"]:
        if not trans_data.get("to_location") or str(trans_data.get("to_location")).strip() == "":
            trans_data["to_location"] = _get_or_assign_location(db, transaction.warehouse_id, transaction.material_id)
    
    db_trans = MaterialTransaction(**trans_data)
    db.add(db_trans)
    
    # 更新库存
    inventory = db.query(Inventory).filter(
        and_(
            Inventory.material_id == transaction.material_id,
            Inventory.warehouse_id == transaction.warehouse_id,
            Inventory.batch_number == transaction.batch_number
        )
    ).first()
    
    if transaction.transaction_type in ["pick", "issue"]:
        # 出库
        if not inventory or inventory.available_quantity < transaction.quantity:
            raise HTTPException(status_code=400, detail="Insufficient inventory")
        inventory.quantity -= transaction.quantity
        inventory.available_quantity -= transaction.quantity
    elif transaction.transaction_type in ["return", "receive"]:
        # 入库
        if not inventory:
            # 创建新库存记录
            inventory = Inventory(
                material_id=transaction.material_id,
                warehouse_id=transaction.warehouse_id,
                batch_number=transaction.batch_number,
                quantity=transaction.quantity,
                available_quantity=transaction.quantity,
                location=trans_data.get("to_location"),
                unit_price=transaction.unit_price
            )
            db.add(inventory)
        else:
            # 累加库存与可用数量；若原先无库位而本次有库位，则补齐库位
            inventory.quantity += transaction.quantity
            inventory.available_quantity += transaction.quantity
            if (not inventory.location or str(inventory.location).strip() == "") and trans_data.get("to_location"):
                inventory.location = trans_data.get("to_location")
    db.commit()
    db.refresh(db_trans)
    logger.info(f"✓ 物料事务完成: ID={db_trans.id}, 类型={transaction.transaction_type}")
    return db_trans


@router.get("/material-transactions", response_model=List[MaterialTransactionResponse], tags=["Inventory"])

@router.get("/material-transactions", response_model=List[MaterialTransactionResponse], tags=["Inventory"])
def get_material_transactions(
    skip: int = 0,
    limit: int = 100,
    material_id: int = None,
    warehouse_id: int = None,
    work_order_id: int = None,
    transaction_type: str = None,
    db: Session = Depends(get_db)
):
    """获取物料事务列表"""
    query = db.query(MaterialTransaction)
    
    if material_id:
        query = query.filter(MaterialTransaction.material_id == material_id)
    if warehouse_id:
        query = query.filter(MaterialTransaction.warehouse_id == warehouse_id)
    if work_order_id:
        query = query.filter(MaterialTransaction.work_order_id == work_order_id)
    if transaction_type:
        query = query.filter(MaterialTransaction.transaction_type == transaction_type)
    
    return query.order_by(MaterialTransaction.transaction_date.desc()).offset(skip).limit(limit).all()


@router.post("/material-picks", response_model=MaterialPickResponse, tags=["Inventory"])
def create_material_pick(pick: MaterialPickCreate, db: Session = Depends(get_db)):
    """创建领料单"""
    logger.info(f"创建领料单: {pick.code}, 工单ID={pick.work_order_id}, 类型={pick.pick_type}")
    
    pick_data = pick.dict(exclude={'items'})
    if not pick_data.get('request_date'):
        pick_data['request_date'] = datetime.now()
    
    db_pick = MaterialPick(**pick_data)
    db.add(db_pick)
    db.flush()
    
    # 添加领料单明细
    for item in pick.items:
        pick_item = MaterialPickItem(
            pick_id=db_pick.id,
            material_id=item.material_id,
            quantity=item.quantity,
            uom_id=item.uom_id,
            warehouse_id=item.warehouse_id
        )
        db.add(pick_item)
    
    db.commit()
    db.refresh(db_pick)
    logger.info(f"✓ 领料单创建成功: ID={db_pick.id}, 编号={db_pick.code}, 明细数={len(pick.items)}")
    return db_pick


@router.get("/material-picks", response_model=List[MaterialPickResponse], tags=["Inventory"])
def get_material_picks(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    work_order_id: int = None,
    db: Session = Depends(get_db)
):
    """获取领料单列表"""
    query = db.query(MaterialPick)
    
    if status:
        query = query.filter(MaterialPick.status == status)
    if work_order_id:
        query = query.filter(MaterialPick.work_order_id == work_order_id)
    
    return query.order_by(MaterialPick.request_date.desc()).offset(skip).limit(limit).all()


@router.get("/material-picks/{pick_id}", response_model=MaterialPickResponse, tags=["Inventory"])
def get_material_pick(pick_id: int, db: Session = Depends(get_db)):
    """获取领料单详情"""
    pick = db.query(MaterialPick).filter(MaterialPick.id == pick_id).first()
    if not pick:
        raise HTTPException(status_code=404, detail="Material Pick not found")
    return pick


@router.put("/material-picks/{pick_id}", response_model=MaterialPickResponse, tags=["Inventory"])
def update_material_pick(pick_id: int, pick: MaterialPickUpdate, db: Session = Depends(get_db)):
    """更新领料单"""
    db_pick = db.query(MaterialPick).filter(MaterialPick.id == pick_id).first()
    if not db_pick:
        raise HTTPException(status_code=404, detail="Material Pick not found")
    
    for key, value in pick.dict(exclude_unset=True).items():
        setattr(db_pick, key, value)
    
    db.commit()
    db.refresh(db_pick)
    return db_pick


@router.post("/material-picks/{pick_id}/confirm", response_model=MaterialPickResponse, tags=["Inventory"])
def confirm_material_pick(pick_id: int, db: Session = Depends(get_db)):
    """确认领料单"""
    db_pick = db.query(MaterialPick).filter(MaterialPick.id == pick_id).first()
    if not db_pick:
        raise HTTPException(status_code=404, detail="Material Pick not found")
    
    if db_pick.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft picks can be confirmed")
    
    db_pick.status = "confirmed"
    db.commit()
    db.refresh(db_pick)
    return db_pick


@router.post("/material-picks/{pick_id}/complete", response_model=MaterialPickResponse, tags=["Inventory"])
def complete_material_pick(pick_id: int, db: Session = Depends(get_db)):
    """完成领料（实际出库）"""
    db_pick = db.query(MaterialPick).filter(MaterialPick.id == pick_id).first()
    if not db_pick:
        raise HTTPException(status_code=404, detail="Material Pick not found")
    
    if db_pick.status != "confirmed":
        raise HTTPException(status_code=400, detail="Only confirmed picks can be completed")
    
    # 创建物料事务并更新库存
    for item in db_pick.items:
        transaction = MaterialTransaction(
            transaction_type="pick",
            material_id=item.material_id,
            warehouse_id=db_pick.warehouse_id,
            work_order_id=db_pick.work_order_id,
            batch_number=item.batch_number,
            quantity=item.picked_quantity,
            from_location=item.location,
            operator_id=db_pick.picker_id,
            reference_no=db_pick.code,
            transaction_date=datetime.now()
        )
        db.add(transaction)
        
        # 更新库存
        inventory = db.query(Inventory).filter(
            and_(
                Inventory.material_id == item.material_id,
                Inventory.warehouse_id == db_pick.warehouse_id,
                Inventory.batch_number == item.batch_number
            )
        ).first()
        
        if inventory:
            inventory.quantity -= item.picked_quantity
            inventory.available_quantity -= item.picked_quantity
    
    db_pick.status = "completed"
    db_pick.pick_date = datetime.now()
    
    db.commit()
    db.refresh(db_pick)
    return db_pick


@router.post("/material-picks/bom", response_model=MaterialPickResponse, tags=["Inventory"])
def create_material_pick_from_bom(
    work_order_id: int,
    warehouse_id: int,
    db: Session = Depends(get_db)
):
    """按BOM自动生成领料单"""
    # 获取工单
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Work Order not found")
    
    if not work_order.bom_id:
        raise HTTPException(status_code=400, detail="Work Order has no BOM")
    
    # 获取BOM
    bom = db.query(BOM).filter(BOM.id == work_order.bom_id).first()
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    
    # 生成领料单编号
    import random
    pick_code = f"PICK-{work_order.code}-{random.randint(1000, 9999)}"
    
    # 创建领料单
    db_pick = MaterialPick(
        code=pick_code,
        work_order_id=work_order_id,
        warehouse_id=warehouse_id,
        pick_type="bom",
        status="draft",
        request_date=datetime.now()
    )
    db.add(db_pick)
    db.flush()
    
    # 根据BOM明细添加领料项
    for bom_item in bom.items:
        required_qty = bom_item.quantity * work_order.planned_quantity * (1 + bom_item.scrap_rate)
        
        pick_item = MaterialPickItem(
            pick_id=db_pick.id,
            material_id=bom_item.material_id,
            required_quantity=required_qty,
            picked_quantity=0
        )
        db.add(pick_item)
    
    db.commit()
    db.refresh(db_pick)
    return db_pick


@router.post("/material-returns", tags=["Inventory"])
def return_material(
    material_id: int,
    warehouse_id: int,
    work_order_id: int = None,
    batch_number: str = None,
    quantity: float = 0,
    location: str = None,
    operator_id: int = None,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """退料"""
    # 创建退料事务
    transaction = MaterialTransaction(
        transaction_type="return",
        material_id=material_id,
        warehouse_id=warehouse_id,
        work_order_id=work_order_id,
        batch_number=batch_number,
        quantity=quantity,
        to_location=location,
        operator_id=operator_id,
        notes=notes,
        transaction_date=datetime.now()
    )
    db.add(transaction)
    
    # 更新库存
    inventory = db.query(Inventory).filter(
        and_(
            Inventory.material_id == material_id,
            Inventory.warehouse_id == warehouse_id,
            Inventory.batch_number == batch_number
        )
    ).first()
    
    if not inventory:
        # 创建新库存记录
        inventory = Inventory(
            material_id=material_id,
            warehouse_id=warehouse_id,
            batch_number=batch_number,
            quantity=quantity,
            available_quantity=quantity,
            location=location
        )
        db.add(inventory)
    else:
        inventory.quantity += quantity
        inventory.available_quantity += quantity
    
    db.commit()
    return {"message": "Material returned successfully", "transaction_id": transaction.id}
