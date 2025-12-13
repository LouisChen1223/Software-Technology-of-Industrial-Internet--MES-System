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
      <el-button type="primary" @click="openPick">普通领料</el-button>
      <el-button type="primary" @click="openBOMPick">按BOM领料</el-button>
      <el-button @click="openSupplement">补料(入库)</el-button>
      <el-button type="warning" @click="openReturn">退料(入库)</el-button>
    </div>
    <el-table :data="filtered" height="60vh" stripe>
      <el-table-column prop="material" label="物料"/>
      <el-table-column prop="lot" label="批次"/>
      <el-table-column prop="loc" label="库位" width="120"/>
      <el-table-column prop="qty" label="数量" width="100"/>
      <el-table-column prop="uom" label="单位" width="80"/>
    </el-table>

    <!-- 操作对话框 -->
    <el-dialog v-model="dlgVisible" :title="dlgTitle" width="520px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="工单ID" v-if="dlg!=='supplement' && dlg!=='return'">
          <el-input-number v-model="(form as any).work_order_id" :min="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="物料ID" v-if="dlg!=='bom'">
          <el-input-number v-model="(form as any).material_id" :min="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="仓库ID">
          <el-input-number v-model="(form as any).warehouse_id" :min="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="批次">
          <el-input v-model="(form as any).batch_number" />
        </el-form-item>
        <el-form-item label="数量" v-if="dlg!=='bom'">
          <el-input-number v-model="(form as any).quantity" :min="1" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDlg">取消</el-button>
        <el-button type="primary" @click="submit">确认</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import * as XLSX from 'xlsx'
import { inventoryApi } from '@/api/inventory'

interface Inv { material: string; lot: string; loc: string; qty: number; uom: string }
const list = ref<Inv[]>([])
const q = ref('')

const filtered = computed(() => {
  if (!q.value) return list.value
  return list.value.filter(r => (r.material + r.lot + r.loc).includes(q.value))
})

async function loadData() {
  const resp = await inventoryApi.list()
  // 简易映射（需要结合主数据才能显示物料编码等，这里只填关键字段）
  list.value = resp.map(r => ({
    material: `MAT-${r.material_id}`,
    lot: r.batch_number || '-',
    loc: r.location || '-',
    qty: r.available_quantity,
    uom: 'PCS'
  }))
}

// 对话框与表单
const dlg = ref<'pick' | 'bom' | 'supplement' | 'return' | ''>('')
const dlgVisible = computed({
  get: () => dlg.value !== '',
  set: (v: boolean) => { if (!v) dlg.value = '' }
})
const dlgTitle = computed(() => dlg.value === 'pick' ? '普通领料' : dlg.value === 'bom' ? '按BOM领料' : dlg.value === 'supplement' ? '补料入库' : dlg.value === 'return' ? '退料入库' : '')
const form = ref({
  work_order_id: undefined as number | undefined,
  material_id: undefined as number | undefined,
  warehouse_id: 1,
  batch_number: '',
  quantity: 1
})

function openPick() { dlg.value = 'pick' }
function openBOMPick() { dlg.value = 'bom' }
function openSupplement() { dlg.value = 'supplement' }
function openReturn() { dlg.value = 'return' }

function closeDlg() { dlg.value = '' }

async function submit() {
  try {
    if (dlg.value === 'pick') {
      await inventoryApi.trans({
        transaction_type: 'pick',
        material_id: form.value.material_id!,
        warehouse_id: form.value.warehouse_id,
        work_order_id: form.value.work_order_id,
        batch_number: form.value.batch_number,
        quantity: form.value.quantity,
        reference_no: 'UI-PICK'
      })
    } else if (dlg.value === 'supplement') {
      await inventoryApi.trans({
        transaction_type: 'receive',
        material_id: form.value.material_id!,
        warehouse_id: form.value.warehouse_id,
        batch_number: form.value.batch_number,
        quantity: form.value.quantity,
        reference_no: 'UI-SUPPLEMENT'
      })
    } else if (dlg.value === 'return') {
      await inventoryApi.trans({
        transaction_type: 'return',
        material_id: form.value.material_id!,
        warehouse_id: form.value.warehouse_id,
        batch_number: form.value.batch_number,
        quantity: form.value.quantity,
        reference_no: 'UI-RETURN'
      })
    } else if (dlg.value === 'bom') {
      await inventoryApi.createPickFromBOM(form.value.work_order_id!, form.value.warehouse_id)
    }
    dlg.value = ''
    await loadData()
  } catch (e) {
    console.error('操作失败', e)
  }
}

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
