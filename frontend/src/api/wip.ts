import http from './http'

export interface WipItem {
  id: number
  work_order_id: number
  operation_id: number
  material_id: number
  batch_number?: string
  serial_number?: string
  quantity: number
  status: string
  location?: string
  created_at?: string
  updated_at?: string
  work_order?: { id: number; code: string }
  operation?: { id: number; name: string; code?: string }
}

export const wipApi = {
  async list(params?: { work_order_id?: number; status?: string; skip?: number; limit?: number }) {
    const resp = await http.get('/wip-tracking', { params })
    return resp.data as WipItem[]
  },
  async traceByBatch(batch: string) {
    const resp = await http.get(`/wip-tracking/batch/${encodeURIComponent(batch)}`)
    return resp.data as WipItem[]
  },
  async traceBySerial(serial: string) {
    const resp = await http.get(`/wip-tracking/serial/${encodeURIComponent(serial)}`)
    return resp.data as WipItem[]
  }
}