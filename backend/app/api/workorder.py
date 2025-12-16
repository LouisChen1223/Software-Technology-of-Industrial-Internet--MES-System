from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime
from app.database import get_db
import logging

logger = logging.getLogger(__name__)
from app.models.workorder import WorkOrder, WorkOrderOperation, WorkReport, WIPTracking
from app.models.master import Material, BOM, Routing, RoutingItem
from app.schemas.workorder import (
    WorkOrderCreate, WorkOrderUpdate, WorkOrderResponse,
    WorkReportCreate, WorkReportResponse,
    WIPTrackingCreate, WIPTrackingUpdate, WIPTrackingResponse
)

router = APIRouter()


# ==================== Work Order APIs ====================
@router.post("/work-orders", response_model=WorkOrderResponse, tags=["Work Order"])
def create_work_order(work_order: WorkOrderCreate, db: Session = Depends(get_db)):
    """创建工单"""
    logger.info(f"创建工单: {work_order.code or '[auto]'} - 产品ID={work_order.product_id}, 数量={work_order.planned_quantity}")

    # 校验产品存在
    product = db.query(Material).filter(Material.id == work_order.product_id).first()
    if not product:
        raise HTTPException(status_code=400, detail="Invalid product_id: product not found")
    # 仅允许选择物料类型为成品的作为工单产品
    if (product.material_type or '').strip() != '成品':
        raise HTTPException(status_code=400, detail="product_id must be a '成品' material")

    wo_data = work_order.dict(exclude={'operations'})
    # 若未传工单号，自动生成 WOYYYYMMDDNNN（当日递增序号）
    if not wo_data.get('code'):
        today_str = datetime.now().strftime('%Y%m%d')
        prefix = f"WO{today_str}"
        # 查找当日最大序号
        last = (
            db.query(WorkOrder)
            .filter(WorkOrder.code.like(f"{prefix}%"))
            .order_by(WorkOrder.code.desc())
            .first()
        )
        seq = 1
        if last and last.code.startswith(prefix):
            try:
                seq = int(last.code.replace(prefix, '')) + 1
            except Exception:
                seq = 1
        wo_data['code'] = f"{prefix}{seq:03d}"
    db_wo = WorkOrder(**wo_data)

    # 若未指定 routing_id，则按产品选择启用的工艺路线
    if not db_wo.routing_id:
        routing = (
            db.query(Routing)
            .filter(Routing.product_id == work_order.product_id, Routing.is_active == 1)
            .order_by(Routing.version.desc())
            .first()
        )
        if routing:
            db_wo.routing_id = routing.id

    # 若未指定 bom_id，则按产品选择启用的 BOM
    if not db_wo.bom_id:
        bom = (
            db.query(BOM)
            .filter(BOM.product_id == work_order.product_id, BOM.is_active == 1)
            .order_by(BOM.version.desc())
            .first()
        )
        if bom:
            db_wo.bom_id = bom.id

    db.add(db_wo)
    db.flush()
    
    # 添加工单工序
    if work_order.operations:
        for op in work_order.operations:
            db_op = WorkOrderOperation(**op.dict(), work_order_id=db_wo.id)
            db.add(db_op)
    else:
        # 如果没有指定工序，从工艺路线自动生成
        if db_wo.routing_id:
            routing = db.query(Routing).filter(Routing.id == db_wo.routing_id).first()
            if routing:
                for item in routing.items:
                    db_op = WorkOrderOperation(
                        work_order_id=db_wo.id,
                        operation_id=item.operation_id,
                        sequence=item.sequence,
                        equipment_id=item.equipment_id,
                        planned_quantity=db_wo.planned_quantity,
                        status="pending"
                    )
                    db.add(db_op)
    db.commit()
    db.refresh(db_wo)
    logger.info(f"✓ 工单创建成功: ID={db_wo.id}, 编号={db_wo.code}")
    return db_wo


@router.get("/work-orders", response_model=List[WorkOrderResponse], tags=["Work Order"])
@router.get("/work-orders", response_model=List[WorkOrderResponse], tags=["Work Order"])
def get_work_orders(
    skip: int = 0, 
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """获取工单列表"""
    query = db.query(WorkOrder)
    if status:
        query = query.filter(WorkOrder.status == status)
    return query.offset(skip).limit(limit).all()


@router.get("/work-orders/{work_order_id}", response_model=WorkOrderResponse, tags=["Work Order"])
def get_work_order(work_order_id: int, db: Session = Depends(get_db)):
    """获取工单详情"""
    wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    return wo


@router.put("/work-orders/{work_order_id}", response_model=WorkOrderResponse, tags=["Work Order"])
def update_work_order(work_order_id: int, work_order: WorkOrderUpdate, db: Session = Depends(get_db)):
    """更新工单"""
    db_wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not db_wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    
    for key, value in work_order.dict(exclude_unset=True).items():
        setattr(db_wo, key, value)
    
    db.commit()
    db.refresh(db_wo)
    return db_wo


@router.post("/work-orders/{work_order_id}/generate-operations", tags=["Work Order"])
def generate_operations(work_order_id: int, force: bool = False, db: Session = Depends(get_db)):
    """根据工艺路线为工单生成工序。
    - 若 force=True，先删除已存在的工序再重建。
    - 否则在不存在工序时才创建。
    """
    db_wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not db_wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    if not db_wo.routing_id:
        raise HTTPException(status_code=400, detail="Work Order has no routing")

    existing = db.query(WorkOrderOperation).filter(WorkOrderOperation.work_order_id == work_order_id).count()
    if existing and not force:
        return {"message": "Operations already exist", "count": existing}
    if existing and force:
        db.query(WorkOrderOperation).filter(WorkOrderOperation.work_order_id == work_order_id).delete()
        db.commit()

    routing = db.query(Routing).filter(Routing.id == db_wo.routing_id).first()
    if not routing:
        raise HTTPException(status_code=400, detail="Routing not found")

    for item in routing.items:
        db.add(WorkOrderOperation(
            work_order_id=db_wo.id,
            operation_id=item.operation_id,
            sequence=item.sequence,
            equipment_id=item.equipment_id,
            planned_quantity=db_wo.planned_quantity,
            status="pending",
            planned_start_date=db_wo.planned_start_date,
        ))
    db.commit()
    count = db.query(WorkOrderOperation).filter(WorkOrderOperation.work_order_id == work_order_id).count()
    return {"message": "Operations generated", "count": count}


@router.delete("/work-orders/{work_order_id}", tags=["Work Order"])
def delete_work_order(work_order_id: int, db: Session = Depends(get_db)):
    """删除工单"""
    db_wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not db_wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    
    db.delete(db_wo)
    db.commit()
    return {"message": "Work Order deleted successfully"}

@router.post("/work-orders/{work_order_id}/release", response_model=WorkOrderResponse, tags=["Work Order"])
def release_work_order(work_order_id: int, db: Session = Depends(get_db)):
    """下达工单"""
    db_wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not db_wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    
    if db_wo.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft work orders can be released")
    
    logger.info(f"下达工单: ID={work_order_id}, 编号={db_wo.code}")
    db_wo.status = "released"
    db.commit()
    db.refresh(db_wo)
    logger.info(f"✓ 工单已下达: {db_wo.code}")
    return db_wo


@router.post("/work-orders/{work_order_id}/start", response_model=WorkOrderResponse, tags=["Work Order"])
def start_work_order(work_order_id: int, db: Session = Depends(get_db)):
    """开始工单"""
    db_wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not db_wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    
    if db_wo.status != "released":
        raise HTTPException(status_code=400, detail="Only released work orders can be started")
    
    db_wo.status = "in_progress"
    db_wo.actual_start_date = datetime.now()
    db.commit()
    db.refresh(db_wo)
    return db_wo


@router.post("/work-orders/{work_order_id}/complete", response_model=WorkOrderResponse, tags=["Work Order"])
def complete_work_order(work_order_id: int, db: Session = Depends(get_db)):
    """完成工单"""
    db_wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not db_wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    
    if db_wo.status != "in_progress":
        raise HTTPException(status_code=400, detail="Only in-progress work orders can be completed")
    
    db_wo.status = "completed"
    db_wo.actual_end_date = datetime.now()
    db.commit()
    db.refresh(db_wo)
    return db_wo


@router.post("/work-orders/{work_order_id}/cancel", response_model=WorkOrderResponse, tags=["Work Order"])
def cancel_work_order(work_order_id: int, db: Session = Depends(get_db)):
    """取消工单"""
    db_wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not db_wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    
    db_wo.status = "cancelled"
    db.commit()
    db.refresh(db_wo)
    return db_wo

@router.post("/work-reports", response_model=WorkReportResponse, tags=["Work Order"])
def create_work_report(report: WorkReportCreate, db: Session = Depends(get_db)):
    """创建报工记录（扫码报工）"""
    # 验证工单存在
    db_wo = db.query(WorkOrder).filter(WorkOrder.id == report.work_order_id).first()
    if not db_wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    
    logger.info(f"报工: 工单ID={report.work_order_id}, 类型={report.report_type}, 数量={report.quantity}")
    
    # 创建报工记录
    report_data = report.dict()
    if not report_data.get('report_time'):
        report_data['report_time'] = datetime.now()
    
    db_report = WorkReport(**report_data)
    db.add(db_report)
    db_report = WorkReport(**report_data)
    db.add(db_report)
    
    # 更新工单数量
    if report.report_type == "complete":
        db_wo.completed_quantity += report.quantity
    elif report.report_type == "scrap":
        db_wo.scrapped_quantity += report.quantity
    
    # 更新工单工序数量
    if report.work_order_operation_id:
        db_op = db.query(WorkOrderOperation).filter(
            WorkOrderOperation.id == report.work_order_operation_id
        ).first()
        if db_op:
            if report.report_type == "start":
                db_op.status = "in_progress"
                if not db_op.actual_start_date:
                    db_op.actual_start_date = datetime.now()
            elif report.report_type == "complete":
                db_op.completed_quantity += report.quantity
                if db_op.completed_quantity >= db_op.planned_quantity:
                    db_op.status = "completed"
                    db_op.actual_end_date = datetime.now()
            elif report.report_type == "scrap":
                db_op.scrapped_quantity += report.quantity
    
    # 更新工单状态
    if report.report_type == "start" and db_wo.status == "released":
        db_wo.status = "in_progress"
        if not db_wo.actual_start_date:
            db_wo.actual_start_date = datetime.now()
    
    db.commit()
    db.refresh(db_report)
    logger.info(f"✓ 报工成功: 报工ID={db_report.id}, 类型={report.report_type}")
    return db_report


@router.get("/work-reports", response_model=List[WorkReportResponse], tags=["Work Order"])
def get_work_reports(
    skip: int = 0, 
    limit: int = 100,
    work_order_id: int = None,
    db: Session = Depends(get_db)
):
    """获取报工记录列表"""
    query = db.query(WorkReport)
    if work_order_id:
        query = query.filter(WorkReport.work_order_id == work_order_id)
    return query.order_by(WorkReport.report_time.desc()).offset(skip).limit(limit).all()


@router.get("/work-reports/{report_id}", response_model=WorkReportResponse, tags=["Work Order"])
def get_work_report(report_id: int, db: Session = Depends(get_db)):
    """获取报工记录详情"""
    report = db.query(WorkReport).filter(WorkReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Work Report not found")
    return report


# ==================== WIP Tracking APIs ====================
@router.post("/wip-tracking", response_model=WIPTrackingResponse, tags=["WIP"])
def create_wip_tracking(wip: WIPTrackingCreate, db: Session = Depends(get_db)):
    """创建在制品追踪记录"""
    db_wip = WIPTracking(**wip.dict())
    db.add(db_wip)
    db.commit()
    db.refresh(db_wip)
    return db_wip


@router.get("/wip-tracking", response_model=List[WIPTrackingResponse], tags=["WIP"])
def get_wip_tracking(
    skip: int = 0, 
    limit: int = 100,
    work_order_id: int = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """获取在制品列表"""
    logger.info(f"获取WIP跟踪列表: skip={skip}, limit={limit}, work_order_id={work_order_id}, status={status}")
    
    # 使用 joinedload 预加载关联数据
    query = db.query(WIPTracking).options(
        joinedload(WIPTracking.work_order),
        joinedload(WIPTracking.operation),
        joinedload(WIPTracking.material),
        joinedload(WIPTracking.operator),
        joinedload(WIPTracking.equipment)
    )
    
    if work_order_id:
        query = query.filter(WIPTracking.work_order_id == work_order_id)
    if status:
        query = query.filter(WIPTracking.status == status)
    
    wip_list = query.offset(skip).limit(limit).all()
    logger.info(f"✓ 返回 {len(wip_list)} 条WIP跟踪记录")
    
    return wip_list


@router.get("/wip-tracking/{wip_id}", response_model=WIPTrackingResponse, tags=["WIP"])
def get_wip_tracking_detail(wip_id: int, db: Session = Depends(get_db)):
    """获取在制品详情"""
    wip = db.query(WIPTracking).filter(WIPTracking.id == wip_id).first()
    if not wip:
        raise HTTPException(status_code=404, detail="WIP Tracking not found")
    return wip


@router.put("/wip-tracking/{wip_id}", response_model=WIPTrackingResponse, tags=["WIP"])
def update_wip_tracking(wip_id: int, wip: WIPTrackingUpdate, db: Session = Depends(get_db)):
    """更新在制品"""
    db_wip = db.query(WIPTracking).filter(WIPTracking.id == wip_id).first()
    if not db_wip:
        raise HTTPException(status_code=404, detail="WIP Tracking not found")
    
    for key, value in wip.dict(exclude_unset=True).items():
        setattr(db_wip, key, value)
    
    db.commit()
    db.refresh(db_wip)
    return db_wip


@router.get("/wip-tracking/batch/{batch_number}", response_model=List[WIPTrackingResponse], tags=["WIP"])
def trace_by_batch(batch_number: str, db: Session = Depends(get_db)):
    """按批次号追溯"""
    return db.query(WIPTracking).filter(WIPTracking.batch_number == batch_number).all()


@router.get("/wip-tracking/serial/{serial_number}", response_model=List[WIPTrackingResponse], tags=["WIP"])
def trace_by_serial(serial_number: str, db: Session = Depends(get_db)):
    """按序列号追溯"""
    return db.query(WIPTracking).filter(WIPTracking.serial_number == serial_number).all()
