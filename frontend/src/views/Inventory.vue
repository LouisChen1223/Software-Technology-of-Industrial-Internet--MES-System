<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>库存 / 出入库</span>
        <div>
          <el-input v-model="q" placeholder="物料/批次/库位" style="width:220px;margin-right:8px"/>
          <el-upload :auto-upload="false" accept=".xlsx,.xls" :on-change="onImport">
            <el-button>导入Excel</el-button>
          </el-upload>
          <el-button @click="onExport">导出</el-button>
        </div>
      </div>
    </template>
    <div class="toolbar">
      <el-button type="primary" @click="issue">领料</el-button>
      <el-button @click="supplement">补料</el-button>
      <el-button type="warning" @click="returnBack">退料</el-button>
    </div>
    <el-table :data="filtered" height="60vh" stripe>
      <el-table-column prop="material" label="物料"/>
      <el-table-column prop="lot" label="批次"/>
      <el-table-column prop="loc" label="库位" width="120"/>
      <el-table-column prop="qty" label="数量" width="100"/>
      <el-table-column prop="uom" label="单位" width="80"/>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import * as XLSX from 'xlsx'

interface Inv { material: string; lot: string; loc: string; qty: number; uom: string }
const list = ref<Inv[]>([])
const q = ref('')

const filtered = computed(() => {
  if (!q.value) return list.value
  return list.value.filter(r => (r.material + r.lot + r.loc).includes(q.value))
})

function loadData() {
  list.value = [
    { material: 'MAT-001', lot: 'L20251112A', loc: 'A01-01', qty: 120, uom: 'PCS' },
    { material: 'MAT-002', lot: 'L20251112B', loc: 'A01-02', qty: 80, uom: 'PCS' },
    { material: 'MAT-003', lot: 'L20251101A', loc: 'B02-01', qty: 200, uom: 'PCS' }
  ]
}

function issue() { console.info('issue selected rows or open dialog') }
function supplement() { console.info('supplement materials') }
function returnBack() { console.info('return materials') }

function onImport(file: any) {
  const reader = new FileReader()
  reader.onload = () => {
    const workbook = XLSX.read(reader.result as ArrayBuffer, { type: 'array' })
    const ws = workbook.Sheets[workbook.SheetNames[0]]
    const data = XLSX.utils.sheet_to_json<Inv>(ws)
    list.value = data
  }
  reader.readAsArrayBuffer(file.raw)
}

function onExport() {
  const ws = XLSX.utils.json_to_sheet(list.value)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Inventory')
  XLSX.writeFile(wb, 'inventory.xlsx')
}

onMounted(loadData)
</script>

<style scoped>
.card-header { display:flex; align-items:center; justify-content:space-between; }
.toolbar { margin-bottom: 12px; }
</style>
