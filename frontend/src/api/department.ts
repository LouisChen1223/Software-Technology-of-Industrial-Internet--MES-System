import http from './http'
import type { Department, DepartmentCreate, DepartmentUpdate } from '@/types/department'

const base = '/departments'

export const listDepartments = (params?: { skip?: number; limit?: number; active?: number }) => {
  return http.get<Department[]>(base, { params })
}

export const getDepartment = (id: number) => {
  return http.get<Department>(`${base}/${id}`)
}

export const createDepartment = (data: DepartmentCreate) => {
  return http.post<Department>(base, data)
}

export const updateDepartment = (id: number, data: DepartmentUpdate) => {
  return http.put<Department>(`${base}/${id}`, data)
}

export const deleteDepartment = (id: number) => {
  return http.delete(`${base}/${id}`)
}
