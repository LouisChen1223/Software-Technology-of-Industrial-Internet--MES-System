<template>
  <el-card>
    <template #header>
      <div class="head"><span>设备档案</span><el-button type="primary" @click="openAdd">新建</el-button></div>
    </template>
    <el-table :data="list" height="60vh">
      <el-table-column prop="code" label="编码" width="140"/>
      <el-table-column prop="name" label="名称"/>
      <el-table-column prop="type" label="类型" width="120"/>
      <el-table-column prop="workstationCode" label="工位" width="120"/>
      <el-table-column prop="enabled" label="启用" width="100">
        <template #default="{ row }">{{ row.enabled ? '是' : '否' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dlg" :title="form.id? '编辑设备': '新建设备'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="编码"><el-input v-model="form.code"/></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="类型"><el-input v-model="form.type"/></el-form-item>
        <el-form-item label="工位"><el-input v-model="form.workstationCode"/></el-form-item>
        <el-form-item label="启用"><el-switch v-model="(form as any).enabled"/></el-form-item>
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
import type { Equipment } from '@/types/master'
import { equipmentApi } from '@/api/masterData'

const list = ref<Equipment[]>([])
const dlg = ref(false)
const form = ref<Partial<Equipment>>({ enabled: true })

async function load() {
  try {
    list.value = await equipmentApi.list()
  } catch (error) {
    console.error('加载设备失败:', error)
  }
}

function openAdd() {
  form.value = { enabled: true } as any
  dlg.value = true
}

function edit(row: Equipment) {
  form.value = { ...row } as any
  dlg.value = true
}

async function remove(id: number) {
  try {
    await equipmentApi.remove(id)
    await load()
  } catch (error) {
    console.error('删除设备失败:', error)
  }
}

async function save() {
  try {
    const obj = { ...form.value } as Equipment
    await equipmentApi.upsert(obj)
    dlg.value = false
    await load()
  } catch (error) {
    console.error('保存设备失败:', error)
  }
}

onMounted(() => { load() })
</script>

<style scoped>
.head{display:flex;align-items:center;justify-content:space-between}
</style>
