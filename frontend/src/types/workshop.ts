export interface Workshop {
  id: number
  code: string
  name: string
  supervisor?: string
  location?: string
  description?: string
  active: number
  created_at: string
  updated_at: string
}

export interface WorkshopCreate {
  code: string
  name: string
  supervisor?: string
  location?: string
  description?: string
  active?: number
}

export interface WorkshopUpdate {
  code?: string
  name?: string
  supervisor?: string
  location?: string
  description?: string
  active?: number
}
