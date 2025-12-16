<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>工单管理</span>
        <div>
          <el-input v-model="q" placeholder="搜索工单/产品/状态" style="width: 240px; margin-right: 8px"/>
          <el-button @click="reset" style="margin-right:8px">重置</el-button>
          <el-button type="primary" @click="openAdd">新建</el-button>
        </div>
      </div>
    </template>
    <el-table :data="filtered" height="60vh" stripe>
      <el-table-column prop="woNo" label="工单号" width="140"/>
      <el-table-column prop="productName" label="产品"/>
      <el-table-column prop="qty" label="数量" width="100"/>
      <el-table-column prop="dueDate" label="交期" width="160"/>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          {{ statusLabel(row.status) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="480">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          <el-button size="small" @click="goHMI(row)">到HMI执行</el-button>
          <el-button size="small" type="success" @click="viewWIP(row)">查看WIP</el-button>
          <el-button size="small" type="primary" :disabled="row.status!=='draft'" @click="release(row)">下达</el-button>
          <el-button size="small" type="warning" :disabled="row.status!=='released'" @click="start(row)">开始</el-button>
          <el-button size="small" type="success" :disabled="row.status!=='in_progress'" @click="complete(row)">完工</el-button>
          <el-button size="small" type="danger" :disabled="row.status==='completed'" @click="cancel(row)">取消</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" :title="form.id? '编辑工单':'新建工单'" width="600px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="工单号">
          <el-input v-model="form.code" placeholder="保存后自动生成" disabled/>
        </el-form-item>
        <el-form-item label="产品">
          <el-select v-model="(form as any).product_id" placeholder="选择产品" style="width:100%">
            <el-option v-for="m in materials" :key="m.id" :label="m.name" :value="Number(m.id)" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量"><el-input-number v-model="(form as any).planned_quantity" :min="0" style="width:100%"/></el-form-item>
        <el-form-item label="优先级"><el-input-number v-model="(form as any).priority" :min="1" :max="10" style="width:100%"/></el-form-item>
        <el-form-item label="计划开工"><el-date-picker v-model="(form as any).planned_start_date" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%"/></el-form-item>
        <el-form-item label="计划完工"><el-date-picker v-model="(form as any).planned_end_date" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%"/></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option value="draft" label="草稿"/>
            <el-option value="released" label="已下达"/>
            <el-option value="in_progress" label="执行中"/>
            <el-option value="completed" label="已完工"/>
            <el-option value="cancelled" label="已取消"/>
          </el-select>
        </el-form-item>
        <el-form-item label="客户"><el-input v-model="form.customer"/></el-form-item>
        <el-form-item label="备注"><el-input type="textarea" v-model="form.notes"/></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg=false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { WorkOrder } from '@/types/order'
import { workorderApi } from '@/api/workorder'
import { materialApi } from '@/api/masterData'

const list = ref<WorkOrder[]>([])
const materials = ref<{ id: string; name: string }[]>([])
const q = ref('')
const router = useRouter()
const dlg = ref(false)
const form = ref<Partial<WorkOrder>>({ status: 'draft', product_id: 1, planned_quantity: 1, priority: 5 })

const filtered = computed(() => {
  if (!q.value) return list.value
  return list.value.filter(x => [x.woNo, x.productCode, statusLabel(x.status), x.dueDate].join('|').includes(q.value))
})

function reset() {
  q.value = ''
}
function statusLabel(s?: WorkOrder['status']): string {
  const map: Record<string, string> = {
    draft: '草稿',
    released: '已下达',
    in_progress: '执行中',
    paused: '暂停',
    completed: '已完工',
    cancelled: '已取消'
  }
  return s ? (map[s] || s) : ''
}

async function load() {
  try {
    list.value = await workorderApi.list()
    const mats = await materialApi.list()
    // 仅允许选择物料类型为“成品”的作为工单产品
    const finished = mats.filter(m => (m.type || '').trim() === '成品')
    materials.value = finished.map(m => ({ id: m.id, name: `${m.code} - ${m.name}` }))
    // 映射产品名称到工单列表显示
    const map = new Map(materials.value.map(m => [m.id, m.name]))
    list.value = list.value.map(x => ({
      ...x,
      productName: map.get(String(x.product_id)) || String(x.product_id)
    }))
  } catch (error) {
    console.error('加载工单失败:', error)
  }
}

function openAdd() {
  form.value = { status: 'draft', product_id: 1, planned_quantity: 1, priority: 5 } as any
  dlg.value = true
}

function edit(row: WorkOrder) {
  form.value = { ...row } as any
  dlg.value = true
}

async function remove(id: string) {
  try {
    await workorderApi.remove(id)
    await load()
  } catch (error) {
    console.error('删除工单失败:', error)
  }
}

async function save() {
  try {
    const obj = { ...form.value } as WorkOrder
    // 将日期分钟秒归零到整点，前端提交更干净（后端亦有校验）
    const normalize = (s?: string) => {
      if (!s) return s
      const d = new Date(s)
      d.setMinutes(0, 0, 0)
      return d.toISOString()
    }
    obj.planned_start_date = normalize(obj.planned_start_date)
    obj.planned_end_date = normalize(obj.planned_end_date)
    await workorderApi.upsert(obj)
    dlg.value = false
    await load()
  } catch (error) {
    console.error('保存工单失败:', error)
  }
}

function goHMI(row: WorkOrder) {
  router.push({ path: '/hmi', query: { wo: row.woNo } })
}

function viewWIP(row: WorkOrder) {
  router.push({ path: '/wip', query: { wo: row.woNo } })
}

async function release(row: WorkOrder) {
  try {
    await workorderApi.release(String(row.id))
    await load()
  } catch (error) {
    console.error('下达工单失败:', error)
  }
}

async function start(row: WorkOrder) {
  try {
    await workorderApi.start(String(row.id))
    await load()
  } catch (error) {
    console.error('开始工单失败:', error)
  }
}

async function complete(row: WorkOrder) {
  try {
    await workorderApi.complete(String(row.id))
    await load()
  } catch (error) {
    console.error('完工工单失败:', error)
  }
}

async function cancel(row: WorkOrder) {
  try {
    await workorderApi.cancel(String(row.id))
    await load()
  } catch (error) {
    console.error('取消工单失败:', error)
  }
}

onMounted(() => { load() })
</script>

<style scoped>
.card-header { display: flex; align-items: center; justify-content: space-between; }
</style>
