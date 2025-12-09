// 主数据类型定义

export interface Material {
  id: string // 唯一ID
  code: string // 物料编码
  name: string
  spec?: string // 规格型号
  uom: string // 单位
  type?: string // 原材料/半成品/成品/耗材
  version?: string // 版本号
  active: boolean
  createdAt: string
  updatedAt: string
}

export interface BomHeader {
  id: string
  productCode: string // 成品编码
  productName: string
  version: string
  status: 'draft' | 'released' | 'archived'
  createdAt: string
  updatedAt: string
}

export interface BomItem {
  id: string
  headerId: string
  materialCode: string
  materialName: string
  qty: number
  scrapRate?: number // 损耗率
  remark?: string
}

export interface Operation {
  id: string
  code: string // 工序编码
  name: string
  description?: string
  stdDurationMin?: number // 标准工时(分钟)
  workstationCode?: string // 关联缺省工位
  needTooling?: boolean
  qualityCheck?: boolean
}

export interface Routing {
  id: string
  productCode: string
  version: string
  status: 'draft' | 'released'
  ops: RoutingOp[]
}

export interface RoutingOp {
  seq: number
  operationCode: string
  operationName: string
  equipmentCode?: string
  toolingCode?: string
}

export interface Equipment {
  id: string
  code: string
  name: string
  type?: string // 设备类型
  vendor?: string
  lineCode?: string
  workstationCode?: string
  enabled: boolean
  capacityPerHour?: number
}

export interface Tooling {
  id: string
  code: string
  name: string
  type?: string
  description?: string
  usable: boolean
}

export interface Person {
  id: string
  empNo: string
  name: string
  role: string // operator / qc / supervisor
  shiftCode?: string
  active: boolean
}

export interface Shift {
  id: string
  code: string
  name: string
  start: string // HH:mm
  end: string // HH:mm
  description?: string
  active: boolean
}

// 仓库与计量单位
export interface Warehouse {
  id: string
  code: string // 仓库编码
  name: string // 仓库名称
  type?: string // 原材料/半成品/成品/在制品/不良品
  address?: string
  manager?: string
  active: boolean
}

export interface Uom {
  id: string
  code: string // 单位编码，如 PCS/SET/KG
  name?: string // 单位名称
  precision?: number // 小数位数
  active: boolean
}

export interface MasterChangeLog {
  id: string
  entity: string
  entityId: string
  action: 'create' | 'update' | 'delete'
  operator: string
  time: string
  diff?: Record<string, any>
}
