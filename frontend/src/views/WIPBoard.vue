<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>WIP 看板</span>
        <el-button size="small" @click="refresh">刷新</el-button>
      </div>
    </template>
    <div ref="chartRef" style="height:400px"></div>
    <el-table :data="rows" size="small" style="margin-top:16px" height="40vh">
      <el-table-column prop="wo" label="工单" width="140"/>
      <el-table-column prop="op" label="工序"/>
      <el-table-column prop="wip" label="在制数量" width="120"/>
      <el-table-column prop="started" label="开工时间" width="160"/>
      <el-table-column prop="status" label="状态" width="120"/>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import http from '@/api/http'

interface WipRow { wo: string; op: string; wip: number; started: string; status: string }
const rows = ref<WipRow[]>([])
const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

async function loadWipData() {
  try {
    // 获取WIP追踪数据
    const resp = await http.get('/wip-tracking')
    const wipData = resp.data
    
    // 转换数据格式用于表格显示
    rows.value = wipData.map((item: any) => ({
      wo: item.work_order?.code || 'N/A',
      op: item.operation?.name || 'N/A',
      wip: item.quantity || 0,
      started: item.created_at ? new Date(item.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : '-',
      status: item.status === 'in-process' ? '执行中' : item.status === 'pending' ? '排队' : '未开始'
    }))
  } catch (error) {
    console.error('加载WIP数据失败:', error)
    // 如果加载失败，显示空数据
    rows.value = []
  }
}

function renderChart() {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  
  if (rows.value.length === 0) {
    chart.setOption({
      title: { text: '暂无数据', left: 'center', top: 'center' }
    })
    return
  }
  
  chart.setOption({
    tooltip: {},
    xAxis: { 
      type: 'category', 
      data: rows.value.map(r => r.wo + '-' + r.op.split(' ')[0]),
      axisLabel: { rotate: 45 }
    },
    yAxis: { type: 'value', name: '在制数量' },
    series: [{ 
      type: 'bar', 
      data: rows.value.map(r => r.wip),
      itemStyle: { color: '#5470c6' }
    }]
  })
}

async function refresh() {
  await loadWipData()
  renderChart()
}

onMounted(refresh)
</script>

<style scoped>
.card-header { display:flex; align-items:center; justify-content:space-between; }
</style>
