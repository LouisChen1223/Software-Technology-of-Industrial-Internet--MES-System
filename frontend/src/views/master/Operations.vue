<template>
  <el-card>
    <template #header>
      <div class="head">
        <span>工序定义</span>
        <el-button type="primary" @click="openAdd">新建</el-button>
      </div>
    </template>
    <el-table :data="list" height="60vh">
      <el-table-column prop="code" label="编码" width="140"/>
      <el-table-column prop="name" label="名称"/>
      <el-table-column prop="stdDurationMin" label="标准工时(分)" width="140"/>
      <el-table-column prop="workshopId" label="车间" width="160">
        <template #default="{ row }">{{ workshopName(row.workshopId) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" :title="form.id? '编辑工序':'新建工序'" width="520px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="编码"><el-input v-model="form.code"/></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="标准工时(分)"><el-input-number v-model="(form as any).stdDurationMin" :min="0"/></el-form-item>
        <el-form-item label="所属车间">
          <el-select v-model="(form as any).workshopId" placeholder="选择车间">
            <el-option v-for="w in workshops" :key="w.id" :label="w.name" :value="String(w.id)" />
          </el-select>
        </el-form-item>
        <el-form-item label="需工装"><el-switch v-model="(form as any).needTooling"/></el-form-item>
        <el-form-item label="质检点"><el-switch v-model="(form as any).qualityCheck"/></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg=false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Operation } from '@/types/master'
import { operationApi } from '@/api/masterData'
import { listWorkshops } from '@/api/workshop'

const workshops = ref<Array<{ id: number; name: string }>>([])

const list = ref<Operation[]>([])
const dlg = ref(false)
const form = ref<Partial<Operation>>({})

async function load() {
  try {
    const [opsResp] = await Promise.all([operationApi.list()])
    list.value = opsResp
  } catch (error) {
    console.error('加载工序失败:', error)
  }
}

async function loadWorkshops() {
  try {
    const resp = await listWorkshops({ active: 1 })
    workshops.value = Array.isArray(resp.data) ? resp.data.map((w: any) => ({ id: w.id, name: w.name })) : []
  } catch (e) {
    console.error('加载车间失败:', e)
  }
}

function openAdd() {
  form.value = {} as any
  dlg.value = true
}

function edit(row: Operation) {
  form.value = { ...row } as any
  dlg.value = true
}

async function remove(id: number) {
  try {
    await operationApi.remove(id)
    await load()
  } catch (error) {
    console.error('删除工序失败:', error)
  }
}

async function save() {
  try {
    const obj = { ...form.value } as Operation
    await operationApi.upsert(obj)
    dlg.value = false
    await load()
  } catch (error) {
    console.error('保存工序失败:', error)
  }
}

function workshopName(id?: string) {
  if (!id) return ''
  const w = workshops.value.find(x => String(x.id) === String(id))
  return w ? w.name : id
}

onMounted(() => { load(); loadWorkshops() })
</script>

<style scoped>
.head{display:flex;align-items:center;justify-content:space-between}
</style>
