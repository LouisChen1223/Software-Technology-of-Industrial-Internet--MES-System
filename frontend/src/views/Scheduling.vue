<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>排程甘特图 / 负荷分析 / 交期预警</span>
        <div class="actions">
          <el-button type="primary" @click="run">重新排程</el-button>
          <span class="scale">比例 (px/小时)：</span>
          <el-slider v-model="scale" :min="6" :max="80" :step="2" style="width: 200px" />
        </div>
      </div>
    </template>

    <el-row :gutter="16">
      <el-col :span="16">
        <div class="gantt">
          <div class="gantt-header">
            <div class="col-equip">设备</div>
            <div class="col-timeline">时间轴（小时）</div>
          </div>
          <div v-for="(rows, equip) in grouped" :key="String(equip)" class="gantt-row">
            <div class="col-equip">{{ equipLabel(equip) }}</div>
            <div class="col-timeline">
              <div class="timeline" :style="{ width: totalWidth + 'px' }">
                <div
                  v-for="t in rows"
                  :key="t.work_order_operation_id"
                  class="bar"
                  :style="barStyle(t)"
                  :title="barTitle(t)"
                >
                  {{ barLabel(t) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <el-card class="panel" header="排程明细">
          <el-table :data="taskTable" size="small" stripe>
            <el-table-column prop="work_order" label="工单" width="140" />
            <el-table-column prop="operation" label="工序" width="140" />
            <el-table-column prop="equipment" label="设备" width="120" />
            <el-table-column prop="start" label="开始时间" width="180" />
            <el-table-column prop="end" label="结束时间" width="180" />
            <el-table-column prop="duration" label="工时(h)" width="90" />
            <el-table-column prop="qty" label="数量" width="80" />
            <el-table-column prop="remaining" label="未完数量" width="90" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="panel" header="设备负荷（小时）">
          <el-table :data="loadList" size="small" stripe>
            <el-table-column prop="equipment" label="设备" width="120" />
            <el-table-column prop="hours" label="负荷" />
          </el-table>
        </el-card>
        <el-card class="panel" header="交期预警">
          <el-table :data="warnings" size="small" stripe>
            <el-table-column prop="code" label="工单" width="140" />
            <el-table-column prop="planned_end_date" label="计划交期" width="180" />
            <el-table-column prop="task_end" label="预计完成" width="180" />
            <el-table-column prop="delay_hours" label="超期(小时)" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { scheduleApi, type ScheduleTask, type ScheduleResult } from '@/api/schedule'

const data = ref<ScheduleResult>({ tasks: [], loads: {}, warnings: [] })
const scale = ref(20) // px / hour，可调节

async function run() {
  data.value = await scheduleApi.run()
}

onMounted(run)

const grouped = computed<Record<string, ScheduleTask[]>>(() => {
  const g: Record<string, ScheduleTask[]> = {}
  data.value.tasks.forEach((t) => {
    const k = String(t.equipment_id)
    g[k] = g[k] || []
    g[k].push(t)
  })
  return g
})

const loadList = computed(() => {
  return Object.entries(data.value.loads).map(([k, v]) => ({
    equipment: equipLabel(k),
    hours: v,
  }))
})

const warnings = computed(() => data.value.warnings)

const taskTable = computed(() => {
  return data.value.tasks
    .slice()
    .sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())
    .map((t) => ({
      work_order: t.work_order_code || `WO#${t.work_order_id}`,
      operation: t.operation_code || t.operation_name || `OP#${t.operation_id}`,
      equipment: equipLabel(t.equipment_id),
      start: t.start,
      end: t.end,
      duration: t.duration_hours ? t.duration_hours.toFixed(2) : '',
      qty: t.planned_quantity,
      remaining: t.remaining_quantity,
    }))
})

function equipLabel(equip: string | number) {
  return equip === -1 || equip === '-1' ? '未分配' : `设备 ${equip}`
}

const baseMs = computed(() => {
  if (data.value.tasks.length === 0) return Date.now()
  const minStart = Math.min(...data.value.tasks.map((t) => new Date(t.start).getTime()))
  return minStart
})

const totalWidth = computed(() => {
  if (data.value.tasks.length === 0) return 800
  const maxEnd = Math.max(...data.value.tasks.map((t) => new Date(t.end).getTime()))
  const hours = Math.max((maxEnd - baseMs.value) / 3600000, 8) // 最少显示 8 小时
  return hours * scale.value
})

const opColors = ['#409EFF', '#E6A23C', '#F56C6C', '#67C23A', '#909399', '#9B59B6', '#1ABC9C']

function colorForTask(t: ScheduleTask) {
  // 已完工任务统一为绿色
  if (t.remaining_quantity === 0) {
    return '#67C23A'
  }
  // 不同工序用不同颜色（按 operation_id 分配）
  const idx = Math.abs(t.operation_id) % opColors.length
  return opColors[idx]
}

function barStyle(t: ScheduleTask) {
  const s = new Date(t.start).getTime()
  const e = new Date(t.end).getTime()
  const h = (e - s) / 3600000
  const pxPerHour = scale.value
  const width = Math.max(h * pxPerHour, 6) // 短任务至少 6px 可见
  const left = Math.max(((s - baseMs.value) / 3600000) * pxPerHour, 0)
  const color = colorForTask(t)
  return {
    left: `${left}px`,
    width: `${width}px`,
    background: color,
  }
}

function barTitle(t: ScheduleTask) {
  const label = barLabel(t)
  const dur = t.duration_hours ? `${t.duration_hours.toFixed(2)}h` : ''
  return `${label}\n${t.start} -> ${t.end}${dur ? ` (${dur})` : ''}`
}

function barLabel(t: ScheduleTask) {
  const wo = t.work_order_code || `WO#${t.work_order_id}`
  const op = t.operation_code || t.operation_name || `OP#${t.operation_id}`
  return `${wo}-${op}`
}
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.gantt {
  border: 1px solid #e5e5e5;
  overflow-x: auto;
}
.gantt-header,
.gantt-row {
  display: grid;
  grid-template-columns: 180px 1fr;
}
.gantt-header {
  background: #f8f8f8;
  border-bottom: 1px solid #eee;
  padding: 6px 8px;
  font-weight: 600;
}
.gantt-row {
  border-bottom: 1px solid #f0f0f0;
  min-height: 38px;
}
.col-equip {
  border-right: 1px solid #eee;
  padding: 8px;
}
.col-timeline {
  position: relative;
  padding: 6px;
}
.timeline {
  position: relative;
  height: 36px;
}
.bar {
  position: absolute;
  height: 24px;
  line-height: 24px;
  color: #fff;
  font-size: 12px;
  border-radius: 4px;
  padding: 0 6px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}
.panel {
  margin-top: 12px;
}
.actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.scale {
  margin-left: 12px;
  font-size: 12px;
  color: #666;
}
</style>

