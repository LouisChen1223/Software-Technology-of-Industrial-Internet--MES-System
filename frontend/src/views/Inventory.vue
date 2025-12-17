<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>库存 / 出入库</span>
        <div>
          <el-input
            v-model="q"
            placeholder="物料 / 批次 / 库位"
            style="width:220px;margin-right:8px"
          />
          <el-upload :auto-upload="false" accept=".xlsx,.xls" :on-change="onImport">
            <el-button>导入 Excel</el-button>
          </el-upload>
          <el-button @click="onExport">导出</el-button>
        </div>
      </div>
    </template>

    <div class="toolbar">
      <el-button type="primary" @click="openPick">普通领料</el-button>
      <el-button type="primary" @click="openBOMPick">按 BOM 领料</el-button>
      <el-button @click="openSupplement">补料（入库）</el-button>
      <el-button type="warning" @click="openReturn">退料（入库）</el-button>
    </div>

    <el-table :data="filtered" height="60vh" stripe>
      <el-table-column prop="material" label="物料" />
      <el-table-column prop="lot" label="批次" />
      <el-table-column prop="loc" label="库位" width="120" />
      <el-table-column prop="qty" label="数量" width="100" />
      <el-table-column prop="uom" label="单位" width="80" />
    </el-table>

    <!-- 操作对话框 -->
    <el-dialog v-model="dlgVisible" :title="dlgTitle" width="560px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="工单" v-if="dlg !== 'supplement' && dlg !== 'return'">
          <el-select
            v-model="form.work_order_code"
            placeholder="选择工单"
            filterable
            clearable
          >
            <el-option
              v-for="wo in workorderOptions"
              :key="wo.id"
              :label="(wo.woNo || wo.code) + ' | ' + (wo.status || '')"
              :value="wo.woNo || wo.code"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="物料" v-if="dlg !== 'bom'">
          <el-select
            v-model="form.material_code"
            placeholder="选择物料"
            filterable
            clearable
          >
            <el-option
              v-for="m in materialOptions"
              :key="m.id"
              :label="`${m.code} | ${m.name}`"
              :value="m.code"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="仓库">
          <el-select
            v-model="form.warehouse_code"
            placeholder="选择仓库"
            filterable
            clearable
          >
            <el-option
              v-for="w in warehouseOptions"
              :key="w.id"
              :label="`${w.code} | ${w.name}`"
              :value="w.code"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="批次" v-if="dlg !== 'bom'">
          <el-input v-model="form.batch_number" />
        </el-form-item>

        <el-form-item label="数量" v-if="dlg !== 'bom'">
          <el-input-number v-model="form.quantity" :min="1" style="width:100%" />
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
import { inventoryApi, type InventoryItem } from '@/api/inventory'
import { materialApi, warehouseApi } from '@/api/masterData'
import { workorderApi } from '@/api/workorder'
import { ElMessage } from 'element-plus'

interface InvRow {
  material: string
  lot: string
  loc: string
  qty: number
  uom: string
}

const list = ref<InvRow[]>([])
const q = ref('')

const filtered = computed(() => {
  if (!q.value) return list.value
  return list.value.filter((r) => (r.material + r.lot + r.loc).includes(q.value))
})

// 主数据（用于把编码映射到数值 ID，并展示编码）
const materialOptions = ref<any[]>([])
const warehouseOptions = ref<any[]>([])
const workorderOptions = ref<any[]>([])
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
    workorderApi.list(),
  ])

  materialOptions.value = materials.filter((m: any) => m.active !== 0)
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

  warehouseOptions.value = warehouses.filter((w: any) => w.active !== 0)
  warehouseCodeToId.value = {}
  for (const w of warehouses) {
    const idNum = Number(w.id)
    if (w.code) {
      warehouseCodeToId.value[w.code] = idNum
      warehouseCodeToId.value[normalizeCode(w.code)] = idNum
    }
  }

  workorderCodeToId.value = {}
  workorderOptions.value = workorders.filter((wo: any) =>
    ['released', 'in_progress', 'paused'].includes(wo.status),
  )
  for (const wo of workorderOptions.value) {
    const idNum = Number(wo.id)
    const code = wo.woNo || wo.code
    if (idNum && code) {
      workorderCodeToId.value[code] = idNum
      workorderCodeToId.value[normalizeCode(code)] = idNum
    }
  }
}

async function loadData() {
  const resp = await inventoryApi.list()
  list.value = (resp as InventoryItem[]).map((r) => ({
    material: materialIdToCode.value[r.material_id] || `ID-${r.material_id}`,
    lot: r.batch_number || '-',
    loc: r.location || '-',
    qty: r.available_quantity,
    uom: 'PCS',
  }))
}

// 对话框与表单
const dlg = ref<'pick' | 'bom' | 'supplement' | 'return' | ''>('')
const dlgVisible = computed({
  get: () => dlg.value !== '',
  set: (v: boolean) => {
    if (!v) dlg.value = ''
  },
})
const dlgTitle = computed(() => {
  if (dlg.value === 'pick') return '普通领料'
  if (dlg.value === 'bom') return '按 BOM 领料'
  if (dlg.value === 'supplement') return '补料入库'
  if (dlg.value === 'return') return '退料入库'
  return ''
})

const form = ref({
  work_order_code: '',
  material_code: '',
  warehouse_code: '',
  batch_number: '',
  quantity: 1,
})

function openPick() {
  dlg.value = 'pick'
}
function openBOMPick() {
  dlg.value = 'bom'
}
function openSupplement() {
  dlg.value = 'supplement'
}
function openReturn() {
  dlg.value = 'return'
}

function closeDlg() {
  dlg.value = ''
}

async function submit() {
  try {
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
        ElMessage.error('请选择物料')
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
      ElMessage.error('请选择仓库')
      return
    }
    if (isDigits(whInput)) {
      warehouse_id = Number(whInput)
    } else {
      const norm = normalizeCode(whInput)
      warehouse_id = warehouseCodeToId.value[whInput] ?? warehouseCodeToId.value[norm]
    }

    if (dlg.value !== 'bom' && !material_id) {
      ElMessage.error('未找到对应物料（仅支持数字 ID 或有效编码）')
      return
    }
    if (!warehouse_id) {
      ElMessage.error('未找到对应仓库（仅支持数字 ID 或有效编码）')
      return
    }

    if (dlg.value === 'pick') {
      // 预校验批次是否存在，减少 400 错误
      const invs = await inventoryApi.list({
        material_id: material_id!,
        warehouse_id: warehouse_id!,
      })
      const batches = Array.from(
        new Set((invs as any[]).map((i) => i.batch_number).filter(Boolean)),
      ) as string[]
      if (!form.value.batch_number) {
        ElMessage.error('普通领料必须选择批次')
        return
      }
      if (!form.value.batch_number) {
        if (batches.length === 1) {
          form.value.batch_number = batches[0]
        } else {
          ElMessage.error(
            `请选择批次。可用批次：${batches.length ? batches.join(', ') : '无库存'}`,
          )
          return
        }
      } else if (!batches.includes(form.value.batch_number)) {
        ElMessage.error(
          `该物料在此仓库下无此批次。可用批次：${
            batches.length ? batches.join(', ') : '无'
          }`,
        )
        return
      }

      await inventoryApi.trans({
        transaction_type: 'pick',
        material_id: material_id!,
        warehouse_id: warehouse_id!,
        work_order_id,
        batch_number: form.value.batch_number,
        quantity: form.value.quantity,
        reference_no: 'UI-PICK',
      })
    } else if (dlg.value === 'supplement') {
      if (!form.value.batch_number) {
        ElMessage.error('补料必须填写批次')
        return
      }
      await inventoryApi.trans({
        transaction_type: 'receive',
        material_id: material_id!,
        warehouse_id: warehouse_id!,
        batch_number: form.value.batch_number,
        quantity: form.value.quantity,
        reference_no: 'UI-SUPPLEMENT',
      })
    } else if (dlg.value === 'return') {
      if (!form.value.batch_number) {
        ElMessage.error('退料必须填写批次')
        return
      }
      await inventoryApi.trans({
        transaction_type: 'return',
        material_id: material_id!,
        warehouse_id: warehouse_id!,
        batch_number: form.value.batch_number,
        quantity: form.value.quantity,
        reference_no: 'UI-RETURN',
      })
    } else if (dlg.value === 'bom') {
      if (!work_order_id) {
        ElMessage.error('请选择有效的工单')
        return
      }
      const pick: any = await inventoryApi.createPickFromBOM(
        work_order_id,
        warehouse_id!,
      )
      if (!pick || !Array.isArray(pick.items) || !pick.items.length) {
        ElMessage.error('按 BOM 生成领料明细失败')
        return
      }
      // 直接按 BOM 明细生成出库事务（每个明细一笔 pick 事务）
      for (const item of pick.items as any[]) {
        const matId = Number(item.material_id)
        const reqQty = Number(item.required_quantity || 0)
        if (!matId || reqQty <= 0) continue
        const invs = await inventoryApi.list({
          material_id: matId,
          warehouse_id: warehouse_id!,
        })
        const inv = (invs as any[])[0]
        if (!inv || inv.available_quantity < reqQty) {
          ElMessage.error(`物料 ${matId} 库存不足，无法按 BOM 领料`)
          return
        }
        await inventoryApi.trans({
          transaction_type: 'pick',
          material_id: matId,
          warehouse_id: warehouse_id!,
          batch_number: inv.batch_number,
          quantity: reqQty,
          reference_no: pick.code || 'UI-BOM-PICK',
        })
      }
    }

    dlg.value = ''
    await loadData()
  } catch (e: any) {
    console.error('操作失败', e)
    const msg =
      e?.response?.data?.detail ||
      e?.response?.data?.message ||
      e?.message ||
      '操作失败，请检查输入与网络'
    ElMessage.error(msg)
  }
}

function onImport(file: any) {
  const reader = new FileReader()
  reader.onload = () => {
    const workbook = XLSX.read(reader.result as ArrayBuffer, { type: 'array' })
    const ws = workbook.Sheets[workbook.SheetNames[0]]
    const data = XLSX.utils.sheet_to_json<InvRow>(ws)
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
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.toolbar {
  margin-bottom: 12px;
}
</style>
