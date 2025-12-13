from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.database import get_db
from app.models.workorder import WorkOrder, WorkOrderOperation

router = APIRouter()


def working_slots(start: datetime, hours: float) -> (datetime, datetime):
    """简单工作时间模型：每日8小时，跨日顺延。"""
    day_hours = 8
    end = start
    remaining = hours
    while remaining > 0:
        take = min(day_hours, remaining)
        end = end + timedelta(hours=take)
        remaining -= take
        if remaining > 0:
            # 跳到下一天早上8点
            end = (end.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1))
    return start, end


@router.post("/schedule/run", tags=["Scheduling"])
def run_scheduling(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    生成简易排程：
    - 按设备维度为工单工序排时间
    - 假设产能速率 1 单位/小时；每日8小时
    - 仅对 `released` 与 `in_progress` 的工单进行排程
    """
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    equipment_cursor: Dict[int, datetime] = {}
    tasks: List[Dict[str, Any]] = []

    ops = db.query(WorkOrderOperation).join(WorkOrder).filter(
        WorkOrder.status.in_(["released", "in_progress"])
    ).order_by(WorkOrder.priority.asc(), WorkOrder.id.asc(), WorkOrderOperation.sequence.asc()).all()

    for op in ops:
        equip_id = op.equipment_id or -1  # 未分配设备归到 -1
        cursor = equipment_cursor.get(equip_id, op.planned_start_date or now)
        # 计算工时：速率1单位/小时
        qty = max(op.planned_quantity - op.completed_quantity, 0)
        hours = qty
        start, end = working_slots(cursor, hours)
        equipment_cursor[equip_id] = end

        tasks.append({
            "work_order_id": op.work_order_id,
            "operation_id": op.operation_id,
            "work_order_operation_id": op.id,
            "equipment_id": equip_id,
            "sequence": op.sequence,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "planned_quantity": op.planned_quantity,
            "remaining_quantity": qty,
        })

    # 简单的负荷统计（每设备累计工时）
    loads: Dict[int, float] = {}
    for t in tasks:
        equip = t["equipment_id"]
        s = datetime.fromisoformat(t["start"]) 
        e = datetime.fromisoformat(t["end"]) 
        hours = (e - s).total_seconds() / 3600
        loads[equip] = loads.get(equip, 0.0) + hours

    # 交期预警：若任务结束时间晚于工单计划完工时间
    warnings: List[Dict[str, Any]] = []
    for t in tasks:
        wo = db.query(WorkOrder).filter(WorkOrder.id == t["work_order_id"]).first()
        if wo and wo.planned_end_date:
            end = datetime.fromisoformat(t["end"]) 
            if end > wo.planned_end_date:
                warnings.append({
                    "work_order_id": wo.id,
                    "code": wo.code,
                    "planned_end_date": wo.planned_end_date.isoformat(),
                    "task_end": end.isoformat(),
                    "delay_hours": (end - wo.planned_end_date).total_seconds() / 3600
                })

    return {"tasks": tasks, "loads": loads, "warnings": warnings}


@router.get("/schedule", tags=["Scheduling"])
def get_schedule(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """根据当前 released/in_progress 工单返回简易排程（同 run）。"""
    return run_scheduling(db)