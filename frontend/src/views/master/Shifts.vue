<template>
  <el-card>
    <template #header>
      <div class="head"><span>班次定义</span><el-button type="primary" @click="openAdd">新建</el-button></div>
    </template>
    <el-table :data="list" height="60vh">
      <el-table-column prop="code" label="编码" width="140"/>
      <el-table-column prop="name" label="名称"/>
      <el-table-column prop="start" label="开始" width="100"/>
      <el-table-column prop="end" label="结束" width="100"/>
      <el-table-column prop="active" label="启用" width="80">
        <template #default="{ row }">{{ row.active ? '是' : '否' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dlg" :title="form.id? '编辑班次':'新建班次'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="编码"><el-input v-model="form.code"/></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name"/></el-form-item>
  <el-form-item label="开始"><el-input v-model="form.start" placeholder="08:00"/></el-form-item>
  <el-form-item label="结束"><el-input v-model="form.end" placeholder="16:30"/></el-form-item>
        <el-form-item label="启用"><el-switch v-model="(form as any).active"/></el-form-item>
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
import type { Shift } from '@/types/master'
import { shiftApi } from '@/api/masterData'

const list = ref<Shift[]>([])
const dlg = ref(false)
const form = ref<Partial<Shift>>({ active: true })

async function load() {
  try {
    list.value = await shiftApi.list()
  } catch (error) {
    console.error('加载班次失败:', error)
  }
}

function openAdd() {
  form.value = { active: true } as any
  dlg.value = true
}

function edit(row: Shift) {
  form.value = { ...row } as any
  dlg.value = true
}

async function remove(id: number) {
  try {
    await shiftApi.remove(id)
    await load()
  } catch (error) {
    console.error('删除班次失败:', error)
  }
}

async function save() {
  try {
    const obj = { ...form.value } as Shift
    await shiftApi.upsert(obj)
    dlg.value = false
    await load()
  } catch (error) {
    console.error('保存班次失败:', error)
  }
}

onMounted(() => { load() })
</script>

<style scoped>
.head{display:flex;align-items:center;justify-content:space-between}
</style>
