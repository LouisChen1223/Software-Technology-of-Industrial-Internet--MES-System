export interface Department {
  id: number
  code: string
  name: string
  manager?: string
  description?: string
  active: number
  created_at: string
  updated_at: string
}

export interface DepartmentCreate {
  code: string
  name: string
  manager?: string
  description?: string
  active?: number
}

export interface DepartmentUpdate {
  code?: string
  name?: string
  manager?: string
  description?: string
  active?: number
}
