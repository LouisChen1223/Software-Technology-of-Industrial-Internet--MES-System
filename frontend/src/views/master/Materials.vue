<template>
  <el-card>
    <template #header>
      <div class="head">
        <span>物料主数据</span>
        <div>
          <el-input v-model="q" placeholder="编码/名称/规格" style="width:240px;margin-right:8px"/>
          <el-button type="primary" @click="openAdd">新建</el-button>
        </div>
      </div>
    </template>
    <el-table :data="filtered" height="60vh" stripe>
      <el-table-column prop="code" label="编码" width="140"/>
      <el-table-column prop="name" label="名称"/>
      <el-table-column prop="spec" label="规格"/>
      <el-table-column prop="uom" label="单位" width="80"/>
      <el-table-column prop="type" label="类型" width="120"/>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" :title="form.id ? '编辑物料' : '新建物料'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="编码"><el-input v-model="form.code"/></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="规格"><el-input v-model="form.spec"/></el-form-item>
        <el-form-item label="单位"><el-input v-model="form.uom"/></el-form-item>
        <el-form-item label="类型"><el-select v-model="form.type"><el-option value="原材料"/><el-option value="半成品"/><el-option value="成品"/><el-option value="耗材"/></el-select></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.active"/></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg=false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import type { Material } from '@/types/master'
import { materialApi } from '@/api/masterData'

const list = ref<Material[]>([])
const q = ref('')
const dlg = ref(false)
const form = reactive<Partial<Material>>({ active: true, uom: 'PCS' })

const filtered = computed(() => q.value ? list.value.filter(x => (x.code + x.name + (x.spec||'')).includes(q.value)) : list.value)

async function load() {
  try {
    list.value = await materialApi.list()
  } catch (error) {
    console.error('加载物料失败:', error)
  }
}

function openAdd() {
  Object.assign(form, { id: undefined, code:'', name:'', spec:'', uom:'PCS', type:'原材料', active:true })
  dlg.value = true
}

function edit(row: Material) {
  Object.assign(form, row)
  dlg.value = true
}

async function remove(row: Material) {
  try {
    await materialApi.remove(row.id)
    await load()
  } catch (error) {
    console.error('删除物料失败:', error)
  }
}

async function save() {
  try {
    if (form.id) {
      await materialApi.update(form.id, form as any)
    } else {
      await materialApi.create(form as any)
    }
    dlg.value = false
    await load()
  } catch (error) {
    console.error('保存物料失败:', error)
  }
}

onMounted(() => { load() })
</script>

<style scoped>
.head{display:flex;align-items:center;justify-content:space-between}
</style>
