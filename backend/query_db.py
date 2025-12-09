"""
查询数据库工具
"""
from app.database import SessionLocal
from app.models.workorder import WorkOrder, WIPTracking
from app.models.inventory import Inventory
from app.models.master import Material, Operation

def query_work_orders():
    """查询所有工单"""
    db = SessionLocal()
    try:
        work_orders = db.query(WorkOrder).all()
        print(f"\n=== 工单列表 (共 {len(work_orders)} 条) ===")
        for wo in work_orders:
            print(f"ID: {wo.id}, 编号: {wo.code}, 产品ID: {wo.product_id}, "
                  f"数量: {wo.planned_quantity}, 状态: {wo.status}, BOM: {wo.bom_id}, Routing: {wo.routing_id}")
    finally:
        db.close()

def query_wip_tracking():
    """查询WIP跟踪数据"""
    db = SessionLocal()
    try:
        wip_items = db.query(WIPTracking).all()
        print(f"\n=== WIP跟踪列表 (共 {len(wip_items)} 条) ===")
        for wip in wip_items:
            print(f"ID: {wip.id}, 工单ID: {wip.work_order_id}, 工序ID: {wip.operation_id}, "
                  f"数量: {wip.quantity}, 状态: {wip.status}, 位置: {wip.location}")
    finally:
        db.close()

def query_inventory():
    """查询库存"""
    db = SessionLocal()
    try:
        items = db.query(Inventory).all()
        print(f"\n=== 库存列表 (共 {len(items)} 条) ===")
        for item in items:
            print(f"ID: {item.id}, 物料ID: {item.material_id}, "
                  f"数量: {item.quantity}, 仓库ID: {item.warehouse_id}")
    finally:
        db.close()

def query_materials():
    """查询物料"""
    db = SessionLocal()
    try:
        materials = db.query(Material).all()
        print(f"\n=== 物料列表 (共 {len(materials)} 条) ===")
        for mat in materials:
            print(f"ID: {mat.id}, 编号: {mat.code}, 名称: {mat.name}, "
                  f"类型: {mat.material_type}")
    finally:
        db.close()

if __name__ == "__main__":
    print("MES 数据库查询工具")
    print("=" * 50)
    
    query_materials()
    query_work_orders()
    query_wip_tracking()
    query_inventory()
