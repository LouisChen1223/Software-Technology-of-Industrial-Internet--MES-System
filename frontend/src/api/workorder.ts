import http from './http'
import type { WorkOrder } from '@/types/order'

// 转换前端数据到后端格式
function toBackendFormat(data: Partial<WorkOrder>): any {
  return {
    code: data.code || data.woNo || '',
    product_id: data.product_id || 1, // 默认产品ID，应该从下拉列表选择
    bom_id: data.bom_id,
    routing_id: data.routing_id,
    planned_quantity: data.planned_quantity || data.qty || 0,
    completed_quantity: data.completed_quantity || 0,
    scrapped_quantity: data.scrapped_quantity || 0,
    status: data.status || 'draft',
    priority: data.priority || 5,
    planned_start_date: data.planned_start_date || data.startDate,
    planned_end_date: data.planned_end_date || data.dueDate,
    customer: data.customer,
    notes: data.notes || data.remark
  }
}

// 转换后端数据到前端显示格式
function toFrontendFormat(data: any): WorkOrder {
  return {
    ...data,
    woNo: data.code,
    qty: data.planned_quantity,
    startDate: data.planned_start_date,
    dueDate: data.planned_end_date,
    remark: data.notes
  }
}

export const workorderApi = {
  async list(): Promise<WorkOrder[]> {
    const resp = await http.get('/work-orders')
    return resp.data.map(toFrontendFormat)
  },
  
  async get(id: string): Promise<WorkOrder> {
    const resp = await http.get(`/work-orders/${id}`)
    return toFrontendFormat(resp.data)
  },
  
  async create(data: Partial<WorkOrder>): Promise<WorkOrder> {
    const backendData = toBackendFormat(data)
    const resp = await http.post('/work-orders', backendData)
    return toFrontendFormat(resp.data)
  },
  
  async update(id: string, data: Partial<WorkOrder>): Promise<WorkOrder> {
    const backendData = toBackendFormat(data)
    const resp = await http.put(`/work-orders/${id}`, backendData)
    return toFrontendFormat(resp.data)
  },
  
  async upsert(o: WorkOrder): Promise<WorkOrder> {
    if (o.id) {
      return await this.update(o.id.toString(), o)
    } else {
      return await this.create(o)
    }
  },
  
  async remove(id: string): Promise<void> {
    await http.delete(`/work-orders/${id}`)
  },
  
  async release(id: string): Promise<WorkOrder> {
    const resp = await http.post(`/work-orders/${id}/release`)
    return toFrontendFormat(resp.data)
  },
  async start(id: string): Promise<WorkOrder> {
    const resp = await http.post(`/work-orders/${id}/start`)
    return toFrontendFormat(resp.data)
  },
  async complete(id: string): Promise<WorkOrder> {
    const resp = await http.post(`/work-orders/${id}/complete`)
    return toFrontendFormat(resp.data)
  },
  async cancel(id: string): Promise<WorkOrder> {
    const resp = await http.post(`/work-orders/${id}/cancel`)
    return toFrontendFormat(resp.data)
  }
}
