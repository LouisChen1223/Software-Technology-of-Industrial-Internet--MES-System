"""
鏁版嵁搴撳垵濮嬪寲鑴氭湰
鍒涘缓鎵€鏈夎〃骞舵彃鍏ョず渚嬫暟鎹?"""
from app.database import engine, Base, SessionLocal
from app.models.master import (
    UOM, Warehouse, Material, BOM, BOMItem,
    Operation, Equipment, Tooling, Personnel, Shift, Routing, RoutingItem,
)
from app.models import Department, Workshop
from app.models.material_type import MaterialType
from app.models.workorder import WorkOrder, WorkOrderOperation, WorkReport, WIPTracking
from app.models import Shift
from app.models.inventory import Inventory, MaterialTransaction, MaterialPick, MaterialPickItem
from datetime import datetime, timedelta


def init_db():
    """鍒濆鍖栨暟鎹簱"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("鉁?Database tables created successfully!")
    
    db = SessionLocal()
    try:
        # 鍏煎宸叉湁鏁版嵁搴擄細鑻?uoms 琛ㄧ己鍒楋紝寮哄埗閲嶅缓璇ヨ〃
        try:
            db.execute("SELECT precision, active FROM uoms LIMIT 1")
        except Exception:
            print("Recreating 'uoms' table to add missing columns...")
            try:
                db.execute("DROP TABLE IF EXISTS uoms")
                db.commit()
            except Exception:
                db.rollback()
            # 浠呴噸寤?uoms 琛?            from app.models.master import UOM as _UOM
            _UOM.__table__.create(bind=engine, checkfirst=True)

        # 鍏煎宸叉湁鏁版嵁搴擄細鑻?warehouses 琛ㄧ己灏?active 鍒楋紝灏濊瘯娣诲姞鎴栭噸寤?        try:
            db.execute("SELECT active FROM warehouses LIMIT 1")
        except Exception:
            print("Altering 'warehouses' table to add 'active' column...")
            try:
                db.execute("ALTER TABLE warehouses ADD COLUMN active INTEGER DEFAULT 1")
                db.commit()
            except Exception:
                db.rollback()
                # 鍥為€€鏂规锛氶噸寤鸿〃锛堜細涓㈠け鏁版嵁锛岃皑鎱庝娇鐢級
                print("Failed to alter warehouses; recreating table...")
                from app.models.master import Warehouse as _Warehouse
                _Warehouse.__table__.create(bind=engine, checkfirst=True)

        # 鍏煎宸叉湁鏁版嵁搴擄細鑻?materials 琛ㄧ己灏?active 鍒楋紝灏濊瘯娣诲姞鎴栭噸寤?        try:
            db.execute("SELECT active FROM materials LIMIT 1")
        except Exception:
            print("Altering 'materials' table to add 'active' column...")
            try:
                db.execute("ALTER TABLE materials ADD COLUMN active INTEGER DEFAULT 1")
                db.commit()
            except Exception:
                db.rollback()
                from app.models.master import Material as _Material
                _Material.__table__.create(bind=engine, checkfirst=True)

        # 鍏煎宸叉湁鏁版嵁搴擄細涓?personnel 澧炲姞 shift_code 鍒楋紙鑻ヤ笉瀛樺湪锛?        try:
            db.execute("SELECT shift_code FROM personnel LIMIT 1")
        except Exception:
            print("Altering 'personnel' table to add 'shift_code' column...")
            try:
                db.execute("ALTER TABLE personnel ADD COLUMN shift_code VARCHAR(50)")
                db.commit()
            except Exception:
                db.rollback()
                from app.models.master import Personnel as _Personnel
                _Personnel.__table__.create(bind=engine, checkfirst=True)

        # 鍏煎宸叉湁鏁版嵁搴擄細鑻?shifts 琛ㄧ己灏?active 鍒楋紝灏濊瘯娣诲姞鎴栭噸寤?        try:
            db.execute("SELECT active FROM shifts LIMIT 1")
        except Exception:
            print("Altering 'shifts' table to add 'active' column...")
            try:
                db.execute("ALTER TABLE shifts ADD COLUMN active INTEGER DEFAULT 1")
                db.commit()
            except Exception:
                db.rollback()
                from app.models.master import Shift as _Shift
                _Shift.__table__.create(bind=engine, checkfirst=True)

        # 妫€鏌ユ槸鍚﹀凡鏈夋暟鎹?        if db.query(UOM).first():
            print("Database already has data. Skipping sample data insertion.")
            return
        
        print("\nInserting sample data...")
        
        # 1. 鍗曚綅
        print("- Creating UOMs...")
        uoms = [
            UOM(code="PC", name="浠?, description="璁′欢鍗曚綅"),
            UOM(code="KG", name="鍗冨厠", description="閲嶉噺鍗曚綅"),
            UOM(code="M", name="绫?, description="闀垮害鍗曚綅"),
            UOM(code="SET", name="濂?, description="鎴愬鍗曚綅"),
        ]
        db.add_all(uoms)
        db.commit()

        # 1.5 鐗╂枡绫诲瀷
        print("- Creating material types...")
        material_types = [
            MaterialType(code="鍘熸潗鏂?, name="鍘熸潗鏂?, description="鍘熸潗鏂欑被"),
            MaterialType(code="鍗婃垚鍝?, name="鍗婃垚鍝?, description="鍗婃垚鍝佺被"),
            MaterialType(code="鎴愬搧", name="鎴愬搧", description="鎴愬搧绫?),
            MaterialType(code="鑰楁潗", name="鑰楁潗", description="鑰楁潗/杈呮枡"),
        ]
        db.add_all(material_types)
        db.commit()
        
        # 2. 浠撳簱
        print("- Creating warehouses...")
        warehouses = [
            Warehouse(code="WH001", name="鍘熸枡浠?, location="A鍖?, warehouse_type="鍘熸枡浠?, manager="寮犱笁", active=1),
            Warehouse(code="WH002", name="鎴愬搧浠?, location="B鍖?, warehouse_type="鎴愬搧浠?, manager="鏉庡洓", active=1),
            Warehouse(code="WH003", name="鍦ㄥ埗鍝佷粨", location="C鍖?, warehouse_type="鍦ㄥ埗鍝佷粨", manager="鐜嬩簲", active=1),
        ]
        db.add_all(warehouses)
        db.commit()
        
        # 3. 鐗╂枡
        print("- Creating materials...")
        materials = [
            Material(code="MAT001", name="鏃犱汉鏈烘満鏋?, specification="纰崇氦缁?, material_type="鍘熸枡", uom_id=1, unit_price=150.0, active=1),
            Material(code="MAT002", name="鐢垫満", specification="2312 1400KV", material_type="鍘熸枡", uom_id=1, unit_price=80.0, active=1),
            Material(code="MAT003", name="铻烘棆妗?, specification="8瀵?, material_type="鍘熸枡", uom_id=1, unit_price=20.0, active=1),
            Material(code="MAT004", name="椋炴帶", specification="F4", material_type="鍘熸枡", uom_id=1, unit_price=200.0, active=1),
            Material(code="MAT005", name="鐢垫睜", specification="4S 5000mAh", material_type="鍘熸枡", uom_id=1, unit_price=180.0, active=1),
            Material(code="PROD001", name="鍥涜酱鏃犱汉鏈?, specification="鏍囧噯鐗?, material_type="鎴愬搧", uom_id=1, unit_price=1000.0, active=1),
        ]
        db.add_all(materials)
        db.commit()
        
        # 4. BOM
        print("- Creating BOMs...")
        bom = BOM(
            code="BOM001",
            name="鍥涜酱鏃犱汉鏈築OM",
            product_id=6,  # PROD001
            version="1.0",
            quantity=1,
            is_active=1,
            description="鍥涜酱鏃犱汉鏈虹墿鏂欐竻鍗?
        )
        db.add(bom)
        db.flush()
        
        bom_items = [
            BOMItem(bom_id=bom.id, material_id=1, quantity=1, sequence=1),  # 鏈烘灦
            BOMItem(bom_id=bom.id, material_id=2, quantity=4, sequence=2),  # 鐢垫満
            BOMItem(bom_id=bom.id, material_id=3, quantity=4, sequence=3),  # 铻烘棆妗?            BOMItem(bom_id=bom.id, material_id=4, quantity=1, sequence=4),  # 椋炴帶
            BOMItem(bom_id=bom.id, material_id=5, quantity=1, sequence=5),  # 鐢垫睜
        ]
        db.add_all(bom_items)
        db.commit()
        
        # 5. 宸ュ簭
        print("- Creating operations...")
        operations = [
            Operation(code="OP001", name="鏈烘灦瑁呴厤", operation_type="瑁呴厤", standard_time=30, workshop_id=1),
            Operation(code="OP002", name="鐢垫満瀹夎", operation_type="瑁呴厤", standard_time=20, workshop_id=1),
            Operation(code="OP003", name="椋炴帶瀹夎", operation_type="瑁呴厤", standard_time=15, workshop_id=1),
            Operation(code="OP004", name="鍔熻兘娴嬭瘯", operation_type="妫€楠?, standard_time=10, workshop_id=2),
            Operation(code="OP005", name="鍖呰", operation_type="鍖呰", standard_time=5, workshop_id=1),
        ]
        db.add_all(operations)
        db.commit()
        
        # 6. 璁惧
        print("- Creating equipment...")
        equipment_list = [
            Equipment(code="EQ001", name="瑁呴厤宸ヤ綔鍙?", equipment_type="瑁呴厤鍙?, status="idle", location="杞﹂棿A", workshop_id=1),
            Equipment(code="EQ002", name="瑁呴厤宸ヤ綔鍙?", equipment_type="瑁呴厤鍙?, status="idle", location="杞﹂棿A", workshop_id=1),
            Equipment(code="EQ003", name="娴嬭瘯鍙?", equipment_type="娴嬭瘯璁惧", status="idle", location="杞﹂棿B", workshop_id=2),
        ]
        db.add_all(equipment_list)
        db.commit()
        
        # 7. 宸ヨ
        print("- Creating tooling...")
        tooling_list = [
            Tooling(code="TOOL001", name="鐢靛姩铻轰笣鍒€", tooling_type="宸ュ叿", quantity=10, status="available", workshop_id=1),
            Tooling(code="TOOL002", name="娴嬭瘯娌诲叿", tooling_type="娌诲叿", quantity=5, status="available", workshop_id=2),
        ]
        db.add_all(tooling_list)
        db.commit()
        
        # 8. 閮ㄩ棬锛堢ず渚嬶級
        print("- Creating departments...")
        from app.models import Department
        departments = [
            Department(code="DEPT-A", name="鐢熶骇涓€閮?, manager="寮犱笁", description="璐熻矗鏃犱汉鏈鸿閰嶇嚎"),
            Department(code="DEPT-B", name="璐ㄩ噺閮?, manager="鏉庡洓", description="璐ㄩ噺绠＄悊涓庢楠?),
        ]
        db.add_all(departments)
        db.commit()

        # 9. 杞﹂棿锛堢ず渚嬶級
        print("- Creating workshops...")
        from app.models import Workshop
        workshops = [
            Workshop(code="WS-A1", name="瑁呴厤杞﹂棿A1", supervisor="鐜嬩簲", location="鍘傛埧A-涓€灞?, description="鏃犱汉鏈轰富瑁呴厤绾?, active=1),
            Workshop(code="WS-B1", name="娴嬭瘯杞﹂棿B1", supervisor="璧靛叚", location="鍘傛埧B-浜屽眰", description="鍔熻兘娴嬭瘯涓庤皟璇?, active=1),
        ]
        db.add_all(workshops)
        db.commit()

        # 10. 浜哄憳
        print("- Creating personnel...")
        personnel_list = [
            Personnel(code="P001", name="宸ヤ汉鐢?, department="鐢熶骇", department_id=1, position="瑁呴厤宸?, skill_level="涓骇", phone="13800000001", email="p001@example.com", shift_code="D1"),
            Personnel(code="P002", name="宸ヤ汉涔?, department="鐢熶骇", department_id=1, position="瑁呴厤宸?, skill_level="鍒濈骇", phone="13800000002", email="p002@example.com", shift_code="D1"),
            Personnel(code="Q001", name="妫€楠屽憳", department="璐ㄩ噺", department_id=2, position="妫€楠屽憳", skill_level="涓骇", phone="13800000003", email="q001@example.com", shift_code="N1"),
        ]
        db.add_all(personnel_list)
        db.commit()
        
        # 9. 鐝
        print("- Creating shifts...")
        shifts = [
            Shift(code="D1", name="鐧界彮", start_time="08:00", end_time="17:00", active=1, workshop_id=1),
            Shift(code="N1", name="鏅氱彮", start_time="20:00", end_time="05:00", active=1, workshop_id=2),
        ]
        db.add_all(shifts)
        db.commit()
        
        # 10. 宸ヨ壓璺嚎
        print("- Creating routings...")
        routing = Routing(
            code="RT001",
            name="鍥涜酱鏃犱汉鏈哄伐鑹鸿矾绾?,
            product_id=6,
            version="1.0",
            is_active=1
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
        
        # 11. 鍒濆搴撳瓨
        print("- Creating initial inventory...")
        inventory_list = [
            Inventory(warehouse_id=1, material_id=1, batch_number="B20240101", quantity=100, available_quantity=100, location="A-01"),
            Inventory(warehouse_id=1, material_id=2, batch_number="B20240102", quantity=400, available_quantity=400, location="A-02"),
            Inventory(warehouse_id=1, material_id=3, batch_number="B20240103", quantity=400, available_quantity=400, location="A-03"),
            Inventory(warehouse_id=1, material_id=4, batch_number="B20240104", quantity=100, available_quantity=100, location="A-04"),
            Inventory(warehouse_id=1, material_id=5, batch_number="B20240105", quantity=100, available_quantity=100, location="A-05"),
        ]
        db.add_all(inventory_list)
        db.commit()
        
        # 12. 绀轰緥宸ュ崟锛堟椂闂寸簿纭埌灏忔椂锛?        print("- Creating sample work orders...")
        today = datetime.now().replace(minute=0, second=0, microsecond=0)
        work_order = WorkOrder(
            code=f"WO{today.strftime('%Y%m%d')}001",
            product_id=6,
            bom_id=bom.id,
            routing_id=routing.id,
            planned_quantity=10,
            status="released",
            priority=5,
            planned_start_date=today,
            planned_end_date=(today + timedelta(days=2)).replace(minute=0, second=0, microsecond=0),
            customer="瀹㈡埛A",
            sales_order="SO20240001",
            created_by="绯荤粺绠＄悊鍛?
        )
        db.add(work_order)
        db.commit()

        # 涓虹ず渚嬪伐鍗曟牴鎹伐鑹鸿矾绾胯嚜鍔ㄧ敓鎴愬伐搴?        if work_order.routing_id:
            r_items = db.query(RoutingItem).filter(RoutingItem.routing_id == work_order.routing_id).order_by(RoutingItem.sequence.asc()).all()
            for item in r_items:
                db.add(WorkOrderOperation(
                    work_order_id=work_order.id,
                    operation_id=item.operation_id,
                    sequence=item.sequence,
                    equipment_id=item.equipment_id,
                    planned_quantity=work_order.planned_quantity,
                    status="pending",
                    planned_start_date=work_order.planned_start_date,
                ))
            db.commit()
        
        # 13. WIP tracking sample data is omitted so that WIP reflects real HMI reports.
        wip_list = []
        
        print("\n鉁?Sample data inserted successfully!")
        print("\n" + "="*50)
        print("Database initialization completed!")
        print("="*50)
        print("\nSample data summary:")
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
        print("\nYou can now start the API server with:")
        print("  uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"\n鉁?Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()


