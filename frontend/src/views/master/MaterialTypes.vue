<template>
  <el-card>
    <template #header>
      <div class="head">
        <span>物料类型</span>
        <div>
          <el-input v-model="q" placeholder="编码/名称" style="width:200px;margin-right:8px" />
          <el-button type="primary" @click="openAdd">新建</el-button>
        </div>
      </div>
    </template>
    <el-table :data="filtered" height="60vh" stripe>
      <el-table-column prop="code" label="编码" width="140" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="active" label="启用" width="100">
        <template #default="{ row }">{{ row.active ? '是' : '否' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" :title="form.id ? '编辑物料类型' : '新建物料类型'" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="编码"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
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
import type { MaterialType } from '@/types/master'
import { materialTypeApi } from '@/api/masterData'

const list = ref<MaterialType[]>([])
const q = ref('')
const dlg = ref(false)
const form = ref<Partial<MaterialType>>({ active: true })

const filtered = computed(() =>
  q.value ? list.value.filter(x => (x.code + (x.name || '')).includes(q.value)) : list.value
)

async function load() {
  try {
    list.value = await materialTypeApi.list()
  } catch (error) {
    console.error('加载物料类型失败:', error)
  }
}

function openAdd() {
  form.value = { active: true } as any
  dlg.value = true
}

function edit(row: MaterialType) {
  form.value = { ...row, active: !!row.active } as any
  dlg.value = true
}

async function remove(id: string) {
  try {
    await materialTypeApi.remove(id)
    await load()
  } catch (error) {
    console.error('删除物料类型失败:', error)
  }
}

async function save() {
  try {
    const payload = { ...(form.value as any) } as MaterialType
    await materialTypeApi.upsert(payload)
    dlg.value = false
    await load()
  } catch (error) {
    console.error('保存物料类型失败:', error)
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>

