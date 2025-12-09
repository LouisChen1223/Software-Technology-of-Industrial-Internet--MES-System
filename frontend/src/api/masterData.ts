import http from './http'
import type { Material, BomHeader, BomItem, Operation, Routing, Equipment, Tooling, Person, Shift, Warehouse, Uom } from '@/types/master'

// UOM API
export const uomApi = {
  async list(): Promise<Uom[]> {
    const resp = await http.get('/uoms')
    return resp.data
  },
  async create(data: Partial<Uom>): Promise<Uom> {
    const resp = await http.post('/uoms', data)
    return resp.data
  },
  async update(id: number, data: Partial<Uom>): Promise<Uom> {
    const resp = await http.put(`/uoms/${id}`, data)
    return resp.data
  },
  async upsert(u: Uom): Promise<Uom> {
    if (u.id) {
      return await this.update(u.id, u)
    } else {
      return await this.create(u)
    }
  },
  async remove(id: number): Promise<void> {
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
  async update(id: number, data: Partial<Warehouse>): Promise<Warehouse> {
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
  async list(): Promise<Material[]> {
    const resp = await http.get('/materials')
    return resp.data
  },
  async create(data: Partial<Material>): Promise<Material> {
    const resp = await http.post('/materials', data)
    return resp.data
  },
  async update(id: number, data: Partial<Material>): Promise<Material> {
    const resp = await http.put(`/materials/${id}`, data)
    return resp.data
  },
  async remove(id: number): Promise<void> {
    await http.delete(`/materials/${id}`)
  }
}

// BOM API
export const bomApi = {
  async headers(): Promise<BomHeader[]> {
    const resp = await http.get('/boms')
    return resp.data
  },
  async items(bomId: number): Promise<BomItem[]> {
    const resp = await http.get(`/boms/${bomId}`)
    return resp.data.items || []
  },
  async createHeader(data: Partial<BomHeader>): Promise<BomHeader> {
    const resp = await http.post('/boms', data)
    return resp.data
  },
  async addItem(bomId: number, item: Partial<BomItem>): Promise<BomItem> {
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
  async update(id: number, data: Partial<Operation>): Promise<Operation> {
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
  async update(id: number, data: Partial<Routing>): Promise<Routing> {
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
  async update(id: number, data: Partial<Equipment>): Promise<Equipment> {
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
  async update(id: number, data: Partial<Tooling>): Promise<Tooling> {
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
  async update(id: number, data: Partial<Person>): Promise<Person> {
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
  async update(id: number, data: Partial<Shift>): Promise<Shift> {
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
