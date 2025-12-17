<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>WIP 看板</span>
        <div>
          <el-select
            v-model="statusFilter"
            size="small"
            style="width: 140px; margin-right: 8px"
          >
            <el-option label="全部状态" value="all" />
            <el-option label="在制" value="在制" />
            <el-option label="执行中" value="执行中" />
            <el-option label="排队" value="排队" />
          </el-select>
          <el-button size="small" @click="refresh">刷新</el-button>
        </div>
      </div>
    </template>

    <div ref="chartRef" style="height: 400px"></div>

    <el-divider />

    <div class="trace-tools">
      <el-select
        v-model="batch"
        filterable
        clearable
        placeholder="批次号（正向追溯）"
        style="width: 240px; margin-right: 8px"
      >
        <el-option
          v-for="b in batchOptions"
          :key="b"
          :label="b"
          :value="b"
        />
      </el-select>
      <el-button size="small" @click="doTraceBatch">追溯批次 → 成品</el-button>

      <el-select
        v-model="serial"
        filterable
        clearable
        placeholder="序列号（正向/逆向）"
        style="width: 240px; margin: 0 8px"
      >
        <el-option
          v-for="s in serialOptions"
          :key="s"
          :label="s"
          :value="s"
        />
      </el-select>
      <el-button size="small" @click="doTraceSerial">追溯序列</el-button>

      <el-button size="small" type="primary" @click="clearTrace">清空追溯结果</el-button>
    </div>

    <el-table :data="traceRows" size="small" style="margin-top: 8px" height="30vh">
      <el-table-column prop="wo" label="工单" width="140" />
      <el-table-column prop="op" label="工序" />
      <el-table-column prop="material" label="物料" />
      <el-table-column prop="batch" label="批次" />
      <el-table-column prop="serial" label="序列" />
      <el-table-column prop="qty" label="数量" width="100" />
      <el-table-column prop="status" label="状态" width="120" />
    </el-table>

    <el-table :data="filteredRows" size="small" style="margin-top: 16px" height="40vh">
      <el-table-column prop="wo" label="工单" width="140" />
      <el-table-column prop="op" label="工序" />
      <el-table-column prop="wip" label="在制数量" width="120" />
      <el-table-column prop="started" label="开始时间" width="160" />
      <el-table-column prop="status" label="状态" width="120" />
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import * as echarts from 'echarts'
import http from '@/api/http'
import { wipApi } from '@/api/wip'

interface WipRow {
  wo: string
  op: string
  wip: number
  started: string
  status: string
}

const rows = ref<WipRow[]>([])
const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

const batch = ref('')
const serial = ref('')
const traceRows = ref<any[]>([])
const batchOptions = ref<string[]>([])
const serialOptions = ref<string[]>([])
const statusFilter = ref<'all' | '在制' | '执行中' | '排队'>('all')

const filteredRows = computed<WipRow[]>(() => {
  if (statusFilter.value === 'all') {
    return rows.value
  }
  return rows.value.filter((r) => r.status === statusFilter.value)
})

function mapStatus(raw: string | null | undefined): string {
  if (!raw) return '-'
  if (raw === 'in-process') return '执行中'
  if (raw === 'pending') return '排队'
  if (raw === 'wip') return '在制'
  return raw
}

async function loadWipData() {
  try {
    // 获取 WIP 在制数据
    const resp = await http.get('/wip-tracking')
    const wipData = resp.data as any[]

    const batchSet = new Set<string>()
    const serialSet = new Set<string>()

    // 转成表格数据 + 批次/序列下拉选项
    rows.value = wipData.map((item) => {
      if (item.batch_number) batchSet.add(item.batch_number)
      if (item.serial_number) serialSet.add(item.serial_number)

      return {
        wo: item.work_order?.code || 'N/A',
        op: item.operation?.name || 'N/A',
        wip: item.quantity || 0,
        started: item.created_at
          ? new Date(item.created_at).toLocaleTimeString('zh-CN', {
              hour: '2-digit',
              minute: '2-digit',
            })
          : '-',
        status: mapStatus(item.status),
      }
    })

    batchOptions.value = Array.from(batchSet)
    serialOptions.value = Array.from(serialSet)
  } catch (error) {
    console.error('加载 WIP 数据失败:', error)
    rows.value = []
    batchOptions.value = []
    serialOptions.value = []
  }
}

function renderChart() {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const data = filteredRows.value

  if (data.length === 0) {
    chart.setOption({
      title: { text: '暂无数据', left: 'center', top: 'center' },
      xAxis: { show: false },
      yAxis: { show: false },
      series: [],
    })
    return
  }

  chart.setOption({
    tooltip: {},
    xAxis: {
      type: 'category',
      data: data.map((r) => r.wo + '-' + r.op.split(' ')[0]),
      axisLabel: {
        rotate: 0,
      },
    },
    yAxis: { type: 'value', name: '在制数量' },
    series: [
      {
        type: 'bar',
        data: data.map((r) => r.wip),
        itemStyle: { color: '#5470c6' },
      },
    ],
  })
}

async function refresh() {
  await loadWipData()
  renderChart()
}

async function doTraceBatch() {
  if (!batch.value) return
  const list = await wipApi.traceByBatch(batch.value)
  traceRows.value = list.map((item) => ({
    wo: item.work_order?.code || item.work_order_id,
    op: item.operation?.name || item.operation_id,
    material: item.material_id,
    batch: item.batch_number || '-',
    serial: item.serial_number || '-',
    qty: item.quantity,
    status: mapStatus(item.status),
  }))
}

async function doTraceSerial() {
  if (!serial.value) return
  const list = await wipApi.traceBySerial(serial.value)
  traceRows.value = list.map((item) => ({
    wo: item.work_order?.code || item.work_order_id,
    op: item.operation?.name || item.operation_id,
    material: item.material_id,
    batch: item.batch_number || '-',
    serial: item.serial_number || '-',
    qty: item.quantity,
    status: mapStatus(item.status),
  }))
}

function clearTrace() {
  traceRows.value = []
  batch.value = ''
  serial.value = ''
}

onMounted(refresh)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.trace-tools {
  display: flex;
  align-items: center;
}
</style>

