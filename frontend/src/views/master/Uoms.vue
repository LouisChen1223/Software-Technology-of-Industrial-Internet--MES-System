<template>
  <el-card>
    <template #header>
      <div class="head">
        <span>计量单位</span>
        <div>
          <el-input v-model="q" placeholder="编码/名称" style="width:200px;margin-right:8px"/>
          <el-button type="primary" @click="openAdd">新建</el-button>
        </div>
      </div>
    </template>
    <el-table :data="filtered" height="60vh" stripe>
      <el-table-column prop="code" label="编码" width="140"/>
      <el-table-column prop="name" label="名称"/>
      <el-table-column prop="precision" label="精度" width="100"/>
      <el-table-column prop="active" label="启用" width="100">
        <template #default="{ row }">{{ row.active ? '是':'否' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" :title="form.id? '编辑单位':'新建单位'" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="编码"><el-input v-model="form.code"/></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="精度"><el-input-number v-model="(form as any).precision" :min="0" :max="6"/></el-form-item>
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
import type { Uom } from '@/types/master'
import { uomApi } from '@/api/masterData'

const list = ref<Uom[]>([])
const q = ref('')
const dlg = ref(false)
const form = ref<Partial<Uom>>({ active: true, precision: 0 })

const filtered = computed(() => q.value ? list.value.filter(x => (x.code + (x.name||'')).includes(q.value)) : list.value)

async function load() {
  try {
    list.value = await uomApi.list()
  } catch (error) {
    console.error('加载单位失败:', error)
  }
}

function openAdd() {
  form.value = { active: true, precision: 0 } as any
  dlg.value = true
}

function edit(row: Uom) {
  form.value = { ...row } as any
  dlg.value = true
}

async function remove(id: number) {
  try {
    await uomApi.remove(id)
    await load()
  } catch (error) {
    console.error('删除单位失败:', error)
  }
}

async function save() {
  try {
    const obj = { ...form.value } as Uom
    await uomApi.upsert(obj)
    dlg.value = false
    await load()
  } catch (error) {
    console.error('保存单位失败:', error)
  }
}

onMounted(() => { load() })
</script>

<style scoped>
.head{display:flex;align-items:center;justify-content:space-between}
</style>
