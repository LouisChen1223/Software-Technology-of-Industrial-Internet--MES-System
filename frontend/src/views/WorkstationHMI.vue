<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>工位 HMI - 工单 {{ currentWO || '未选择' }}</span>
        <el-select v-model="currentWO" placeholder="选择工单" style="width: 200px" @change="loadOps">
          <el-option v-for="wo in woList" :key="wo.id" :value="wo.code" :label="wo.code" />
        </el-select>
        <el-button @click="toggleScan">{{ scanning ? '停止扫码' : '启动扫码' }}</el-button>
      </div>
    </template>
    <div class="hmi-grid">
      <div class="left">
        <el-form :model="report" label-width="80px" size="small">
          <el-form-item label="工序">
            <el-select v-model="report.op" placeholder="选择工序">
              <el-option v-for="op in ops" :key="op" :value="op" :label="op" />
            </el-select>
          </el-form-item>
          <el-form-item label="数量">
            <el-input-number v-model="report.qty" :min="1" />
          </el-form-item>
          <el-form-item label="动作">
            <el-select v-model="report.action" placeholder="动作">
              <el-option label="开工" value="start" />
              <el-option label="完工" value="complete" />
              <el-option label="报废" value="scrap" />
              <el-option label="暂停" value="pause" />
            </el-select>
          </el-form-item>
          <el-form-item label="条码">
            <el-input v-model="report.barcode" placeholder="支持扫码枪" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submit">报工</el-button>
            <el-button @click="reset">重置</el-button>
          </el-form-item>
        </el-form>
        <el-divider />
        <div v-if="scanning">
          <qr-scanner @detected="onDetected" />
        </div>
      </div>
      <div class="right">
        <el-timeline>
          <el-timeline-item v-for="item in history" :key="item.id" :timestamp="item.time" :type="item.type">
            {{ item.desc }}
          </el-timeline-item>
        </el-timeline>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import QrScanner from '@/components/QrScanner.vue'
import http from '@/api/http'
import { operationApi } from '@/api/masterData'

const woList = ref<any[]>([])
const currentWO = ref<string>('')
const currentWOId = ref<number | null>(null)
const ops = ref<any[]>([])
const scanning = ref(false)

interface HistoryItem { id: number; time: string; type: string; desc: string }
const history = ref<HistoryItem[]>([])
let hid = 1

const report = reactive({ op: '', qty: 1, action: '', barcode: '' })

// 加载工单列表
async function loadWorkOrders() {
  try {
    const resp = await http.get('/work-orders')
    woList.value = resp.data
  } catch (error) {
    console.error('加载工单列表失败:', error)
  }
}

// 加载工单的工序
async function loadOps() {
  if (!currentWOId.value) return
  try {
    const list = await operationApi.list()
    ops.value = list.map((op: any) => `${op.code} - ${op.name}`)
  } catch (error) {
    console.error('加载工序失败:', error)
    ops.value = []
  }
}

// 监听工单选择
watch(currentWO, (newWO) => {
  const wo = woList.value.find(w => w.code === newWO)
  if (wo) {
    currentWOId.value = wo.id
    loadOps()
  } else {
    currentWOId.value = null
    ops.value = []
  }
})

// 提交报工
async function submit() {
  if (!currentWOId.value || !report.op || !report.action) return
  
  try {
    // 根据动作类型调用不同的API
    let apiUrl = ''
    switch (report.action) {
      case 'start':
        apiUrl = `/work-orders/${currentWOId.value}/start`
        break
      case 'complete':
        apiUrl = `/work-orders/${currentWOId.value}/complete`
        break
      case 'scrap':
        // 报废报工
        await http.post('/work-reports', {
          work_order_id: currentWOId.value,
          report_type: 'scrap',
          quantity: report.qty,
          barcode: report.barcode
        })
        break
      default:
        // 普通报工
        await http.post('/work-reports', {
          work_order_id: currentWOId.value,
          report_type: 'production',
          quantity: report.qty,
          barcode: report.barcode
        })
    }
    
    if (apiUrl) {
      await http.post(apiUrl, {
        quantity: report.qty,
        barcode: report.barcode
      })
    }
    
    // 添加到历史记录
    history.value.unshift({
      id: hid++,
      time: new Date().toLocaleTimeString(),
      type: report.action === 'scrap' ? 'danger' : 'primary',
      desc: `${currentWO.value} ${report.op} 动作=${report.action} 数量=${report.qty} 条码=${report.barcode || 'N/A'}`
    })
    
    reset(false)
  } catch (error) {
    console.error('报工失败:', error)
  }
}

function reset(clearWO = true) {
  report.op = ''
  report.qty = 1
  report.action = ''
  report.barcode = ''
  if (clearWO) currentWO.value = ''
}

function toggleScan() { scanning.value = !scanning.value }
function onDetected(code: string) { report.barcode = code; scanning.value = false }

onMounted(async () => {
  await loadWorkOrders()
  
  const params = new URLSearchParams(location.search)
  const wo = params.get('wo')
  if (wo) {
    currentWO.value = wo
  }
})
</script>

<style scoped>
.card-header { display:flex; align-items:center; gap:12px; }
.hmi-grid { display:flex; gap:24px; }
.left { flex: 0 0 360px; }
.right { flex: 1; overflow:auto; max-height:60vh; }
</style>
