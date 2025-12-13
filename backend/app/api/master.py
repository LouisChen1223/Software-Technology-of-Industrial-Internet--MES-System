from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
import logging

logger = logging.getLogger(__name__)
from app.models.master import (
    UOM, Warehouse, Material, BOM, BOMItem, 
    Operation, Equipment, Tooling, Personnel, Shift, Routing, RoutingItem
)
from app.models.material_type import MaterialType
from app.schemas.master import (
    UOMCreate, UOMUpdate, UOMResponse,
    MaterialTypeCreate, MaterialTypeUpdate, MaterialTypeResponse,
    WarehouseCreate, WarehouseUpdate, WarehouseResponse,
    MaterialCreate, MaterialUpdate, MaterialResponse,
    BOMCreate, BOMUpdate, BOMResponse,
    OperationCreate, OperationUpdate, OperationResponse,
    EquipmentCreate, EquipmentUpdate, EquipmentResponse,
    ToolingCreate, ToolingUpdate, ToolingResponse,
    PersonnelCreate, PersonnelUpdate, PersonnelResponse,
    ShiftCreate, ShiftUpdate, ShiftResponse,
    RoutingCreate, RoutingUpdate, RoutingResponse
)

router = APIRouter()


# ==================== UOM APIs ====================
@router.post("/uoms", response_model=UOMResponse, tags=["Master Data"])
def create_uom(uom: UOMCreate, db: Session = Depends(get_db)):
    """创建单位"""
    logger.info(f"创建单位: {uom.code} - {uom.name}")
    db_uom = UOM(**uom.dict())
    db.add(db_uom)
    db.commit()
    db.refresh(db_uom)
    logger.info(f"✓ 单位创建成功: ID={db_uom.id}")
    return db_uom


@router.get("/uoms", response_model=List[UOMResponse], tags=["Master Data"])
def get_uoms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取单位列表"""
    return db.query(UOM).offset(skip).limit(limit).all()


@router.get("/uoms/{uom_id}", response_model=UOMResponse, tags=["Master Data"])
def get_uom(uom_id: int, db: Session = Depends(get_db)):
    """获取单位详情"""
    uom = db.query(UOM).filter(UOM.id == uom_id).first()
    if not uom:
        raise HTTPException(status_code=404, detail="UOM not found")
    return uom


@router.put("/uoms/{uom_id}", response_model=UOMResponse, tags=["Master Data"])
def update_uom(uom_id: int, uom: UOMUpdate, db: Session = Depends(get_db)):
    """更新单位"""
    db_uom = db.query(UOM).filter(UOM.id == uom_id).first()
    if not db_uom:
        raise HTTPException(status_code=404, detail="UOM not found")
    
    for key, value in uom.dict(exclude_unset=True).items():
        setattr(db_uom, key, value)
    
    db.commit()
    db.refresh(db_uom)
    return db_uom


@router.delete("/uoms/{uom_id}", tags=["Master Data"])
def delete_uom(uom_id: int, db: Session = Depends(get_db)):
    """删除单位"""
    db_uom = db.query(UOM).filter(UOM.id == uom_id).first()
    if not db_uom:
        raise HTTPException(status_code=404, detail="UOM not found")
    
    db.delete(db_uom)
    db.commit()
    return {"message": "UOM deleted successfully"}


# ==================== Material Type APIs ====================
@router.post("/material-types", response_model=MaterialTypeResponse, tags=["Master Data"])
def create_material_type(material_type: MaterialTypeCreate, db: Session = Depends(get_db)):
    """创建物料类型"""
    logger.info(f"创建物料类型: {material_type.code} - {material_type.name}")
    db_type = MaterialType(**material_type.dict())
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type


@router.get("/material-types", response_model=List[MaterialTypeResponse], tags=["Master Data"])
def get_material_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取物料类型列表"""
    return db.query(MaterialType).offset(skip).limit(limit).all()


@router.get("/material-types/{type_id}", response_model=MaterialTypeResponse, tags=["Master Data"])
def get_material_type(type_id: int, db: Session = Depends(get_db)):
    """获取物料类型详情"""
    mt = db.query(MaterialType).filter(MaterialType.id == type_id).first()
    if not mt:
        raise HTTPException(status_code=404, detail="Material type not found")
    return mt


@router.put("/material-types/{type_id}", response_model=MaterialTypeResponse, tags=["Master Data"])
def update_material_type(type_id: int, material_type: MaterialTypeUpdate, db: Session = Depends(get_db)):
    """更新物料类型"""
    db_type = db.query(MaterialType).filter(MaterialType.id == type_id).first()
    if not db_type:
        raise HTTPException(status_code=404, detail="Material type not found")

    for key, value in material_type.dict(exclude_unset=True).items():
        setattr(db_type, key, value)

    db.commit()
    db.refresh(db_type)
    return db_type


@router.delete("/material-types/{type_id}", tags=["Master Data"])
def delete_material_type(type_id: int, db: Session = Depends(get_db)):
    """删除物料类型"""
    db_type = db.query(MaterialType).filter(MaterialType.id == type_id).first()
    if not db_type:
        raise HTTPException(status_code=404, detail="Material type not found")

    db.delete(db_type)
    db.commit()
    return {"message": "Material type deleted successfully"}


# ==================== Warehouse APIs ====================
@router.post("/warehouses", response_model=WarehouseResponse, tags=["Master Data"])
def create_warehouse(warehouse: WarehouseCreate, db: Session = Depends(get_db)):
    """创建仓库"""
    db_warehouse = Warehouse(**warehouse.dict())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


@router.get("/warehouses", response_model=List[WarehouseResponse], tags=["Master Data"])
def get_warehouses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取仓库列表"""
    return db.query(Warehouse).offset(skip).limit(limit).all()


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseResponse, tags=["Master Data"])
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    """获取仓库详情"""
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@router.put("/warehouses/{warehouse_id}", response_model=WarehouseResponse, tags=["Master Data"])
def update_warehouse(warehouse_id: int, warehouse: WarehouseUpdate, db: Session = Depends(get_db)):
    """更新仓库"""
    db_warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not db_warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    for key, value in warehouse.dict(exclude_unset=True).items():
        setattr(db_warehouse, key, value)
    
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


@router.delete("/warehouses/{warehouse_id}", tags=["Master Data"])
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    """删除仓库"""
    db_warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not db_warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    db.delete(db_warehouse)
    db.commit()
    return {"message": "Warehouse deleted successfully"}


# ==================== Material APIs ====================
@router.post("/materials", response_model=MaterialResponse, tags=["Master Data"])
def create_material(material: MaterialCreate, db: Session = Depends(get_db)):
    """创建物料"""
    # 校验：禁止使用未启用的计量单位
    if material.uom_id is not None:
        uom = db.query(UOM).filter(UOM.id == material.uom_id).first()
        if not uom:
            raise HTTPException(status_code=400, detail="计量单位不存在")
        # active 列为 0 表示未启用
        if getattr(uom, "active", 1) == 0:
            raise HTTPException(status_code=400, detail="计量单位未启用，不能用于物料")
    db_material = Material(**material.dict())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material


@router.get("/materials", response_model=List[MaterialResponse], tags=["Master Data"])
def get_materials(
    skip: int = 0, 
    limit: int = 100, 
    material_type: str = None,
    db: Session = Depends(get_db)
):
    """获取物料列表"""
    query = db.query(Material)
    if material_type:
        query = query.filter(Material.material_type == material_type)
    return query.offset(skip).limit(limit).all()


@router.get("/materials/{material_id}", response_model=MaterialResponse, tags=["Master Data"])
def get_material(material_id: int, db: Session = Depends(get_db)):
    """获取物料详情"""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.put("/materials/{material_id}", response_model=MaterialResponse, tags=["Master Data"])
def update_material(material_id: int, material: MaterialUpdate, db: Session = Depends(get_db)):
    """更新物料"""
    db_material = db.query(Material).filter(Material.id == material_id).first()
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    update_data = material.dict(exclude_unset=True)
    # 若更新了计量单位，禁止选择未启用的计量单位
    new_uom_id = update_data.get("uom_id")
    if new_uom_id is not None:
        uom = db.query(UOM).filter(UOM.id == new_uom_id).first()
        if not uom:
            raise HTTPException(status_code=400, detail="计量单位不存在")
        if getattr(uom, "active", 1) == 0:
            raise HTTPException(status_code=400, detail="计量单位未启用，不能用于物料")

    for key, value in update_data.items():
        setattr(db_material, key, value)
    
    db.commit()
    db.refresh(db_material)
    return db_material


@router.delete("/materials/{material_id}", tags=["Master Data"])
def delete_material(material_id: int, db: Session = Depends(get_db)):
    """删除物料"""
    db_material = db.query(Material).filter(Material.id == material_id).first()
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    db.delete(db_material)
    db.commit()
    return {"message": "Material deleted successfully"}


# ==================== BOM APIs ====================
@router.post("/boms", response_model=BOMResponse, tags=["Master Data"])
def create_bom(bom: BOMCreate, db: Session = Depends(get_db)):
    """创建BOM"""
    # 约束：同一产品同一版本仅允许一个激活BOM
    bom_data = bom.dict(exclude={'items'})
    if bom_data.get("product_id") is None:
        raise HTTPException(status_code=400, detail="BOM缺少产品ID")
    # 若设置为激活版本，检查是否已存在激活版本
    if int(bom_data.get("is_active", 1)) == 1:
        exists_active = db.query(BOM).filter(
            BOM.product_id == bom_data["product_id"],
            BOM.is_active == 1
        ).first()
        if exists_active:
            raise HTTPException(status_code=400, detail="该产品已存在激活的BOM版本")
    db_bom = BOM(**bom_data)
    db.add(db_bom)
    db.flush()
    
    # 添加BOM明细
    for item in bom.items:
        db_item = BOMItem(**item.dict(), bom_id=db_bom.id)
        db.add(db_item)
    
    db.commit()
    db.refresh(db_bom)
    return db_bom


@router.get("/boms", response_model=List[BOMResponse], tags=["Master Data"])
def get_boms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取BOM列表"""
    return db.query(BOM).offset(skip).limit(limit).all()


@router.get("/boms/{bom_id}", response_model=BOMResponse, tags=["Master Data"])
def get_bom(bom_id: int, db: Session = Depends(get_db)):
    """获取BOM详情"""
    bom = db.query(BOM).filter(BOM.id == bom_id).first()
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    return bom


@router.put("/boms/{bom_id}", response_model=BOMResponse, tags=["Master Data"])
def update_bom(bom_id: int, bom: BOMUpdate, db: Session = Depends(get_db)):
    """更新BOM"""
    db_bom = db.query(BOM).filter(BOM.id == bom_id).first()
    if not db_bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    update_header = bom.dict(exclude_unset=True, exclude={'items'})
    # 若更新为激活状态，需确保产品不存在其他激活版本
    if update_header.get("is_active") is not None:
        new_active = int(update_header["is_active"]) == 1
        if new_active:
            exists_active = db.query(BOM).filter(
                BOM.product_id == (update_header.get("product_id") or db_bom.product_id),
                BOM.is_active == 1,
                BOM.id != bom_id
            ).first()
            if exists_active:
                raise HTTPException(status_code=400, detail="该产品已存在激活的BOM版本")
    # 更新BOM表头
    for key, value in update_header.items():
        setattr(db_bom, key, value)
    
    # 更新BOM明细
    if bom.items is not None:
        # 删除旧的明细
        db.query(BOMItem).filter(BOMItem.bom_id == bom_id).delete()
        # 添加新的明细
        for item in bom.items:
            db_item = BOMItem(**item.dict(), bom_id=bom_id)
            db.add(db_item)
    
    db.commit()
    db.refresh(db_bom)
    return db_bom

# BOM查询：根据产品获取激活版本或指定版本
@router.get("/boms/by-product/{product_id}", response_model=List[BOMResponse], tags=["Master Data"])
def get_boms_by_product(product_id: int, version: str = None, active_only: int = 0, db: Session = Depends(get_db)):
    """按产品筛选BOM，可选版本或仅激活。active_only=1时仅返回激活版本"""
    q = db.query(BOM).filter(BOM.product_id == product_id)
    if version:
        q = q.filter(BOM.version == version)
    if int(active_only) == 1:
        q = q.filter(BOM.is_active == 1)
    return q.all()


@router.delete("/boms/{bom_id}", tags=["Master Data"])
def delete_bom(bom_id: int, db: Session = Depends(get_db)):
    """删除BOM"""
    db_bom = db.query(BOM).filter(BOM.id == bom_id).first()
    if not db_bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    
    db.delete(db_bom)
    db.commit()
    return {"message": "BOM deleted successfully"}


# ==================== Operation APIs ====================
@router.post("/operations", response_model=OperationResponse, tags=["Master Data"])
def create_operation(operation: OperationCreate, db: Session = Depends(get_db)):
    """创建工序"""
    db_operation = Operation(**operation.dict())
    db.add(db_operation)
    db.commit()
    db.refresh(db_operation)
    return db_operation


@router.get("/operations", response_model=List[OperationResponse], tags=["Master Data"])
def get_operations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取工序列表"""
    return db.query(Operation).offset(skip).limit(limit).all()


@router.get("/operations/{operation_id}", response_model=OperationResponse, tags=["Master Data"])
def get_operation(operation_id: int, db: Session = Depends(get_db)):
    """获取工序详情"""
    operation = db.query(Operation).filter(Operation.id == operation_id).first()
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    return operation


@router.put("/operations/{operation_id}", response_model=OperationResponse, tags=["Master Data"])
def update_operation(operation_id: int, operation: OperationUpdate, db: Session = Depends(get_db)):
    """更新工序"""
    db_operation = db.query(Operation).filter(Operation.id == operation_id).first()
    if not db_operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    for key, value in operation.dict(exclude_unset=True).items():
        setattr(db_operation, key, value)
    
    db.commit()
    db.refresh(db_operation)
    return db_operation


@router.delete("/operations/{operation_id}", tags=["Master Data"])
def delete_operation(operation_id: int, db: Session = Depends(get_db)):
    """删除工序"""
    db_operation = db.query(Operation).filter(Operation.id == operation_id).first()
    if not db_operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    db.delete(db_operation)
    db.commit()
    return {"message": "Operation deleted successfully"}


# ==================== Equipment APIs ====================
@router.post("/equipment", response_model=EquipmentResponse, tags=["Master Data"])
def create_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    """创建设备"""
    db_equipment = Equipment(**equipment.dict())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment


@router.get("/equipment", response_model=List[EquipmentResponse], tags=["Master Data"])
def get_equipment_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取设备列表"""
    return db.query(Equipment).offset(skip).limit(limit).all()


@router.get("/equipment/{equipment_id}", response_model=EquipmentResponse, tags=["Master Data"])
def get_equipment(equipment_id: int, db: Session = Depends(get_db)):
    """获取设备详情"""
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@router.put("/equipment/{equipment_id}", response_model=EquipmentResponse, tags=["Master Data"])
def update_equipment(equipment_id: int, equipment: EquipmentUpdate, db: Session = Depends(get_db)):
    """更新设备"""
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    for key, value in equipment.dict(exclude_unset=True).items():
        setattr(db_equipment, key, value)
    
    db.commit()
    db.refresh(db_equipment)
    return db_equipment


@router.delete("/equipment/{equipment_id}", tags=["Master Data"])
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    """删除设备"""
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    db.delete(db_equipment)
    db.commit()
    return {"message": "Equipment deleted successfully"}


# ==================== Tooling APIs ====================
@router.post("/tooling", response_model=ToolingResponse, tags=["Master Data"])
def create_tooling(tooling: ToolingCreate, db: Session = Depends(get_db)):
    """创建工装"""
    db_tooling = Tooling(**tooling.dict())
    db.add(db_tooling)
    db.commit()
    db.refresh(db_tooling)
    return db_tooling


@router.get("/tooling", response_model=List[ToolingResponse], tags=["Master Data"])
def get_tooling_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取工装列表"""
    return db.query(Tooling).offset(skip).limit(limit).all()


@router.get("/tooling/{tooling_id}", response_model=ToolingResponse, tags=["Master Data"])
def get_tooling(tooling_id: int, db: Session = Depends(get_db)):
    """获取工装详情"""
    tooling = db.query(Tooling).filter(Tooling.id == tooling_id).first()
    if not tooling:
        raise HTTPException(status_code=404, detail="Tooling not found")
    return tooling


@router.put("/tooling/{tooling_id}", response_model=ToolingResponse, tags=["Master Data"])
def update_tooling(tooling_id: int, tooling: ToolingUpdate, db: Session = Depends(get_db)):
    """更新工装"""
    db_tooling = db.query(Tooling).filter(Tooling.id == tooling_id).first()
    if not db_tooling:
        raise HTTPException(status_code=404, detail="Tooling not found")
    
    for key, value in tooling.dict(exclude_unset=True).items():
        setattr(db_tooling, key, value)
    
    db.commit()
    db.refresh(db_tooling)
    return db_tooling


@router.delete("/tooling/{tooling_id}", tags=["Master Data"])
def delete_tooling(tooling_id: int, db: Session = Depends(get_db)):
    """删除工装"""
    db_tooling = db.query(Tooling).filter(Tooling.id == tooling_id).first()
    if not db_tooling:
        raise HTTPException(status_code=404, detail="Tooling not found")
    
    db.delete(db_tooling)
    db.commit()
    return {"message": "Tooling deleted successfully"}


# ==================== Personnel APIs ====================
@router.post("/personnel", response_model=PersonnelResponse, tags=["Master Data"])
def create_personnel(personnel: PersonnelCreate, db: Session = Depends(get_db)):
    """创建人员"""
    # 校验班次：若提供 shift_code，则必须存在且启用
    if getattr(personnel, "shift_code", None):
        shift = db.query(Shift).filter(Shift.code == personnel.shift_code).first()
        if not shift:
            raise HTTPException(status_code=400, detail="班次不存在")
        if getattr(shift, "active", 1) == 0:
            raise HTTPException(status_code=400, detail="班次未启用，不能选择")
    db_personnel = Personnel(**personnel.dict())
    db.add(db_personnel)
    db.commit()
    db.refresh(db_personnel)
    return db_personnel


@router.get("/personnel", response_model=List[PersonnelResponse], tags=["Master Data"])
def get_personnel_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取人员列表"""
    return db.query(Personnel).offset(skip).limit(limit).all()


@router.get("/personnel/{personnel_id}", response_model=PersonnelResponse, tags=["Master Data"])
def get_personnel(personnel_id: int, db: Session = Depends(get_db)):
    """获取人员详情"""
    personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
    if not personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")
    update_data = personnel.dict(exclude_unset=True)
    if "shift_code" in update_data and update_data["shift_code"]:
        shift = db.query(Shift).filter(Shift.code == update_data["shift_code"]).first()
        if not shift:
            raise HTTPException(status_code=400, detail="班次不存在")
        if getattr(shift, "active", 1) == 0:
            raise HTTPException(status_code=400, detail="班次未启用，不能选择")
    for key, value in update_data.items():
        setattr(db_personnel, key, value)

@router.put("/personnel/{personnel_id}", response_model=PersonnelResponse, tags=["Master Data"])
def update_personnel(personnel_id: int, personnel: PersonnelUpdate, db: Session = Depends(get_db)):
    """更新人员"""
    db_personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
    if not db_personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")
    
    for key, value in personnel.dict(exclude_unset=True).items():
        setattr(db_personnel, key, value)
    
    db.commit()
    db.refresh(db_personnel)
    return db_personnel


@router.delete("/personnel/{personnel_id}", tags=["Master Data"])
def delete_personnel(personnel_id: int, db: Session = Depends(get_db)):
    """删除人员"""
    db_personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
    if not db_personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")
    
    db.delete(db_personnel)
    db.commit()
    return {"message": "Personnel deleted successfully"}


# ==================== Shift APIs ====================
@router.post("/shifts", response_model=ShiftResponse, tags=["Master Data"])
def create_shift(shift: ShiftCreate, db: Session = Depends(get_db)):
    """创建班次"""
    db_shift = Shift(**shift.dict())
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift


@router.get("/shifts", response_model=List[ShiftResponse], tags=["Master Data"])
def get_shifts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取班次列表"""
    return db.query(Shift).offset(skip).limit(limit).all()


@router.get("/shifts/{shift_id}", response_model=ShiftResponse, tags=["Master Data"])
def get_shift(shift_id: int, db: Session = Depends(get_db)):
    """获取班次详情"""
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    return shift


@router.put("/shifts/{shift_id}", response_model=ShiftResponse, tags=["Master Data"])
def update_shift(shift_id: int, shift: ShiftUpdate, db: Session = Depends(get_db)):
    """更新班次"""
    db_shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not db_shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    for key, value in shift.dict(exclude_unset=True).items():
        setattr(db_shift, key, value)
    
    db.commit()
    db.refresh(db_shift)
    return db_shift


@router.delete("/shifts/{shift_id}", tags=["Master Data"])
def delete_shift(shift_id: int, db: Session = Depends(get_db)):
    """删除班次"""
    db_shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not db_shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    db.delete(db_shift)
    db.commit()
    return {"message": "Shift deleted successfully"}


# ==================== Routing APIs ====================
@router.post("/routings", response_model=RoutingResponse, tags=["Master Data"])
def create_routing(routing: RoutingCreate, db: Session = Depends(get_db)):
    """创建工艺路线"""
    # 约束：同一产品同一版本仅允许一个激活工艺路线
    routing_data = routing.dict(exclude={'items'})
    if routing_data.get("product_id") is None:
        raise HTTPException(status_code=400, detail="工艺路线缺少产品ID")
    if int(routing_data.get("is_active", 1)) == 1:
        exists_active = db.query(Routing).filter(
            Routing.product_id == routing_data["product_id"],
            Routing.is_active == 1
        ).first()
        if exists_active:
            raise HTTPException(status_code=400, detail="该产品已存在激活的工艺路线版本")
    db_routing = Routing(**routing_data)
    db.add(db_routing)
    db.flush()
    
    # 添加工艺路线明细
    for item in routing.items:
        db_item = RoutingItem(**item.dict(), routing_id=db_routing.id)
        db.add(db_item)
    
    db.commit()
    db.refresh(db_routing)
    return db_routing


@router.get("/routings", response_model=List[RoutingResponse], tags=["Master Data"])
def get_routings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取工艺路线列表"""
    return db.query(Routing).offset(skip).limit(limit).all()


@router.get("/routings/{routing_id}", response_model=RoutingResponse, tags=["Master Data"])
def get_routing(routing_id: int, db: Session = Depends(get_db)):
    """获取工艺路线详情"""
    routing = db.query(Routing).filter(Routing.id == routing_id).first()
    if not routing:
        raise HTTPException(status_code=404, detail="Routing not found")
    return routing


@router.put("/routings/{routing_id}", response_model=RoutingResponse, tags=["Master Data"])
def update_routing(routing_id: int, routing: RoutingUpdate, db: Session = Depends(get_db)):
    """更新工艺路线"""
    db_routing = db.query(Routing).filter(Routing.id == routing_id).first()
    if not db_routing:
        raise HTTPException(status_code=404, detail="Routing not found")
    update_header = routing.dict(exclude_unset=True, exclude={'items'})
    if update_header.get("is_active") is not None:
        new_active = int(update_header["is_active"]) == 1
        if new_active:
            exists_active = db.query(Routing).filter(
                Routing.product_id == (update_header.get("product_id") or db_routing.product_id),
                Routing.is_active == 1,
                Routing.id != routing_id
            ).first()
            if exists_active:
                raise HTTPException(status_code=400, detail="该产品已存在激活的工艺路线版本")
    # 更新工艺路线表头
    for key, value in update_header.items():
        setattr(db_routing, key, value)
    
    # 更新工艺路线明细
    if routing.items is not None:
        # 删除旧的明细
        db.query(RoutingItem).filter(RoutingItem.routing_id == routing_id).delete()
        # 添加新的明细
        for item in routing.items:
            db_item = RoutingItem(**item.dict(), routing_id=routing_id)
            db.add(db_item)
    
    db.commit()
    db.refresh(db_routing)
    return db_routing

# Routing查询：按产品获取工艺路线
@router.get("/routings/by-product/{product_id}", response_model=List[RoutingResponse], tags=["Master Data"])
def get_routings_by_product(product_id: int, version: str = None, active_only: int = 0, db: Session = Depends(get_db)):
    """按产品筛选工艺路线，可选版本或仅激活。active_only=1时仅返回激活版本"""
    q = db.query(Routing).filter(Routing.product_id == product_id)
    if version:
        q = q.filter(Routing.version == version)
    if int(active_only) == 1:
        q = q.filter(Routing.is_active == 1)
    return q.all()


@router.delete("/routings/{routing_id}", tags=["Master Data"])
def delete_routing(routing_id: int, db: Session = Depends(get_db)):
    """删除工艺路线"""
    db_routing = db.query(Routing).filter(Routing.id == routing_id).first()
    if not db_routing:
        raise HTTPException(status_code=404, detail="Routing not found")
    
    db.delete(db_routing)
    db.commit()
    return {"message": "Routing deleted successfully"}
