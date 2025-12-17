<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>工位 HMI - 工单 {{ currentWO || '未选择' }}</span>
        <el-select v-model="currentWO" placeholder="选择工单" style="width: 220px">
          <el-option
            v-for="wo in woList"
            :key="wo.id"
            :value="wo.code"
            :label="wo.code"
          />
        </el-select>
        <el-button @click="toggleScan">
          {{ scanning ? '停止扫码' : '启动扫码' }}
        </el-button>
      </div>
    </template>

    <div class="hmi-grid">
      <div class="left">
        <el-form :model="report" label-width="80px" size="small">
          <el-form-item label="工序">
            <el-select v-model="report.operationId" placeholder="选择工单工序">
              <el-option
                v-for="op in ops"
                :key="op.id"
                :value="op.id"
                :label="opLabel(op)"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="数量">
            <el-input-number v-model="report.quantity" :min="1" />
          </el-form-item>
          <el-form-item label="动作">
            <el-select v-model="report.report_type" placeholder="选择动作">
              <el-option label="开工" value="start" />
              <el-option label="完工" value="complete" />
              <el-option label="报废" value="scrap" />
              <el-option label="暂停" value="pause" />
              <el-option label="恢复" value="resume" />
            </el-select>
          </el-form-item>
          <el-form-item label="条码">
            <el-input v-model="report.barcode" placeholder="支持扫码枪输入" />
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
        <el-card v-if="currentWODetail" shadow="never" class="right-section">
          <template #header>
            <span>当前工单进度</span>
          </template>
          <el-descriptions :column="2" size="small" class="wo-summary">
            <el-descriptions-item label="工单号">
              {{ currentWODetail.code }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              {{ currentWODetail.status }}
            </el-descriptions-item>
            <el-descriptions-item label="计划数量">
              {{ currentWODetail.planned_quantity }}
            </el-descriptions-item>
            <el-descriptions-item label="已完工 / 报废">
              {{ currentWODetail.completed_quantity }} / {{ currentWODetail.scrapped_quantity }}
            </el-descriptions-item>
          </el-descriptions>

          <el-table :data="ops" size="small" border>
            <el-table-column prop="sequence" label="序号" width="70" />
            <el-table-column label="工序" min-width="160">
              <template #default="{ row }">
                {{ opLabel(row) }}
              </template>
            </el-table-column>
            <el-table-column prop="planned_quantity" label="计划数" width="90" />
            <el-table-column prop="completed_quantity" label="完工数" width="90" />
            <el-table-column prop="scrapped_quantity" label="报废数" width="90" />
            <el-table-column prop="status" label="状态" width="90" />
          </el-table>
        </el-card>

        <el-card shadow="never" class="right-section">
          <template #header>
            <span>报工历史</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="item in history"
              :key="item.id"
              :timestamp="item.time"
              :type="item.type"
            >
              {{ item.desc }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import QrScanner from '@/components/QrScanner.vue'
import http from '@/api/http'
import { operationApi } from '@/api/masterData'
import { reportApi, type WorkReport } from '@/api/report'

const woList = ref<any[]>([])
const currentWO = ref<string>('')
const currentWOId = ref<number | null>(null)
const currentWODetail = ref<any | null>(null)
const ops = ref<any[]>([])
const allOps = ref<any[]>([])
const scanning = ref(false)

interface HistoryItem {
  id: number
  time: string
  type: string
  desc: string
}
const history = ref<HistoryItem[]>([])
let hid = 1

const report = reactive<{
  operationId?: number
  quantity: number
  report_type?: string
  barcode?: string
}>({
  quantity: 1,
})

// 加载工单列表
async function loadWorkOrders() {
  try {
    const resp = await http.get('/work-orders')
    woList.value = resp.data
  } catch (error) {
    console.error('加载工单列表失败:', error)
  }
}

// 加载当前工单的工序（工单工序）并刷新进度
async function loadOpsForCurrentWO() {
  if (!currentWOId.value) {
    ops.value = []
    currentWODetail.value = null
    return
  }
  try {
    if (!allOps.value.length) {
      allOps.value = await operationApi.list()
    }
    const opMap = new Map<number, any>()
    allOps.value.forEach((o: any) => {
      const idNum = Number(o.id)
      if (!Number.isNaN(idNum)) {
        opMap.set(idNum, o)
      }
    })

    const resp = await http.get(`/work-orders/${currentWOId.value}`)
    const wo = resp.data
    currentWODetail.value = wo
    const workOps = wo.operations || []

    ops.value = workOps.map((wop: any) => {
      const base = opMap.get(wop.operation_id)
      return {
        id: wop.id, // WorkOrderOperation ID
        sequence: wop.sequence,
        operation_id: wop.operation_id,
        code: base?.code || `OP${wop.operation_id}`,
        name: base?.name || '',
        planned_quantity: wop.planned_quantity,
        completed_quantity: wop.completed_quantity,
        scrapped_quantity: wop.scrapped_quantity,
        status: wop.status,
      }
    })
  } catch (error) {
    console.error('加载工单工序失败:', error)
    ops.value = []
    currentWODetail.value = null
  }
}

function opLabel(op: any) {
  const parts: string[] = []
  if (op.sequence != null) parts.push(`#${op.sequence}`)
  if (op.code) parts.push(op.code)
  if (op.name) parts.push(op.name)
  return parts.join(' ')
}

// 监听工单选择
watch(currentWO, (newWO) => {
  const wo = woList.value.find((w) => w.code === newWO)
  if (wo) {
    currentWOId.value = wo.id
    loadOpsForCurrentWO()
  } else {
    currentWOId.value = null
    ops.value = []
    currentWODetail.value = null
  }
})

// 提交报工
async function submit() {
  if (!currentWOId.value) {
    ElMessage.warning('请先选择工单')
    return
  }
  if (!report.operationId) {
    ElMessage.warning('请选择工单工序')
    return
  }
  if (!report.report_type) {
    ElMessage.warning('请选择报工动作')
    return
  }

  // 前端预校验：当前工序完工数量不能超过计划数量
  const qty = report.quantity || 0
  if (report.report_type === 'complete') {
    const op = ops.value.find((o) => o.id === report.operationId)
    if (op) {
      const opPlanned = op.planned_quantity || 0
      const opCompleted = op.completed_quantity || 0
      if (opCompleted + qty > opPlanned) {
        ElMessage.warning('当前工序完工数量不能超过计划数量')
        return
      }
    }
  }

  try {
    const payload: WorkReport = {
      work_order_id: currentWOId.value,
      work_order_operation_id: report.operationId,
      report_type: report.report_type as any,
      quantity: report.quantity,
      barcode: report.barcode,
    }
    await reportApi.create(payload)

    // 刷新当前工单进度和工序状态
    await loadOpsForCurrentWO()

    // 添加到历史记录
    history.value.unshift({
      id: hid++,
      time: new Date().toLocaleTimeString(),
      type: report.report_type === 'scrap' ? 'danger' : 'primary',
      desc: `${currentWO.value} 工序=${report.operationId} 动作=${report.report_type} 数量=${report.quantity} 条码=${report.barcode || 'N/A'}`,
    })

    ElMessage.success('报工成功')
    reset(false)
  } catch (error) {
    console.error('报工失败:', error)
  }
}

function reset(clearWO = true) {
  report.operationId = undefined
  report.quantity = 1
  report.report_type = undefined
  report.barcode = ''
  if (clearWO) {
    currentWO.value = ''
  }
}

function toggleScan() {
  scanning.value = !scanning.value
}

function onDetected(code: string) {
  report.barcode = code
  scanning.value = false
}

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
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.hmi-grid {
  display: flex;
  gap: 24px;
}
.left {
  flex: 0 0 360px;
}
.right {
  flex: 1;
  overflow: auto;
  max-height: 60vh;
}
.right-section {
  margin-bottom: 16px;
}
.wo-summary {
  margin-bottom: 8px;
}
</style>
