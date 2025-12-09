import http from './http'
import type { Material, BomHeader, BomItem, Operation, Routing, Equipment, Tooling, Person, Shift, Warehouse, Uom } from '@/types/master'

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

// Warehouse API
export const warehouseApi = {
  async list(): Promise<Warehouse[]> {
    const resp = await http.get('/warehouses')
    return resp.data
  },
  async create(data: Partial<Warehouse>): Promise<Warehouse> {
    const resp = await http.post('/warehouses', data)
    return resp.data
  },
  async update(id: number | string, data: Partial<Warehouse>): Promise<Warehouse> {
    const resp = await http.put(`/warehouses/${id}`, data)
    return resp.data
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
  async headers(): Promise<BomHeader[]> {
    const resp = await http.get('/boms')
    return resp.data
  },
  async items(bomId: number | string): Promise<BomItem[]> {
    const resp = await http.get(`/boms/${bomId}`)
    return resp.data.items || []
  },
  async createHeader(data: Partial<BomHeader>): Promise<BomHeader> {
    const resp = await http.post('/boms', data)
    return resp.data
  },
  async addItem(bomId: number | string, item: Partial<BomItem>): Promise<BomItem> {
    const resp = await http.post(`/boms/${bomId}/items`, item)
    return resp.data
  }
}

// Operation API
export const operationApi = {
  async list(): Promise<Operation[]> {
    const resp = await http.get('/operations')
    return resp.data
  },
  async create(data: Partial<Operation>): Promise<Operation> {
    const resp = await http.post('/operations', data)
    return resp.data
  },
  async update(id: number | string, data: Partial<Operation>): Promise<Operation> {
    const resp = await http.put(`/operations/${id}`, data)
    return resp.data
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
  async create(data: Partial<Routing>): Promise<Routing> {
    const resp = await http.post('/routings', data)
    return resp.data
  },
  async update(id: number | string, data: Partial<Routing>): Promise<Routing> {
    const resp = await http.put(`/routings/${id}`, data)
    return resp.data
  },
  async upsert(r: Routing): Promise<Routing> {
    if (r.id) {
      return await this.update(r.id, r)
    } else {
      return await this.create(r)
    }
  },
  async remove(id: number): Promise<void> {
    await http.delete(`/routings/${id}`)
  }
}

// Equipment API
export const equipmentApi = {
  async list(): Promise<Equipment[]> {
    const resp = await http.get('/equipment')
    return resp.data
  },
  async create(data: Partial<Equipment>): Promise<Equipment> {
    const resp = await http.post('/equipment', data)
    return resp.data
  },
  async update(id: number | string, data: Partial<Equipment>): Promise<Equipment> {
    const resp = await http.put(`/equipment/${id}`, data)
    return resp.data
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
  async list(): Promise<Tooling[]> {
    const resp = await http.get('/tooling')
    return resp.data
  },
  async create(data: Partial<Tooling>): Promise<Tooling> {
    const resp = await http.post('/tooling', data)
    return resp.data
  },
  async update(id: number | string, data: Partial<Tooling>): Promise<Tooling> {
    const resp = await http.put(`/tooling/${id}`, data)
    return resp.data
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
  async list(): Promise<Person[]> {
    const resp = await http.get('/personnel')
    return resp.data
  },
  async create(data: Partial<Person>): Promise<Person> {
    const resp = await http.post('/personnel', data)
    return resp.data
  },
  async update(id: number | string, data: Partial<Person>): Promise<Person> {
    const resp = await http.put(`/personnel/${id}`, data)
    return resp.data
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
  async list(): Promise<Shift[]> {
    const resp = await http.get('/shifts')
    return resp.data
  },
  async create(data: Partial<Shift>): Promise<Shift> {
    const resp = await http.post('/shifts', data)
    return resp.data
  },
  async update(id: number | string, data: Partial<Shift>): Promise<Shift> {
    const resp = await http.put(`/shifts/${id}`, data)
    return resp.data
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
