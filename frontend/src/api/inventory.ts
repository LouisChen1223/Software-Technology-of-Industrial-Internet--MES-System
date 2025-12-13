import http from './http'

export interface InventoryItemQuery {
  warehouse_id?: number
  material_id?: number
  batch_number?: string
  location?: string
  skip?: number
  limit?: number
}

export interface InventoryItem {
  id: number
  warehouse_id: number
  material_id: number
  batch_number?: string
  location?: string
  quantity: number
  available_quantity: number
  unit_price?: number
}

export interface MaterialTransactionPayload {
  transaction_type: 'pick' | 'issue' | 'return' | 'receive'
  material_id: number
  warehouse_id: number
  work_order_id?: number
  batch_number?: string
  quantity: number
  from_location?: string
  to_location?: string
  operator_id?: number
  reference_no?: string
  unit_price?: number
}

export interface MaterialPickItemPayload {
  material_id: number
  quantity: number
  uom_id?: number
  warehouse_id?: number
}

export interface MaterialPickPayload {
  code: string
  work_order_id?: number
  warehouse_id: number
  pick_type: 'normal' | 'bom'
  status?: 'draft' | 'confirmed' | 'completed'
  items: MaterialPickItemPayload[]
}

export const inventoryApi = {
  async list(params: InventoryItemQuery = {}) {
    const resp = await http.get('/inventory', { params })
    return resp.data as InventoryItem[]
  },
  async trans(payload: MaterialTransactionPayload) {
    const resp = await http.post('/material-transactions', payload)
    return resp.data
  },
  async createPick(payload: MaterialPickPayload) {
    const resp = await http.post('/material-picks', payload)
    return resp.data
  },
  async confirmPick(pick_id: number) {
    const resp = await http.post(`/material-picks/${pick_id}/confirm`)
    return resp.data
  },
  async completePick(pick_id: number) {
    const resp = await http.post(`/material-picks/${pick_id}/complete`)
    return resp.data
  },
  async createPickFromBOM(work_order_id: number, warehouse_id: number) {
    const resp = await http.post('/material-picks/bom', null, { params: { work_order_id, warehouse_id } })
    return resp.data
  }
}