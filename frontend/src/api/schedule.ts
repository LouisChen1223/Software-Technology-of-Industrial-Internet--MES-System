import http from './http'

export interface ScheduleTask {
  work_order_id: number
  operation_id: number
  work_order_operation_id: number
  equipment_id: number
  sequence: number
  start: string
  end: string
  planned_quantity: number
  remaining_quantity: number
}

export interface ScheduleResult {
  tasks: ScheduleTask[]
  loads: Record<string, number>
  warnings: Array<{
    work_order_id: number
    code: string
    planned_end_date: string
    task_end: string
    delay_hours: number
  }>
}

export const scheduleApi = {
  async run(): Promise<ScheduleResult> {
    const resp = await http.post('/schedule/run')
    return resp.data
  },
  async get(): Promise<ScheduleResult> {
    const resp = await http.get('/schedule')
    return resp.data
  }
}