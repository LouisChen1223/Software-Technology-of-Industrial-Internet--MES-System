"""
为现有工单添加WIP跟踪数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 直接创建数据库连接,避免循环导入
DATABASE_URL = "sqlite:///./mes.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.models.workorder import WorkOrder, WIPTracking, WorkOrderOperation
from app.models.master import Operation

def add_wip_for_workorder(work_order_code: str):
    """为指定工单添加WIP跟踪数据"""
    db = SessionLocal()
    try:
        # 查找工单
        work_order = db.query(WorkOrder).filter(WorkOrder.code == work_order_code).first()
        if not work_order:
            print(f"❌ 未找到工单: {work_order_code}")
            return
        
        print(f"✓ 找到工单: {work_order.code}")
        print(f"  产品ID: {work_order.product_id}")
        print(f"  计划数量: {work_order.planned_quantity}")
        print(f"  工艺路线ID: {work_order.routing_id}")
        
        # 查找该工单的工序操作
        if work_order.routing_id:
            # 如果有工艺路线,应该先创建工单工序
            operations = db.query(Operation).all()
            print(f"\n可用工序列表:")
            for op in operations:
                print(f"  {op.id}. {op.name} ({op.code})")
            
            # 检查是否已有工单工序
            wo_operations = db.query(WorkOrderOperation).filter(
                WorkOrderOperation.work_order_id == work_order.id
            ).all()
            
            if wo_operations:
                print(f"\n✓ 工单已有 {len(wo_operations)} 个工序")
                for wo_op in wo_operations:
                    operation = db.query(Operation).filter(Operation.id == wo_op.operation_id).first()
                    print(f"  工序 {wo_op.sequence}: {operation.name if operation else '未知'}")
            else:
                print(f"\n⚠ 工单还没有工序,无法创建WIP跟踪")
                return
        
        # 检查是否已有WIP数据
        existing_wip = db.query(WIPTracking).filter(
            WIPTracking.work_order_id == work_order.id
        ).all()
        
        if existing_wip:
            print(f"\n⚠ 工单已有 {len(existing_wip)} 条WIP跟踪数据:")
            for wip in existing_wip:
                print(f"  - 工序ID: {wip.operation_id}, 数量: {wip.quantity}, 状态: {wip.status}")
            response = input("\n是否要删除现有WIP数据并重新创建? (y/n): ")
            if response.lower() == 'y':
                for wip in existing_wip:
                    db.delete(wip)
                db.commit()
                print("✓ 已删除现有WIP数据")
            else:
                print("取消操作")
                return
        
        # 创建WIP跟踪数据
        print(f"\n创建WIP跟踪数据...")
        
        # 获取前两个工序
        operations = db.query(Operation).limit(2).all()
        if len(operations) < 2:
            print("❌ 没有足够的工序数据")
            return
        
        wip_list = [
            WIPTracking(
                work_order_id=work_order.id,
                operation_id=operations[0].id,
                material_id=work_order.product_id,
                quantity=work_order.planned_quantity / 2,  # 一半数量在第一道工序
                status="in-process",
                location="工位A1",
                operator_id=1,
                equipment_id=1,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            WIPTracking(
                work_order_id=work_order.id,
                operation_id=operations[1].id,
                material_id=work_order.product_id,
                quantity=work_order.planned_quantity / 3,  # 三分之一在第二道工序
                status="pending",
                location="工位A2",
                operator_id=1,
                equipment_id=1,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        for wip in wip_list:
            db.add(wip)
            operation = db.query(Operation).filter(Operation.id == wip.operation_id).first()
            print(f"  + WIP: 工序 {operation.name}, 数量 {wip.quantity}, 状态 {wip.status}, 位置 {wip.location}")
        
        db.commit()
        print(f"\n✓ 成功为工单 {work_order_code} 创建了 {len(wip_list)} 条WIP跟踪数据")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        work_order_code = sys.argv[1]
    else:
        # 列出所有工单
        db = SessionLocal()
        work_orders = db.query(WorkOrder).all()
        db.close()
        
        print("现有工单列表:")
        for wo in work_orders:
            print(f"  - {wo.code} (产品ID: {wo.product_id}, 数量: {wo.planned_quantity}, 状态: {wo.status})")
        
        if not work_orders:
            print("❌ 没有找到任何工单")
            sys.exit(1)
        
        work_order_code = input("\n请输入工单编号: ")
    
    add_wip_for_workorder(work_order_code)
