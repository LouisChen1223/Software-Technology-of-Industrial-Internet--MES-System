export type WorkOrderStatus = 'draft' | 'released' | 'in_progress' | 'completed' | 'cancelled'

export interface WorkOrder {
  id?: number
  code: string  // 工单编号
  product_id: number  // 产品ID
  bom_id?: number
  routing_id?: number
  planned_quantity: number  // 计划数量
  completed_quantity?: number
  scrapped_quantity?: number
  status?: WorkOrderStatus
  priority?: number
  planned_start_date?: string  // ISO datetime
  planned_end_date?: string    // ISO datetime
  actual_start_date?: string
  actual_end_date?: string
  customer?: string
  notes?: string
  created_at?: string
  updated_at?: string
  
  // 前端显示用的额外字段
  woNo?: string
  productCode?: string
  productName?: string
  qty?: number
  uom?: string
  startDate?: string
  dueDate?: string
  remark?: string
}
