<template>
  <el-card>
    <template #header>
      <div class="head">
        <span>工艺路线</span>
        <el-button type="primary" @click="openAdd">新建路线</el-button>
      </div>
    </template>
    <el-row :gutter="16">
      <el-col :span="10">
        <el-table :data="list" height="60vh" @row-click="select">
          <el-table-column prop="productCode" label="产品编码"/>
          <el-table-column prop="version" label="版本" width="100"/>
          <el-table-column prop="status" label="状态" width="120"/>
        </el-table>
      </el-col>
      <el-col :span="14">
        <el-table :data="ops" height="60vh" highlight-current-row @row-click="selOp">
          <el-table-column prop="seq" label="#" width="60"/>
          <el-table-column prop="operationCode" label="工序编码"/>
          <el-table-column prop="operationName" label="工序名称"/>
          <el-table-column prop="equipmentCode" label="设备" width="120"/>
          <el-table-column prop="toolingCode" label="工装" width="120"/>
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
        <el-form-item label="产品编码"><el-input v-model="form.productCode"/></el-form-item>
        <el-form-item label="版本"><el-input v-model="form.version"/></el-form-item>
        <el-form-item label="状态"><el-select v-model="form.status"><el-option value="draft"/><el-option value="released"/></el-select></el-form-item>
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
        <el-form-item label="设备"><el-input v-model="opForm.equipmentCode"/></el-form-item>
        <el-form-item label="工装"><el-input v-model="opForm.toolingCode"/></el-form-item>
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
import type { Routing, RoutingOp } from '@/types/master'
import { routingApi, operationApi } from '@/api/masterData'
import { ElMessageBox } from 'element-plus'

const list = ref<Routing[]>([])
const current = ref<Routing | null>(null)
const ops = ref<RoutingOp[]>([])
const currentOp = ref<RoutingOp | null>(null)

const dlg = ref(false)
const form = ref<Partial<Routing>>({ status: 'draft', version: 'A', ops: [] })
const dlgOp = ref(false)
const opForm = ref<RoutingOp>({ seq: 1, operationCode: '', operationName: '' })
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

function select(r: Routing) {
  current.value = r
  ops.value = r.ops || []
  currentOp.value = null
}

function selOp(row: RoutingOp) {
  currentOp.value = row
}

function openAdd() {
  form.value = { status: 'draft', version: 'A', ops: [] } as any
  dlg.value = true
}

async function save() {
  try {
    const obj = { ...form.value } as Routing
    await routingApi.upsert(obj)
    await loadRoutings()
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
async function saveOp(){ if(!current.value) return; const opsArr = [...(current.value.ops||[])]; if (opFormMode.value==='add') { opsArr.push({ ...opForm.value }) } else { const idx = opsArr.findIndex(x => x.seq===opForm.value.seq); if (idx>=0) opsArr[idx] = { ...opForm.value } }
  // 规范化序号
  opsArr.sort((a,b)=>a.seq-b.seq).forEach((x,i)=>x.seq=i+1)
  const newObj = { ...current.value, ops: opsArr } as Routing; await routingApi.upsert(newObj); list.value = await routingApi.list(); select(newObj); dlgOp.value = false }
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
  const opsArr = (current.value.ops||[]).filter(x => x.seq !== currentOp.value!.seq)
  opsArr.forEach((x,i)=>x.seq=i+1)
  const newObj = { ...current.value, ops: opsArr } as Routing
  await routingApi.upsert(newObj)
  list.value = await routingApi.list()
  select(newObj)
}
const canMoveUp = computed(()=> !!current.value && !!currentOp.value && currentOp.value.seq>1)
const canMoveDown = computed(()=> !!current.value && !!currentOp.value && currentOp.value.seq < (current.value?.ops?.length||0))
function moveUp(){ if(!current.value || !currentOp.value || currentOp.value.seq<=1) return; swap(currentOp.value.seq, currentOp.value.seq-1) }
function moveDown(){ if(!current.value || !currentOp.value) return; const last = current.value.ops?.length||0; if(currentOp.value.seq>=last) return; swap(currentOp.value.seq, currentOp.value.seq+1) }
async function swap(a: number, b: number){ if(!current.value) return; const opsArr = [...(current.value.ops||[])]; const ia = opsArr.findIndex(x=>x.seq===a); const ib = opsArr.findIndex(x=>x.seq===b); if(ia<0||ib<0) return; const ta = { ...opsArr[ia], seq: b }; const tb = { ...opsArr[ib], seq: a }; opsArr[ia]=tb; opsArr[ib]=ta; opsArr.sort((x,y)=>x.seq-y.seq); const newObj = { ...current.value, ops: opsArr } as Routing; await routingApi.upsert(newObj); list.value = await routingApi.list(); select(newObj); currentOp.value = opsArr.find(x=>x.seq===b) || null }
</script>

<style scoped>
.head{display:flex;align-items:center;justify-content:space-between}
</style>
