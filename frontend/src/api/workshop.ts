import http from './http'
import type { Workshop, WorkshopCreate, WorkshopUpdate } from '@/types/workshop'

const base = '/workshops'

export const listWorkshops = (params?: { skip?: number; limit?: number; department_id?: number; active?: number }) => {
  return http.get<Workshop[]>(base, { params })
}

export const getWorkshop = (id: number) => {
  return http.get<Workshop>(`${base}/${id}`)
}

export const createWorkshop = (data: WorkshopCreate) => {
  return http.post<Workshop>(base, data)
}

export const updateWorkshop = (id: number, data: WorkshopUpdate) => {
  return http.put<Workshop>(`${base}/${id}`, data)
}

export const deleteWorkshop = (id: number) => {
  return http.delete(`${base}/${id}`)
}
