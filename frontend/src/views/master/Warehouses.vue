<template>
  <el-card>
    <template #header>
      <div class="head">
        <span>仓库管理</span>
        <div>
          <el-input v-model="q" placeholder="编码/名称/类型" style="width:220px;margin-right:8px"/>
          <el-button type="primary" @click="openAdd">新建</el-button>
        </div>
      </div>
    </template>
    <el-table :data="filtered" height="60vh" stripe>
      <el-table-column prop="code" label="编码" width="140"/>
      <el-table-column prop="name" label="名称"/>
      <el-table-column prop="type" label="类型" width="120"/>
      <el-table-column prop="address" label="地址"/>
      <el-table-column prop="manager" label="负责人" width="120"/>
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

    <el-dialog v-model="dlg" :title="form.id? '编辑仓库':'新建仓库'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="编码"><el-input v-model="form.code"/></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="类型"><el-select v-model="form.type"><el-option value="原材料"/><el-option value="半成品"/><el-option value="成品"/><el-option value="在制品"/><el-option value="不良品"/></el-select></el-form-item>
        <el-form-item label="负责人"><el-input v-model="form.manager"/></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address"/></el-form-item>
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
import { ref, computed, onMounted } from 'vue'
import type { Warehouse } from '@/types/master'
import { warehouseApi } from '@/api/masterData'

const list = ref<Warehouse[]>([])
const q = ref('')
const dlg = ref(false)
const form = ref<Partial<Warehouse>>({ active: true })

const filtered = computed(() => q.value ? list.value.filter(x => (x.code + x.name + (x.type||'')).includes(q.value)) : list.value)

async function load() {
  try {
    list.value = await warehouseApi.list()
  } catch (error) {
    console.error('加载仓库失败:', error)
  }
}

function openAdd() {
  form.value = { active: true } as any
  dlg.value = true
}

function edit(row: Warehouse) {
  form.value = { ...row } as any
  dlg.value = true
}

async function remove(id: number) {
  try {
    await warehouseApi.remove(id)
    await load()
  } catch (error) {
    console.error('删除仓库失败:', error)
  }
}

async function save() {
  try {
    const obj = { ...form.value } as Warehouse
    await warehouseApi.upsert(obj)
    dlg.value = false
    await load()
  } catch (error) {
    console.error('保存仓库失败:', error)
  }
}

onMounted(() => { load() })
</script>

<style scoped>
.head{display:flex;align-items:center;justify-content:space-between}
</style>
