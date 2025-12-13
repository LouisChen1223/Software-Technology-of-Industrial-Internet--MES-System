<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>排程甘特图 / 负荷分析 / 交期预警</span>
        <div>
          <el-button type="primary" @click="run">重新排程</el-button>
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
              <div v-for="t in rows" :key="t.work_order_operation_id" class="bar"
                   :style="barStyle(t)"
                   :title="barTitle(t)">
                {{ t.work_order_id }}-{{ t.sequence }}
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <el-card class="panel" header="设备负荷（小时）">
          <el-table :data="loadList" size="small" :stripe="true">
            <el-table-column prop="equipment" label="设备" width="120"/>
            <el-table-column prop="hours" label="负荷"/>
          </el-table>
        </el-card>
        <el-card class="panel" header="交期预警">
          <el-table :data="warnings" size="small" :stripe="true">
            <el-table-column prop="code" label="工单" width="140"/>
            <el-table-column prop="planned_end_date" label="计划交期" width="180"/>
            <el-table-column prop="task_end" label="预计完成" width="180"/>
            <el-table-column prop="delay_hours" label="超期(小时)"/>
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

async function run() {
  data.value = await scheduleApi.run()
}

onMounted(run)

const grouped = computed<Record<string, ScheduleTask[]>>(() => {
  const g: Record<string, ScheduleTask[]> = {}
  data.value.tasks.forEach(t => {
    const k = String(t.equipment_id)
    g[k] = g[k] || []
    g[k].push(t)
  })
  return g
})

const loadList = computed(() => {
  return Object.entries(data.value.loads).map(([k, v]) => ({ equipment: equipLabel(k), hours: v }))
})

function equipLabel(equip: string | number) { return equip === -1 || equip === "-1" ? "未分配" : `设备 ${equip}` }

function barStyle(t: ScheduleTask) {
  const s = new Date(t.start).getTime()
  const e = new Date(t.end).getTime()
  const h = (e - s) / 3600000
  // 简易比例：1小时 = 20px
  const width = h * 20
  const left = ((s - baseMs.value) / 3600000) * 20
  const color = t.remaining_quantity === 0 ? '#67C23A' : '#409EFF'
  return {
    left: `${left}px`,
    width: `${width}px`,
    background: color
  }
}

function barTitle(t: ScheduleTask) {
  return `WO:${t.work_order_id} Seq:${t.sequence}\n${t.start} -> ${t.end}`
}

const baseMs = computed(() => {
  if (data.value.tasks.length === 0) return Date.now()
  const minStart = Math.min(...data.value.tasks.map(t => new Date(t.start).getTime()))
  return minStart
})
</script>

<style scoped>
.card-header { display:flex; align-items:center; justify-content:space-between; }
.gantt { border: 1px solid #e5e5e5; }
.gantt-header, .gantt-row { display: grid; grid-template-columns: 180px 1fr; }
.gantt-header { background: #f8f8f8; border-bottom: 1px solid #eee; padding: 6px 8px; font-weight: 600; }
.gantt-row { border-bottom: 1px solid #f0f0f0; min-height: 38px; }
.col-equip { border-right: 1px solid #eee; padding: 8px; }
.col-timeline { position: relative; padding: 6px; }
.bar { position: absolute; height: 24px; line-height: 24px; color: #fff; font-size: 12px; border-radius: 4px; padding: 0 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
.panel { margin-top: 12px; }
</style>