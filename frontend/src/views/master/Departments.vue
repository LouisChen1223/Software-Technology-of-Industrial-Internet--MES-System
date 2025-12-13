<template>
  <el-card>
    <template #header>
      <div class="head">
        <span>部门</span>
        <div>
          <el-input v-model="q" placeholder="编码/名称" style="width:200px;margin-right:8px" />
          <el-button type="primary" @click="openAdd">新建</el-button>
        </div>
      </div>
    </template>
    <el-table :data="filtered" height="60vh" stripe>
      <el-table-column prop="code" label="编码" width="140" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="manager" label="负责人" width="140" />
      <el-table-column prop="active" label="启用" width="100">
        <template #default="{ row }">{{ row.active ? '是' : '否' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" :title="form.id ? '编辑部门' : '新建部门'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="编码"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="负责人"><el-input v-model="form.manager" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="(form as any).active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Department } from '@/types/department'
import { listDepartments, createDepartment, updateDepartment, deleteDepartment } from '@/api/department'

const list = ref<Department[]>([])
const q = ref('')
const dlg = ref(false)
const form = ref<Partial<Department>>({ active: 1 })

const filtered = computed(() =>
  q.value ? list.value.filter(x => (x.code + (x.name || '')).includes(q.value)) : list.value
)

async function load() {
  const { data } = await listDepartments()
  list.value = data
}

function openAdd() {
  form.value = { active: 1 } as any
  dlg.value = true
}

function edit(row: Department) {
  form.value = { ...row, active: row.active ? 1 : 0 } as any
  dlg.value = true
}

async function remove(id: number) {
  await deleteDepartment(id)
  await load()
}

async function save() {
  const payload = { ...(form.value as any) }
  if (payload.id) {
    await updateDepartment(payload.id, {
      code: payload.code,
      name: payload.name,
      manager: payload.manager,
      description: payload.description,
      active: payload.active
    })
  } else {
    await createDepartment({
      code: payload.code,
      name: payload.name,
      manager: payload.manager,
      description: payload.description,
      active: payload.active ?? 1
    })
  }
  dlg.value = false
  await load()
}

onMounted(load)
</script>

<style scoped>
.head { display: flex; align-items: center; justify-content: space-between; }
</style>
