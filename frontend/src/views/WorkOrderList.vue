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
      <el-table-column prop="productCode" label="产品"/>
      <el-table-column prop="qty" label="数量" width="100"/>
      <el-table-column prop="dueDate" label="交期" width="160"/>
      <el-table-column prop="status" label="状态" width="120"/>
      <el-table-column label="操作" width="320">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          <el-button size="small" @click="goHMI(row)">到HMI执行</el-button>
          <el-button size="small" type="success" @click="viewWIP(row)">查看WIP</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" :title="form.id? '编辑工单':'新建工单'" width="600px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="工单号"><el-input v-model="form.code"/></el-form-item>
        <el-form-item label="产品ID"><el-input-number v-model="(form as any).product_id" :min="1" style="width:100%"/></el-form-item>
        <el-form-item label="数量"><el-input-number v-model="(form as any).planned_quantity" :min="0" style="width:100%"/></el-form-item>
        <el-form-item label="优先级"><el-input-number v-model="(form as any).priority" :min="1" :max="10" style="width:100%"/></el-form-item>
        <el-form-item label="计划开工"><el-date-picker v-model="(form as any).planned_start_date" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%"/></el-form-item>
        <el-form-item label="计划完工"><el-date-picker v-model="(form as any).planned_end_date" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%"/></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option value="draft" label="草稿"/>
            <el-option value="released" label="已下达"/>
            <el-option value="in-progress" label="执行中"/>
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

const list = ref<WorkOrder[]>([])
const q = ref('')
const router = useRouter()
const dlg = ref(false)
const form = ref<Partial<WorkOrder>>({ status: 'draft', product_id: 1, planned_quantity: 1, priority: 5 })

const filtered = computed(() => {
  if (!q.value) return list.value
  return list.value.filter(x => [x.woNo, x.productCode, x.status, x.dueDate].join('|').includes(q.value))
})

function reset() {
  q.value = ''
}

async function load() {
  try {
    list.value = await workorderApi.list()
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

onMounted(() => { load() })
</script>

<style scoped>
.card-header { display: flex; align-items: center; justify-content: space-between; }
</style>
