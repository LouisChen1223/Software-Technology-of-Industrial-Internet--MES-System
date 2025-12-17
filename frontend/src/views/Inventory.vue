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
    <el-dialog v-model="dlgVisible" :title="dlgTitle" width="560px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="工单(编号或ID)" v-if="dlg!=='supplement' && dlg!=='return'">
          <el-input v-model="(form as any).work_order_code" placeholder="示例: WO20251214001 或 直接填ID" clearable />
        </el-form-item>
        <el-form-item label="物料(编码或ID)" v-if="dlg!=='bom'">
          <el-input v-model="(form as any).material_code" placeholder="支持数字ID或编码(不带横线)" clearable />
        </el-form-item>
        <el-form-item label="仓库(编码或ID)">
          <el-input v-model="(form as any).warehouse_code" placeholder="支持数字ID或编码(不带横线)" clearable />
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
import { materialApi, warehouseApi } from '@/api/masterData'
import { workorderApi } from '@/api/workorder'
import { ElMessage } from 'element-plus'

interface Inv { material: string; lot: string; loc: string; qty: number; uom: string }
const list = ref<Inv[]>([])
const q = ref('')

const filtered = computed(() => {
  if (!q.value) return list.value
  return list.value.filter(r => (r.material + r.lot + r.loc).includes(q.value))
})

// 主数据（用于把编码映射到数值ID，并展示编码）
const materialCodeToId = ref<Record<string, number>>({})
const warehouseCodeToId = ref<Record<string, number>>({})
const materialIdToCode = ref<Record<number, string>>({})
const workorderCodeToId = ref<Record<string, number>>({})

function normalizeCode(input: string): string {
  if (!input) return ''
  return input.replace(/[\-\s]/g, '').toUpperCase()
}

function isDigits(input: string): boolean {
  return /^\d+$/.test(input)
}

async function loadMasters() {
  const [materials, warehouses, workorders] = await Promise.all([
    materialApi.list(),
    warehouseApi.list(),
    workorderApi.list()
  ])
  materialCodeToId.value = {}
  materialIdToCode.value = {}
  for (const m of materials) {
    const idNum = Number(m.id)
    if (!Number.isNaN(idNum)) {
      materialIdToCode.value[idNum] = m.code
    }
    if (m.code) {
      materialCodeToId.value[m.code] = idNum
      materialCodeToId.value[normalizeCode(m.code)] = idNum
    }
  }
  warehouseCodeToId.value = {}
  for (const w of warehouses) {
    const idNum = Number(w.id)
    if (w.code) {
      warehouseCodeToId.value[w.code] = idNum
      warehouseCodeToId.value[normalizeCode(w.code)] = idNum
    }
  }

  workorderCodeToId.value = {}
  for (const wo of workorders) {
    const idNum = Number(wo.id)
    const code = (wo.woNo || wo.code)
    if (idNum && code) {
      workorderCodeToId.value[code] = idNum
      workorderCodeToId.value[normalizeCode(code)] = idNum
    }
  }
}

async function loadData() {
  const resp = await inventoryApi.list()
  list.value = resp.map(r => ({
    material: materialIdToCode.value[r.material_id] || `ID-${r.material_id}`,
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
  work_order_code: '',
  material_code: '',
  warehouse_code: '',
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
    // 将输入转换为数值ID（支持数字ID直输，或编码大小写不敏感、无横线匹配）
    const matInput = (form.value.material_code || '').trim()
    const whInput = (form.value.warehouse_code || '').trim()
    const woInput = (form.value.work_order_code || '').trim()
    // 解析工单
    let work_order_id: number | undefined = undefined
    if (dlg.value === 'pick' || dlg.value === 'bom') {
      if (woInput) {
        if (isDigits(woInput)) {
          work_order_id = Number(woInput)
        } else {
          const norm = normalizeCode(woInput)
          work_order_id = workorderCodeToId.value[woInput] ?? workorderCodeToId.value[norm]
        }
      }
    }

    let material_id: number | undefined = undefined
    if (dlg.value !== 'bom') {
      if (!matInput) {
        ElMessage.error('请填写物料(编码或数字ID)')
        return
      }
      if (isDigits(matInput)) {
        material_id = Number(matInput)
      } else {
        const norm = normalizeCode(matInput)
        material_id = materialCodeToId.value[matInput] ?? materialCodeToId.value[norm]
      }
    }

    let warehouse_id: number | undefined = undefined
    if (!whInput) {
      ElMessage.error('请填写仓库(编码或数字ID)')
      return
    }
    if (isDigits(whInput)) {
      warehouse_id = Number(whInput)
    } else {
      const norm = normalizeCode(whInput)
      warehouse_id = warehouseCodeToId.value[whInput] ?? warehouseCodeToId.value[norm]
    }

    if (dlg.value !== 'bom' && !material_id) {
      ElMessage.error('未找到对应的物料（仅支持数字ID或有效编码，不带横线）')
      return
    }
    if (!warehouse_id) {
      ElMessage.error('未找到对应的仓库（仅支持数字ID或有效编码，不带横线）')
      return
    }

    if (dlg.value === 'pick') {
      // 预校验批次是否存在（减少 400 误会）
      const invs = await inventoryApi.list({ material_id: material_id!, warehouse_id: warehouse_id! })
      const batches = Array.from(new Set((invs || []).map(i => i.batch_number).filter(Boolean))) as string[]
      if (!form.value.batch_number) {
        if (batches.length === 1) {
          form.value.batch_number = batches[0]
        } else {
          ElMessage.error(`请选择批次。可用批次: ${batches.length ? batches.join(', ') : '无库存'}`)
          return
        }
      } else if (!batches.includes(form.value.batch_number)) {
        ElMessage.error(`该物料/仓库下无此批次。可用批次: ${batches.length ? batches.join(', ') : '无'}`)
        return
      }
      await inventoryApi.trans({
        transaction_type: 'pick',
        material_id: material_id!,
        warehouse_id: warehouse_id!,
        work_order_id,
        batch_number: form.value.batch_number,
        quantity: form.value.quantity,
        reference_no: 'UI-PICK'
      })
    } else if (dlg.value === 'supplement') {
      await inventoryApi.trans({
        transaction_type: 'receive',
        material_id: material_id!,
        warehouse_id: warehouse_id!,
        batch_number: form.value.batch_number,
        quantity: form.value.quantity,
        reference_no: 'UI-SUPPLEMENT'
      })
    } else if (dlg.value === 'return') {
      await inventoryApi.trans({
        transaction_type: 'return',
        material_id: material_id!,
        warehouse_id: warehouse_id!,
        batch_number: form.value.batch_number,
        quantity: form.value.quantity,
        reference_no: 'UI-RETURN'
      })
    } else if (dlg.value === 'bom') {
      if (!work_order_id) {
        ElMessage.error('请填写有效的工单编号或ID')
        return
      }
      await inventoryApi.createPickFromBOM(work_order_id, warehouse_id!)
    }
    dlg.value = ''
    await loadData()
  } catch (e) {
    console.error('操作失败', e)
    // 尽量展示后端返回的具体原因（如库存不足/批次不存在）
    const msg = (e && (e as any).response && ((e as any).response.data?.detail || (e as any).response.data?.message))
      || (e as any).message || '操作失败，请检查输入与网络'
    ElMessage.error(msg)
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

onMounted(async () => {
  await loadMasters()
  await loadData()
})
</script>

<style scoped>
.card-header { display:flex; align-items:center; justify-content:space-between; }
.toolbar { margin-bottom: 12px; }
</style>
