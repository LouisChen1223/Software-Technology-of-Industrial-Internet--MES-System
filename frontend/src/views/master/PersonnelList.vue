<template>
  <el-card>
    <template #header>
      <div class="head"><span>人员档案</span><el-button type="primary" @click="openAdd">新建</el-button></div>
    </template>
    <el-table :data="list" height="60vh">
      <el-table-column prop="empNo" label="工号" width="140"/>
      <el-table-column prop="name" label="姓名"/>
      <el-table-column prop="role" label="角色" width="140"/>
      <el-table-column prop="shiftCode" label="班次" width="160">
        <template #default="{ row }">{{ shiftName(row.shiftCode) }}</template>
      </el-table-column>
      <el-table-column prop="active" label="在岗" width="100">
        <template #default="{ row }">{{ row.active ? '是' : '否' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dlg" :title="form.id? '编辑人员': '新建人员'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="工号"><el-input v-model="form.empNo"/></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="角色"><el-select v-model="form.role"><el-option value="operator" label="操作员"/><el-option value="qc" label="质检"/><el-option value="supervisor" label="班组长"/></el-select></el-form-item>
        <el-form-item label="班次">
          <el-select v-model="form.shiftCode" filterable placeholder="请选择班次" style="width:100%">
            <el-option v-for="s in enabledShifts()" :key="s.id" :label="s.code + ' - ' + s.name" :value="s.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="在岗"><el-switch v-model="(form as any).active"/></el-form-item>
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
import type { Person, Shift } from '@/types/master'
import { personApi, shiftApi } from '@/api/masterData'

const list = ref<Person[]>([])
const dlg = ref(false)
const form = ref<Partial<Person>>({ active: true, role: 'operator' })
const shifts = ref<Shift[]>([])
const enabledShifts = () => shifts.value.filter(s => !!s.active)

function shiftName(code?: string) {
  if (!code) return ''
  const s = shifts.value.find(x => x.code === code)
  return s ? s.name : code
}

async function load() {
  try {
    list.value = await personApi.list()
    shifts.value = await shiftApi.list()
  } catch (error) {
    console.error('加载人员失败:', error)
  }
}

function openAdd() {
  const defaultShift = enabledShifts()[0]?.code || ''
  form.value = { active: true, role: 'operator', shiftCode: defaultShift } as any
  dlg.value = true
}

function edit(row: Person) {
  form.value = { ...row } as any
  dlg.value = true
}

async function remove(id: number) {
  try {
    await personApi.remove(id)
    await load()
  } catch (error) {
    console.error('删除人员失败:', error)
  }
}

async function save() {
  try {
    const obj = { ...form.value } as Person
    await personApi.upsert(obj)
    dlg.value = false
    await load()
  } catch (error) {
    console.error('保存人员失败:', error)
  }
}

onMounted(() => { load() })
</script>

<style scoped>
.head{display:flex;align-items:center;justify-content:space-between}
</style>
