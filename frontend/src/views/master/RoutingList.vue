<template>
  <el-card>
    <template #header>
      <div class="head">
        <span>工艺路线</span>
        <div style="display:flex;gap:8px;align-items:center">
          <el-input v-model="filterProductCode" placeholder="产品编码" style="width:160px"/>
          <el-input v-model="filterVersion" placeholder="版本" style="width:120px"/>
          <el-checkbox v-model="filterActiveOnly">仅激活</el-checkbox>
          <el-button size="small" @click="applyFilter">筛选</el-button>
          <el-button type="primary" @click="openAdd">新建路线</el-button>
        </div>
      </div>
    </template>
    <el-row :gutter="16">
      <el-col :span="10">
        <el-table :data="list" height="60vh" @row-click="select">
          <el-table-column prop="code" label="路线编码" width="140"/>
          <el-table-column prop="name" label="名称"/>
          <el-table-column prop="product_id" label="产品ID" width="120"/>
          <el-table-column prop="version" label="版本" width="100"/>
          <el-table-column prop="is_active" label="激活" width="80">
            <template #default="{row}">{{ row.is_active ? '是' : '否' }}</template>
          </el-table-column>
        </el-table>
      </el-col>
      <el-col :span="14">
        <el-table :data="ops" height="60vh" highlight-current-row @row-click="selOp" row-key="sequence">
          <el-table-column prop="sequence" label="#" width="60"/>
          <el-table-column prop="operation_code" label="工序编码"/>
          <el-table-column prop="operation_name" label="工序名称"/>
          <el-table-column prop="equipment_id" label="设备ID" width="120"/>
        </el-table>
        <div style="margin-top:8px">
          <el-button size="small" @click="openAddOp" :disabled="!current">新增工序</el-button>
          <el-button size="small" @click="openEditOp" :disabled="!current || !currentOp">编辑</el-button>
          <el-button size="small" type="danger" @click="removeOp" :disabled="!current || !currentOp">删除</el-button>
          <el-button size="small" @click="moveUp" :disabled="!canMoveUp">上移</el-button>
          <el-button size="small" @click="moveDown" :disabled="!canMoveDown">下移</el-button>
        </div>
      </el-col>
    </el-row>

    <el-dialog v-model="dlg" title="新建路线" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="路线编码"><el-input v-model="form.code"/></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="产品编码"><el-input v-model="form.productCode"/></el-form-item>
        <el-form-item label="版本"><el-input v-model="form.version"/></el-form-item>
        <el-form-item label="激活"><el-switch v-model="form.is_active"/></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg=false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="dlgOp" :title="opFormMode==='add'?'新增工序':'编辑工序'" width="520px">
      <el-form :model="opForm" label-width="100px">
        <el-form-item label="工序"><el-select v-model="opForm.operationCode" filterable style="width: 100%" @change="syncOpName">
          <el-option v-for="o in opList" :key="o.code" :label="o.code + ' - ' + o.name" :value="o.code"/>
        </el-select></el-form-item>
        <el-form-item label="#序号"><el-input v-model="opForm.seq" disabled/></el-form-item>
        <el-form-item label="设备ID"><el-input-number v-model="opForm.equipmentId" :min="0"/></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlgOp=false">取消</el-button>
        <el-button type="primary" @click="saveOp">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Routing, RoutingOp, Material } from '@/types/master'
import { routingApi, operationApi, materialApi } from '@/api/masterData'
import { ElMessageBox } from 'element-plus'

const list = ref<any[]>([])
const current = ref<Routing | null>(null)
const ops = ref<any[]>([])
const currentOp = ref<any | null>(null)

const dlg = ref(false)
const form = ref<any>({ code: '', name: '', productCode: '', version: '1.0', is_active: true })
const dlgOp = ref(false)
const opForm = ref<any>({ seq: 1, operationCode: '', operationName: '', equipmentId: undefined })
const filterProductCode = ref('')
const filterVersion = ref('')
const filterActiveOnly = ref(true)
const opFormMode = ref<'add'|'edit'>('add')
const opList = ref<any[]>([])

async function loadOps() {
  try {
    opList.value = await operationApi.list()
  } catch (error) {
    console.error('加载工序列表失败:', error)
  }
}

async function loadRoutings() {
  try {
    list.value = await routingApi.list()
  } catch (error) {
    console.error('加载工艺路线失败:', error)
  }
}

async function applyFilter(){
  try {
    if (!filterProductCode.value) { list.value = await routingApi.list(); return }
    const mats = await materialApi.list()
    const prod = mats.find(m=>m.code===filterProductCode.value)
    if (!prod) { list.value = []; return }
    list.value = await routingApi.byProduct(prod.id, { version: filterVersion.value || undefined, activeOnly: filterActiveOnly.value })
  } catch (e) { console.error(e) }
}

async function select(r: any) {
  current.value = r
  // 将后端 items 转换为可显示的工序列表（填充工序编码与名称）
  const opMetaList = await operationApi.list()
  ops.value = (r.items || []).map((it:any)=>{
    const meta = opMetaList.find((o:any)=> String(o.id) === String(it.operation_id))
    return {
      ...it,
      sequence: Number(it.sequence),
      operation_code: meta?.code || '',
      operation_name: meta?.name || ''
    }
  })
  currentOp.value = null
}

function selOp(row: RoutingOp) {
  currentOp.value = row
}

function openAdd() {
  form.value = { code: '', name: '', productCode: '', version: '1.0', is_active: true }
  dlg.value = true
}

async function save() {
  try {
    const mats: Material[] = await materialApi.list()
    const prod = mats.find(m => m.code === form.value.productCode)
    if (!prod) throw new Error('未找到对应的成品物料，请先在物料中创建')
    const payload = { code: form.value.code, name: form.value.name, product_id: Number(prod.id), version: form.value.version, is_active: form.value.is_active ? 1 : 0, items: [] }
    if (!payload.code || !payload.name) throw new Error('请填写路线编码与名称')
    await routingApi.create(payload)
    await applyFilter()
    dlg.value = false
  } catch (error) {
    console.error('保存工艺路线失败:', error)
  }
}

onMounted(() => {
  loadRoutings()
  loadOps()
})
function openAddOp(){ if(!current.value) return; const seq = (current.value.ops?.length || 0) + 1; opForm.value = { seq, operationCode: '', operationName: '' } as any; opFormMode.value='add'; dlgOp.value = true }
function openEditOp(){ if(!current.value || !currentOp.value) return; opForm.value = { ...currentOp.value } as any; opFormMode.value='edit'; dlgOp.value = true }
function syncOpName(){ const opMeta = opList.value.find(o => o.code === opForm.value.operationCode); opForm.value.operationName = opMeta ? opMeta.name : '' }
async function saveOp(){
  if(!current.value) return;
  // 必须选择目标工艺路线
  if(!current.value) { console.error('请先选择要新增工序的工艺路线'); return }
  // 获取当前详细 items
  const detailList = list.value
  const routeDetail = detailList.find((r:any)=>r.id===current.value!.id)
  const existingItems = (routeDetail?.items || []).map((it:any)=>({ operation_id: it.operation_id, sequence: it.sequence, equipment_id: it.equipment_id, standard_time: it.standard_time, setup_time: it.setup_time, description: it.description }))
  // 将所选工序编码映射为ID
  const opMeta = opList.value.find((o:any)=>o.code===opForm.value.operationCode)
  if (!opMeta) return
  let updatedItems = existingItems
  if (opFormMode.value==='add') {
    updatedItems = [...existingItems, { operation_id: Number(opMeta.id), sequence: (existingItems.length||0)+1, equipment_id: opForm.value.equipmentId }]
  } else {
    updatedItems = existingItems.map((x:any)=> x.sequence===opForm.value.seq ? { ...x, operation_id: Number(opMeta.id), equipment_id: opForm.value.equipmentId } : x)
  }
  updatedItems.sort((a:any,b:any)=>a.sequence-b.sequence).forEach((x:any,i:number)=>x.sequence=i+1)
  await routingApi.update(current.value!.id, { items: updatedItems })
  list.value = await routingApi.list();
  const refreshed = list.value.find((r:any)=>r.id===current.value!.id)
  await select(refreshed)
  dlgOp.value = false
}
async function removeOp(){
  if(!current.value || !currentOp.value) return;
  try {
    await ElMessageBox.confirm('确认删除该工序？删除后不可恢复。', '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
  } catch {
    return
  }
  const existing = (current.value as any).items || []
  const nextItems = existing.filter((x:any)=> x.sequence !== currentOp.value!.seq)
  nextItems.forEach((x:any,i:number)=>x.sequence=i+1)
  await routingApi.update((current.value as any).id, { items: nextItems })
  list.value = await routingApi.list()
  const refreshed = list.value.find((r:any)=>r.id===(current.value as any).id)
  await select(refreshed)
}
const selectedIndex = computed(()=>{
  if (!currentOp.value) return -1
  return ops.value.findIndex((x:any)=> Number(x.sequence) === Number(currentOp.value!.sequence))
})
const canMoveUp = computed(()=> selectedIndex.value > 0)
const canMoveDown = computed(()=> selectedIndex.value >= 0 && selectedIndex.value < (ops.value.length - 1))
function moveUp(){
  if(!current.value || !currentOp.value){ console.warn('未选择工序'); return }
  const idx = selectedIndex.value
  if(idx<=0) return
  console.log('上移: index=', idx)
  swapByIndex(idx, idx-1)
}
function moveDown(){
  if(!current.value || !currentOp.value){ console.warn('未选择工序'); return }
  const idx = selectedIndex.value
  const last = (ops.value?.length || 0) - 1
  if(idx<0 || idx>=last) return
  console.log('下移: index=', idx)
  swapByIndex(idx, idx+1)
}
async function swapByIndex(aIdx: number, bIdx: number){
  if(!current.value) return;
  try {
    // 拉取最新详情以避免本地状态与后端不一致
    const latestList = await routingApi.list()
    const detail = latestList.find((r:any)=>r.id===(current.value as any).id)
    const existing = (detail?.items || [])
    if(existing.length===0) return
    // 按 sequence 排序，基于索引交换
    const sorted = [...existing].sort((x:any,y:any)=>Number(x.sequence)-Number(y.sequence))
    if(aIdx<0 || bIdx<0 || aIdx>=sorted.length || bIdx>=sorted.length) return
    const temp = sorted[aIdx]
    sorted[aIdx] = sorted[bIdx]
    sorted[bIdx] = temp
    // 规范化 sequence 为 1..n
    const next = sorted.map((it:any, idx:number)=> ({
      operation_id: it.operation_id,
      sequence: idx+1,
      equipment_id: it.equipment_id,
      standard_time: it.standard_time,
      setup_time: it.setup_time,
      description: it.description
    }))
    console.log('提交更新 routing.items = ', next)
    await routingApi.update((current.value as any).id, { items: next })
    // 刷新并选中新的位置 bIdx
    list.value = await routingApi.list()
    const refreshed = list.value.find((r:any)=>r.id===(current.value as any).id)
    await select(refreshed)
    const targetSeq = bIdx + 1
    currentOp.value = (refreshed?.items || []).find((x:any)=>Number(x.sequence)===targetSeq) || null
  } catch (e) {
    console.error('移动工序失败:', e)
  }
}
</script>

<style scoped>
.head{display:flex;align-items:center;justify-content:space-between}
</style>
