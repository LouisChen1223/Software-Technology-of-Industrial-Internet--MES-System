import http from './http'

export type ReportType = 'start' | 'complete' | 'pause' | 'resume' | 'scrap'

export interface WorkReport {
  id?: number
  work_order_id: number
  work_order_operation_id?: number
  report_type: ReportType
  quantity?: number
  operator_id?: number
  equipment_id?: number
  shift_id?: number
  barcode?: string
  notes?: string
  report_time?: string
  created_at?: string
}

export const reportApi = {
  async create(payload: WorkReport): Promise<WorkReport> {
    const resp = await http.post('/work-reports', payload)
    return resp.data
  },
  async list(params?: { work_order_id?: number }): Promise<WorkReport[]> {
    const resp = await http.get('/work-reports', { params })
    return resp.data
  }
}