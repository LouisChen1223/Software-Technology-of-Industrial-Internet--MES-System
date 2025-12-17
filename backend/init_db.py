"""
Database initialization script for the MES demo project.
Creates all tables and inserts sample data.
"""

from datetime import datetime, timedelta
from typing import List

from app.database import Base, engine, SessionLocal
from app.models.master import (
    UOM,
    Warehouse,
    Material,
    BOM,
    BOMItem,
    Operation,
    Equipment,
    Tooling,
    Personnel,
    Shift,
    Routing,
    RoutingItem,
)
from app.models.material_type import MaterialType
from app.models.workorder import WorkOrder, WorkOrderOperation, WIPTracking
from app.models.inventory import Inventory
from app.models import Department, Workshop


def init_db() -> None:
    """Create tables and insert sample data if the DB is empty."""
    print("Creating database tables ...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

    db = SessionLocal()
    try:
        # If there is already data, do not insert again
        if db.query(UOM).first():
            print("Database already has data. Skipping sample data insertion.")
            return

        print()
        print("Inserting sample data ...")

        # 1. Units of measure
        print("- Creating UOMs")
        uoms = [
            UOM(code="PC", name="件", description="计数单位"),
            UOM(code="KG", name="千克", description="重量单位"),
            UOM(code="M", name="米", description="长度单位"),
            UOM(code="SET", name="套", description="成套单位"),
        ]
        db.add_all(uoms)
        db.commit()

        # 1.5 Material types
        print("- Creating material types")
        material_types = [
            MaterialType(code="RAW", name="原材料", description="原材料"),
            MaterialType(code="WIP", name="半成品", description="半成品"),
            MaterialType(code="FG", name="成品", description="成品"),
            MaterialType(code="CONS", name="耗材", description="耗材/辅料"),
        ]
        db.add_all(material_types)
        db.commit()

        # 2. Warehouses
        print("- Creating warehouses")
        warehouses = [
            Warehouse(
                code="WH001",
                name="原料仓库",
                location="A区",
                warehouse_type="RAW",
                manager="张三",
                active=1,
            ),
            Warehouse(
                code="WH002",
                name="成品仓库",
                location="B区",
                warehouse_type="FG",
                manager="李四",
                active=1,
            ),
            Warehouse(
                code="WH003",
                name="在制品仓库",
                location="C区",
                warehouse_type="WIP",
                manager="王五",
                active=1,
            ),
        ]
        db.add_all(warehouses)
        db.commit()

        # 3. Materials
        print("- Creating materials")
        materials = [
            Material(
                code="MAT001",
                name="碳纤维机架",
                specification="机架",
                material_type="RAW",
                uom_id=1,
                unit_price=150.0,
                active=1,
            ),
            Material(
                code="MAT002",
                name="电机",
                specification="2312 1400KV",
                material_type="RAW",
                uom_id=1,
                unit_price=80.0,
                active=1,
            ),
            Material(
                code="MAT003",
                name="螺旋桨",
                specification="8寸",
                material_type="RAW",
                uom_id=1,
                unit_price=20.0,
                active=1,
            ),
            Material(
                code="MAT004",
                name="飞控板",
                specification="F4",
                material_type="RAW",
                uom_id=1,
                unit_price=200.0,
                active=1,
            ),
            Material(
                code="MAT005",
                name="电池",
                specification="4S 5000mAh",
                material_type="RAW",
                uom_id=1,
                unit_price=180.0,
                active=1,
            ),
            Material(
                code="PROD001",
                name="四旋翼无人机",
                specification="标准款",
                material_type="FG",
                uom_id=1,
                unit_price=1000.0,
                active=1,
            ),
        ]
        db.add_all(materials)
        db.commit()

        product = db.query(Material).filter(Material.code == "PROD001").first()

        # 4. BOM
        print("- Creating BOM")
        bom = BOM(
            code="BOM001",
            name="四旋翼无人机BOM",
            product_id=product.id if product else 6,
            version="1.0",
            quantity=1,
            is_active=1,
            description="四旋翼无人机物料清单",
        )
        db.add(bom)
        db.flush()

        bom_items = [
            BOMItem(bom_id=bom.id, material_id=1, quantity=1, sequence=1),
            BOMItem(bom_id=bom.id, material_id=2, quantity=4, sequence=2),
            BOMItem(bom_id=bom.id, material_id=3, quantity=4, sequence=3),
            BOMItem(bom_id=bom.id, material_id=4, quantity=1, sequence=4),
            BOMItem(bom_id=bom.id, material_id=5, quantity=1, sequence=5),
        ]
        db.add_all(bom_items)
        db.commit()

        # 5. Operations
        print("- Creating operations")
        operations = [
            Operation(code="OP001", name="机架装配", operation_type="装配", standard_time=30, workshop_id=1),
            Operation(code="OP002", name="电机安装", operation_type="装配", standard_time=20, workshop_id=1),
            Operation(code="OP003", name="飞控安装", operation_type="装配", standard_time=15, workshop_id=1),
            Operation(code="OP004", name="功能测试", operation_type="检验", standard_time=10, workshop_id=2),
            Operation(code="OP005", name="包装", operation_type="包装", standard_time=5, workshop_id=1),
        ]
        db.add_all(operations)
        db.commit()

        # 6. Equipment
        print("- Creating equipment")
        equipment_list = [
            Equipment(
                code="EQ001",
                name="装配工位1",
                equipment_type="装配",
                status="idle",
                location="装配车间A1",
                workshop_id=1,
            ),
            Equipment(
                code="EQ002",
                name="装配工位2",
                equipment_type="装配",
                status="idle",
                location="装配车间A1",
                workshop_id=1,
            ),
            Equipment(
                code="EQ003",
                name="测试台",
                equipment_type="测试",
                status="idle",
                location="测试车间B1",
                workshop_id=2,
            ),
        ]
        db.add_all(equipment_list)
        db.commit()

        # 7. Tooling
        print("- Creating tooling")
        tooling_list = [
            Tooling(
                code="TOOL001",
                name="电动螺丝刀",
                tooling_type="工装",
                quantity=10,
                status="available",
                workshop_id=1,
            ),
            Tooling(
                code="TOOL002",
                name="测试治具",
                tooling_type="治具",
                quantity=5,
                status="available",
                workshop_id=2,
            ),
        ]
        db.add_all(tooling_list)
        db.commit()

        # 8. Departments
        print("- Creating departments")
        departments = [
            Department(
                code="DEPT-A",
                name="生产一部",
                manager="张三",
                description="负责无人机装配产线",
            ),
            Department(
                code="DEPT-B",
                name="质量部",
                manager="李四",
                description="质量管理与检验",
            ),
        ]
        db.add_all(departments)
        db.commit()

        # 9. Workshops
        print("- Creating workshops")
        workshops = [
            Workshop(
                code="WS-A1",
                name="装配车间A1",
                supervisor="王五",
                location="厂房A-一层",
                description="无人机主装配线",
                active=1,
            ),
            Workshop(
                code="WS-B1",
                name="测试车间B1",
                supervisor="赵六",
                location="厂房B-二层",
                description="功能测试与调试",
                active=1,
            ),
        ]
        db.add_all(workshops)
        db.commit()

        # 10. Personnel
        print("- Creating personnel")
        personnel_list = [
            Personnel(
                code="P001",
                name="操作员A",
                department="生产",
                department_id=1,
                position="装配工",
                skill_level="中级",
                phone="13800000001",
                email="p001@example.com",
                shift_code="D1",
            ),
            Personnel(
                code="P002",
                name="操作员B",
                department="生产",
                department_id=1,
                position="装配工",
                skill_level="初级",
                phone="13800000002",
                email="p002@example.com",
                shift_code="D1",
            ),
            Personnel(
                code="Q001",
                name="检验员",
                department="质量",
                department_id=2,
                position="检验员",
                skill_level="中级",
                phone="13800000003",
                email="q001@example.com",
                shift_code="N1",
            ),
        ]
        db.add_all(personnel_list)
        db.commit()

        # 11. Shifts
        print("- Creating shifts")
        shifts = [
            Shift(
                code="D1",
                name="白班",
                start_time="08:00",
                end_time="17:00",
                description="白班",
                active=1,
            ),
            Shift(
                code="N1",
                name="夜班",
                start_time="20:00",
                end_time="05:00",
                description="夜班",
                active=1,
            ),
        ]
        db.add_all(shifts)
        db.commit()

        # 12. Routing
        print("- Creating routing")
        routing = Routing(
            code="RT001",
            name="四旋翼无人机工艺路线",
            product_id=product.id if product else 6,
            version="1.0",
            is_active=1,
            description="四旋翼无人机装配工艺路线",
        )
        db.add(routing)
        db.flush()

        routing_items = [
            RoutingItem(routing_id=routing.id, operation_id=1, sequence=10, equipment_id=1, standard_time=30),
            RoutingItem(routing_id=routing.id, operation_id=2, sequence=20, equipment_id=1, standard_time=20),
            RoutingItem(routing_id=routing.id, operation_id=3, sequence=30, equipment_id=2, standard_time=15),
            RoutingItem(routing_id=routing.id, operation_id=4, sequence=40, equipment_id=3, standard_time=10),
            RoutingItem(routing_id=routing.id, operation_id=5, sequence=50, standard_time=5),
        ]
        db.add_all(routing_items)
        db.commit()

        # 13. Initial inventory
        print("- Creating initial inventory")
        inventory_list = [
            Inventory(
                warehouse_id=1,
                material_id=1,
                batch_number="B20240101",
                quantity=100,
                available_quantity=100,
                location="A-01",
            ),
            Inventory(
                warehouse_id=1,
                material_id=2,
                batch_number="B20240102",
                quantity=400,
                available_quantity=400,
                location="A-02",
            ),
            Inventory(
                warehouse_id=1,
                material_id=3,
                batch_number="B20240103",
                quantity=400,
                available_quantity=400,
                location="A-03",
            ),
            Inventory(
                warehouse_id=1,
                material_id=4,
                batch_number="B20240104",
                quantity=100,
                available_quantity=100,
                location="A-04",
            ),
            Inventory(
                warehouse_id=1,
                material_id=5,
                batch_number="B20240105",
                quantity=100,
                available_quantity=100,
                location="A-05",
            ),
        ]
        db.add_all(inventory_list)
        db.commit()

        # 14. Sample work order
        print("- Creating sample work order")
        today = datetime.now().replace(minute=0, second=0, microsecond=0)
        work_order = WorkOrder(
            code=f"WO{today.strftime('%Y%m%d')}001",
            product_id=product.id if product else 6,
            bom_id=bom.id,
            routing_id=routing.id,
            planned_quantity=10,
            status="released",
            priority=5,
            planned_start_date=today,
            planned_end_date=(today + timedelta(days=2)).replace(minute=0, second=0, microsecond=0),
            customer="客户A",
            sales_order="SO20240001",
            created_by="系统管理员",
        )
        db.add(work_order)
        db.commit()

        # Auto-generate work order operations from routing
        if work_order.routing_id:
            routing_rows = (
                db.query(RoutingItem)
                .filter(RoutingItem.routing_id == work_order.routing_id)
                .order_by(RoutingItem.sequence.asc())
                .all()
            )
            for item in routing_rows:
                db.add(
                    WorkOrderOperation(
                        work_order_id=work_order.id,
                        operation_id=item.operation_id,
                        sequence=item.sequence,
                        equipment_id=item.equipment_id,
                        planned_quantity=work_order.planned_quantity,
                        status="pending",
                        planned_start_date=work_order.planned_start_date,
                    )
                )
            db.commit()

        # 15. WIP tracking sample data: omitted so that WIP reflects real HMI reports.
        wip_list: List[WIPTracking] = []

        print()
        print("Sample data inserted successfully.")
        print("=" * 50)
        print("Database initialization completed.")
        print("=" * 50)
        print("Sample data summary:")
        print(f"  - {len(uoms)} UOMs")
        print(f"  - {len(warehouses)} Warehouses")
        print(f"  - {len(materials)} Materials")
        print(f"  - 1 BOM with {len(bom_items)} items")
        print(f"  - {len(operations)} Operations")
        print(f"  - {len(equipment_list)} Equipment")
        print(f"  - {len(tooling_list)} Tooling")
        print(f"  - {len(personnel_list)} Personnel")
        print(f"  - {len(shifts)} Shifts")
        print(f"  - 1 Routing with {len(routing_items)} items")
        print(f"  - {len(inventory_list)} Inventory records")
        print(f"  - 1 Work Order")
        print(f"  - {len(wip_list)} WIP Tracking records")
        print()
        print("You can now start the API server with:")
        print("  uvicorn app.main:app --reload")

    except Exception as exc:
        print(f"Error during init_db: {exc}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()

