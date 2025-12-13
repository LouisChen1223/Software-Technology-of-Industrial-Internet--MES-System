import http from './http'
import type { Material, BomHeader, BomItem, Operation, Routing, Equipment, Tooling, Person, Shift, Warehouse, Uom, MaterialType } from '@/types/master'

// UOM API
export const uomApi = {
  // 字段映射：后端无 precision/active，前端需要展示，提供合理默认
  toClient(u: any): Uom {
    return {
      id: String(u.id),
      code: u.code,
      name: u.name,
      precision: u.precision ?? 0,
      // 后端可能返回 0/1，需转为布尔
      active: u.active === undefined ? true : !!u.active,
    }
  },
  toServer(data: Partial<Uom>): any {
    const payload: any = {}
    if (data.code !== undefined) payload.code = data.code
    if (data.name !== undefined) payload.name = data.name
    if (data.precision !== undefined) payload.precision = Number(data.precision)
    if (data.active !== undefined) payload.active = data.active ? 1 : 0
    return payload
  },
  async list(): Promise<Uom[]> {
    const resp = await http.get('/uoms')
    return Array.isArray(resp.data) ? resp.data.map(this.toClient) : []
  },
  async create(data: Partial<Uom>): Promise<Uom> {
    const resp = await http.post('/uoms', this.toServer(data))
    return this.toClient(resp.data)
  },
  async update(id: number | string, data: Partial<Uom>): Promise<Uom> {
    const resp = await http.put(`/uoms/${id}`, this.toServer(data))
    return this.toClient(resp.data)
  },
  async upsert(u: Uom): Promise<Uom> {
    if (u.id) {
      return await this.update(u.id, u)
    } else {
      return await this.create(u)
    }
  },
  async remove(id: number | string): Promise<void> {
    await http.delete(`/uoms/${id}`)
  }
}

// Material Type API
export const materialTypeApi = {
  toClient(t: any): MaterialType {
    return {
      id: String(t.id),
      code: t.code,
      name: t.name,
      active: t.active === undefined ? true : !!t.active,
    }
  },
  toServer(data: Partial<MaterialType>): any {
    const payload: any = {}
    if (data.code !== undefined) payload.code = data.code
    if (data.name !== undefined) payload.name = data.name
    if (data.active !== undefined) payload.active = data.active ? 1 : 0
    return payload
  },
  async list(): Promise<MaterialType[]> {
    const resp = await http.get('/material-types')
    return Array.isArray(resp.data) ? resp.data.map(this.toClient) : []
  },
  async create(data: Partial<MaterialType>): Promise<MaterialType> {
    const resp = await http.post('/material-types', this.toServer(data))
    return this.toClient(resp.data)
  },
  async update(id: number | string, data: Partial<MaterialType>): Promise<MaterialType> {
    const resp = await http.put(`/material-types/${id}`, this.toServer(data))
    return this.toClient(resp.data)
  },
  async upsert(t: MaterialType): Promise<MaterialType> {
    if (t.id) {
      return await this.update(t.id, t)
    } else {
      return await this.create(t)
    }
  },
  async remove(id: number | string): Promise<void> {
    await http.delete(`/material-types/${id}`)
  }
}

// Warehouse API
export const warehouseApi = {
  toClient(w: any): Warehouse {
    return {
      id: String(w.id),
      code: w.code,
      name: w.name,
      type: w.warehouse_type || '',
      address: w.location || '',
      manager: w.manager || '',
      // 后端无 active，默认启用
      active: w.active === undefined ? true : !!w.active,
    }
  },
  toServer(data: Partial<Warehouse>): any {
    const payload: any = {}
    if (data.code !== undefined) payload.code = data.code
    if (data.name !== undefined) payload.name = data.name
    if (data.type !== undefined) payload.warehouse_type = data.type
    if (data.address !== undefined) payload.location = data.address
    if (data.manager !== undefined) payload.manager = data.manager
    if (data.active !== undefined) payload.active = data.active ? 1 : 0
    return payload
  },
  async list(): Promise<Warehouse[]> {
    const resp = await http.get('/warehouses')
    return Array.isArray(resp.data) ? resp.data.map(this.toClient) : []
  },
  async create(data: Partial<Warehouse>): Promise<Warehouse> {
    const resp = await http.post('/warehouses', this.toServer(data))
    return this.toClient(resp.data)
  },
  async update(id: number | string, data: Partial<Warehouse>): Promise<Warehouse> {
    const resp = await http.put(`/warehouses/${id}`, this.toServer(data))
    return this.toClient(resp.data)
  },
  async upsert(w: Warehouse): Promise<Warehouse> {
    if (w.id) {
      return await this.update(w.id, w)
    } else {
      return await this.create(w)
    }
  },
  async remove(id: number): Promise<void> {
    await http.delete(`/warehouses/${id}`)
  }
}

// Material API
export const materialApi = {
  // 将后端字段映射为前端 Material 结构
  toClient(m: any): Material {
    return {
      id: String(m.id),
      code: m.code,
      name: m.name,
      spec: m.specification ?? '',
      // 后端为 uom_id（数字），前端展示为字符串；若无则空字符串
      uom: m.uom_id != null ? String(m.uom_id) : '',
      type: m.material_type ?? '',
      version: '',
      active: true,
      createdAt: m.created_at ?? '',
      updatedAt: m.updated_at ?? ''
    }
  },
  // 将前端 Material 结构映射为后端字段
  toServer(data: Partial<Material>): any {
    const payload: any = {}
    if (data.code !== undefined) payload.code = data.code
    if (data.name !== undefined) payload.name = data.name
    if (data.spec !== undefined) payload.specification = data.spec
    if (data.type !== undefined) payload.material_type = data.type
    // 尝试将 uom 转换为数字 ID；否则不传（保持后端原值）
    if (data.uom !== undefined) {
      const n = Number(data.uom)
      if (!Number.isNaN(n)) payload.uom_id = n
    }
    return payload
  },
  async list(): Promise<Material[]> {
    const resp = await http.get('/materials')
    return Array.isArray(resp.data) ? resp.data.map(this.toClient) : []
  },
  async create(data: Partial<Material>): Promise<Material> {
    const resp = await http.post('/materials', this.toServer(data))
    return this.toClient(resp.data)
  },
  async update(id: number | string, data: Partial<Material>): Promise<Material> {
    const resp = await http.put(`/materials/${id}`, this.toServer(data))
    return this.toClient(resp.data)
  },
  async remove(id: number | string): Promise<void> {
    await http.delete(`/materials/${id}`)
  }
}

// BOM API
export const bomApi = {
  async list(): Promise<BomHeader[]> {
    const resp = await http.get('/boms')
    return resp.data
  },
  async detail(bomId: number | string): Promise<{ header: BomHeader; items: BomItem[] }> {
    const resp = await http.get(`/boms/${bomId}`)
    return { header: resp.data, items: resp.data.items || [] }
  },
  async byProduct(productId: number | string, opts?: { version?: string; activeOnly?: boolean | number }): Promise<BomHeader[]> {
    const params: any = {}
    if (opts?.version) params.version = opts.version
    if (opts?.activeOnly !== undefined) params.active_only = Number(opts.activeOnly) === 1 || opts.activeOnly === true ? 1 : 0
    const resp = await http.get(`/boms/by-product/${productId}`, { params })
    return resp.data
  },
  async create(payload: { code: string; name: string; product_id: number; version?: string; quantity?: number; is_active?: number; description?: string; items?: Array<{ material_id: number; quantity: number; sequence?: number; scrap_rate?: number; description?: string }> }): Promise<BomHeader> {
    const resp = await http.post('/boms', payload)
    return resp.data
  },
  async update(bomId: number | string, payload: Partial<{ code: string; name: string; product_id: number; version: string; quantity: number; is_active: number; description: string; items: Array<{ material_id: number; quantity: number; sequence?: number; scrap_rate?: number; description?: string }> }>): Promise<BomHeader> {
    const resp = await http.put(`/boms/${bomId}`, payload)
    return resp.data
  },
  async remove(bomId: number | string): Promise<void> {
    await http.delete(`/boms/${bomId}`)
  }
}

// Operation API
export const operationApi = {
  toClient(o: any): Operation {
    return {
      id: String(o.id),
      code: o.code,
      name: o.name,
      description: o.description || '',
      stdDurationMin: o.standard_time ?? 0,
      workstationCode: o.workstation_code || '',
      needTooling: !!o.need_tooling,
      qualityCheck: !!o.quality_check,
    }
  },
  toServer(data: Partial<Operation>): any {
    const payload: any = {}
    if (data.code !== undefined) payload.code = data.code
    if (data.name !== undefined) payload.name = data.name
    if (data.description !== undefined) payload.description = data.description
    if (data.stdDurationMin !== undefined) payload.standard_time = Number(data.stdDurationMin)
    if (data.workstationCode !== undefined) payload.workstation_code = data.workstationCode
    if (data.needTooling !== undefined) payload.need_tooling = data.needTooling ? 1 : 0
    if (data.qualityCheck !== undefined) payload.quality_check = data.qualityCheck ? 1 : 0
    return payload
  },
  async list(): Promise<Operation[]> {
    const resp = await http.get('/operations')
    return Array.isArray(resp.data) ? resp.data.map(this.toClient) : []
  },
  async create(data: Partial<Operation>): Promise<Operation> {
    const resp = await http.post('/operations', this.toServer(data))
    return this.toClient(resp.data)
  },
  async update(id: number | string, data: Partial<Operation>): Promise<Operation> {
    const resp = await http.put(`/operations/${id}`, this.toServer(data))
    return this.toClient(resp.data)
  },
  async upsert(op: Operation): Promise<Operation> {
    if (op.id) {
      return await this.update(op.id, op)
    } else {
      return await this.create(op)
    }
  },
  async remove(id: number): Promise<void> {
    await http.delete(`/operations/${id}`)
  }
}

// Routing API
export const routingApi = {
  async list(): Promise<Routing[]> {
    const resp = await http.get('/routings')
    return resp.data
  },
  async byProduct(productId: number | string, opts?: { version?: string; activeOnly?: boolean | number }): Promise<Routing[]> {
    const params: any = {}
    if (opts?.version) params.version = opts.version
    if (opts?.activeOnly !== undefined) params.active_only = Number(opts.activeOnly) === 1 || opts.activeOnly === true ? 1 : 0
    const resp = await http.get(`/routings/by-product/${productId}`, { params })
    return resp.data
  },
  async create(payload: { code: string; name: string; product_id: number; version?: string; is_active?: number; description?: string; items?: Array<{ operation_id: number; sequence: number; equipment_id?: number; standard_time?: number; setup_time?: number; description?: string }> }): Promise<Routing> {
    const resp = await http.post('/routings', payload)
    return resp.data
  },
  async update(id: number | string, payload: Partial<{ code: string; name: string; product_id: number; version: string; is_active: number; description: string; items: Array<{ operation_id: number; sequence: number; equipment_id?: number; standard_time?: number; setup_time?: number; description?: string }> }>): Promise<Routing> {
    const resp = await http.put(`/routings/${id}`, payload)
    return resp.data
  },
  async upsert(r: any): Promise<Routing> {
    if (r.id) {
      return await this.update(r.id, r)
    } else {
      return await this.create(r)
    }
  },
  async remove(id: number | string): Promise<void> {
    await http.delete(`/routings/${id}`)
  }
}

// Equipment API
export const equipmentApi = {
  toClient(e: any): Equipment {
    return {
      id: String(e.id),
      code: e.code,
      name: e.name,
      type: e.equipment_type || '',
      vendor: e.manufacturer || '',
      lineCode: e.line_code || '',
      workstationCode: e.workstation_code || '',
      enabled: e.status ? e.status !== 'maintenance' && e.status !== 'fault' : true,
      capacityPerHour: e.capacity ?? 0
    }
  },
  toServer(data: Partial<Equipment>): any {
    const payload: any = {}
    if (data.code !== undefined) payload.code = data.code
    if (data.name !== undefined) payload.name = data.name
    if (data.type !== undefined) payload.equipment_type = data.type
    if (data.vendor !== undefined) payload.manufacturer = data.vendor
    if (data.capacityPerHour !== undefined) payload.capacity = Number(data.capacityPerHour)
    if (data.workstationCode !== undefined) payload.workstation_code = data.workstationCode
    if (data.enabled !== undefined) payload.status = data.enabled ? 'idle' : 'maintenance'
    return payload
  },
  async list(): Promise<Equipment[]> {
    const resp = await http.get('/equipment')
    return Array.isArray(resp.data) ? resp.data.map(this.toClient) : []
  },
  async create(data: Partial<Equipment>): Promise<Equipment> {
    const resp = await http.post('/equipment', this.toServer(data))
    return this.toClient(resp.data)
  },
  async update(id: number | string, data: Partial<Equipment>): Promise<Equipment> {
    const resp = await http.put(`/equipment/${id}`, this.toServer(data))
    return this.toClient(resp.data)
  },
  async upsert(e: Equipment): Promise<Equipment> {
    if (e.id) {
      return await this.update(e.id, e)
    } else {
      return await this.create(e)
    }
  },
  async remove(id: number): Promise<void> {
    await http.delete(`/equipment/${id}`)
  }
}

// Tooling API
export const toolingApi = {
  toClient(t: any): Tooling {
    return {
      id: String(t.id),
      code: t.code,
      name: t.name,
      type: t.tooling_type || '',
      description: t.description || '',
      usable: t.status ? t.status === 'available' : true
    }
  },
  toServer(data: Partial<Tooling>): any {
    const payload: any = {}
    if (data.code !== undefined) payload.code = data.code
    if (data.name !== undefined) payload.name = data.name
    if (data.type !== undefined) payload.tooling_type = data.type
    if (data.description !== undefined) payload.description = data.description
    if (data.usable !== undefined) payload.status = data.usable ? 'available' : 'maintenance'
    return payload
  },
  async list(): Promise<Tooling[]> {
    const resp = await http.get('/tooling')
    return Array.isArray(resp.data) ? resp.data.map(this.toClient) : []
  },
  async create(data: Partial<Tooling>): Promise<Tooling> {
    const resp = await http.post('/tooling', this.toServer(data))
    return this.toClient(resp.data)
  },
  async update(id: number | string, data: Partial<Tooling>): Promise<Tooling> {
    const resp = await http.put(`/tooling/${id}`, this.toServer(data))
    return this.toClient(resp.data)
  },
  async upsert(t: Tooling): Promise<Tooling> {
    if (t.id) {
      return await this.update(t.id, t)
    } else {
      return await this.create(t)
    }
  },
  async remove(id: number): Promise<void> {
    await http.delete(`/tooling/${id}`)
  }
}

// Personnel API
export const personApi = {
  toClient(p: any): Person {
    return {
      id: String(p.id),
      empNo: p.code,
      name: p.name,
      role: p.position || 'operator',
      shiftCode: p.shift_code || '',
      active: p.status ? p.status === 'active' : true
    }
  },
  toServer(data: Partial<Person>): any {
    const payload: any = {}
    if (data.empNo !== undefined) payload.code = data.empNo
    if (data.name !== undefined) payload.name = data.name
    if (data.role !== undefined) payload.position = data.role
    if (data.shiftCode !== undefined) payload.shift_code = data.shiftCode
    if (data.active !== undefined) payload.status = data.active ? 'active' : 'inactive'
    return payload
  },
  async list(): Promise<Person[]> {
    const resp = await http.get('/personnel')
    return Array.isArray(resp.data) ? resp.data.map(this.toClient) : []
  },
  async create(data: Partial<Person>): Promise<Person> {
    const resp = await http.post('/personnel', this.toServer(data))
    return this.toClient(resp.data)
  },
  async update(id: number | string, data: Partial<Person>): Promise<Person> {
    const resp = await http.put(`/personnel/${id}`, this.toServer(data))
    return this.toClient(resp.data)
  },
  async upsert(p: Person): Promise<Person> {
    if (p.id) {
      return await this.update(p.id, p)
    } else {
      return await this.create(p)
    }
  },
  async remove(id: number): Promise<void> {
    await http.delete(`/personnel/${id}`)
  }
}

// Shift API
export const shiftApi = {
  toClient(s: any): Shift {
    return {
      id: String(s.id),
      code: s.code,
      name: s.name,
      start: s.start_time,
      end: s.end_time,
      description: s.description || '',
      active: s.active === undefined ? true : !!s.active
    }
  },
  toServer(data: Partial<Shift>): any {
    const payload: any = {}
    if (data.code !== undefined) payload.code = data.code
    if (data.name !== undefined) payload.name = data.name
    if (data.start !== undefined) payload.start_time = data.start
    if (data.end !== undefined) payload.end_time = data.end
    if (data.description !== undefined) payload.description = data.description
    if (data.active !== undefined) payload.active = data.active ? 1 : 0
    return payload
  },
  async list(): Promise<Shift[]> {
    const resp = await http.get('/shifts')
    return Array.isArray(resp.data) ? resp.data.map(this.toClient) : []
  },
  async create(data: Partial<Shift>): Promise<Shift> {
    const resp = await http.post('/shifts', this.toServer(data))
    return this.toClient(resp.data)
  },
  async update(id: number | string, data: Partial<Shift>): Promise<Shift> {
    const resp = await http.put(`/shifts/${id}`, this.toServer(data))
    return this.toClient(resp.data)
  },
  async upsert(s: Shift): Promise<Shift> {
    if (s.id) {
      return await this.update(s.id, s)
    } else {
      return await this.create(s)
    }
  },
  async remove(id: number): Promise<void> {
    await http.delete(`/shifts/${id}`)
  }
}

// 不再需要 ensureSeed 函数，数据由后端初始化脚本提供
