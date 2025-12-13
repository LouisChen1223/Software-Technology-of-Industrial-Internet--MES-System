<template>
  <el-card>
    <template #header>
      <div class="head">
        <span>BOM 管理</span>
        <div style="display:flex;gap:8px;align-items:center">
          <el-input v-model="filterProductCode" placeholder="产品编码" style="width:160px"/>
          <el-input v-model="filterVersion" placeholder="版本" style="width:120px"/>
          <el-checkbox v-model="filterActiveOnly">仅激活</el-checkbox>
          <el-button size="small" @click="applyFilter">筛选</el-button>
          <el-button type="primary" @click="openHeader">新建BOM</el-button>
        </div>
      </div>
    </template>
    <el-row :gutter="16">
      <el-col :span="10">
        <el-table :data="headers" height="60vh" @row-click="selectHeader">
          <el-table-column prop="code" label="BOM编码" width="140"/>
          <el-table-column prop="name" label="名称"/>
          <el-table-column prop="product_id" label="产品ID" width="120"/>
          <el-table-column prop="version" label="版本" width="100"/>
          <el-table-column prop="is_active" label="激活" width="80">
            <template #default="{row}">{{ row.is_active ? '是' : '否' }}</template>
          </el-table-column>
        </el-table>
      </el-col>
      <el-col :span="14">
        <el-table :data="items" height="60vh">
          <el-table-column prop="sequence" label="#" width="60"/>
          <el-table-column prop="material_id" label="物料ID" width="100"/>
          <el-table-column prop="material_code" label="物料编码"/>
          <el-table-column prop="material_name" label="物料名称"/>
          <el-table-column prop="quantity" label="用量" width="100"/>
          <el-table-column prop="scrap_rate" label="损耗%" width="100"/>
        </el-table>
        <div style="margin-top:8px">
          <el-button size="small" @click="addItem" :disabled="!current">新增行</el-button>
        </div>
      </el-col>
    </el-row>

    <el-dialog v-model="dlgHeader" title="新建BOM" width="520px">
      <el-form :model="headerForm" label-width="90px">
        <el-form-item label="BOM编码"><el-input v-model="headerForm.code"/></el-form-item>
        <el-form-item label="名称"><el-input v-model="headerForm.name"/></el-form-item>
        <el-form-item label="产品">
          <el-select v-model="headerForm.productCode" filterable placeholder="选择成品物料">
            <el-option v-for="m in allMaterials.filter(mm=>mm.type==='成品')" :key="m.code" :label="m.name + ' (' + m.code + ')'" :value="m.code"/>
          </el-select>
        </el-form-item>
        <el-form-item label="版本"><el-input v-model="headerForm.version"/></el-form-item>
        <el-form-item label="激活"><el-switch v-model="headerForm.is_active"/></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlgHeader=false">取消</el-button>
        <el-button type="primary" @click="saveHeader">保存</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="dlgItem" title="新增BOM行" width="520px">
      <el-form :model="itemForm" label-width="90px">
        <el-form-item label="选择物料">
          <el-select v-model="itemForm.materialCode" filterable placeholder="选择有库存的物料">
            <el-option v-for="m in stockedMaterials" :key="m.material_code" :label="m.material_name + ' (' + m.material_code + ')'" :value="m.material_code"/>
          </el-select>
        </el-form-item>
        <el-form-item label="用量"><el-input-number v-model="(itemForm as any).qty" :min="0"/></el-form-item>
        <el-form-item label="损耗%"><el-input-number v-model="(itemForm as any).scrapRate" :min="0" :max="100"/></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlgItem=false">取消</el-button>
        <el-button type="primary" @click="saveItem">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { BomHeader, BomItem, Material } from '@/types/master'
import { bomApi, materialApi } from '@/api/masterData'
import http from '@/api/http'

const headers = ref<any[]>([])
const items = ref<any[]>([])
const current = ref<any | null>(null)

const dlgHeader = ref(false)
const headerForm = ref<any>({ code: '', name: '', productCode: '', version: '1.0', is_active: true })

const dlgItem = ref(false)
const itemForm = ref<any>({ materialCode: '', qty: 1, scrapRate: 0 })
const stockedMaterials = ref<any[]>([])
const allMaterials = ref<Material[]>([])
const filterProductCode = ref('')
const filterVersion = ref('')
const filterActiveOnly = ref(true)

async function load() {
  try {
    headers.value = await bomApi.list()
    allMaterials.value = await materialApi.list()
  } catch (error) {
    console.error('加载BOM失败:', error)
  }
}

async function applyFilter(){
  try {
    if (!filterProductCode.value) { headers.value = await bomApi.list(); return }
    const prod = allMaterials.value.find(m=>m.code===filterProductCode.value)
    if (!prod) { headers.value = []; return }
    headers.value = await bomApi.byProduct(prod.id, { version: filterVersion.value || undefined, activeOnly: filterActiveOnly.value })
  } catch (e) { console.error(e) }
}

async function selectHeader(row: BomHeader) {
  try {
    current.value = row
    const detail = await bomApi.detail(row.id)
    // 通过物料列表补充编码与名称
    const mats = await materialApi.list()
    items.value = (detail.items || []).map((it:any)=>{
      const m = mats.find(mm => String(mm.id) === String(it.material_id))
      return {
        ...it,
        material_code: m?.code || '',
        material_name: m?.name || ''
      }
    })
  } catch (error) {
    console.error('加载BOM明细失败:', error)
  }
}

function openHeader() {
  headerForm.value = { code: '', name: '', productCode: '', version: '1.0', is_active: true }
  dlgHeader.value = true
}

async function saveHeader() {
  try {
    // 将产品编码映射为产品ID
    const prod = allMaterials.value.find(m => m.code === headerForm.value.productCode)
    if (!prod) throw new Error('未找到对应的成品物料，请先在物料中创建')
    const payload = {
      code: headerForm.value.code,
      name: headerForm.value.name,
      product_id: Number(prod.id),
      version: headerForm.value.version,
      is_active: headerForm.value.is_active ? 1 : 0,
      quantity: 1,
      items: []
    }
    if (!payload.code || !payload.name) throw new Error('请填写BOM编码与名称')
    const h = await bomApi.create(payload)
    current.value = h
    await applyFilter()
    dlgHeader.value = false
  } catch (error) {
    console.error('保存BOM头失败:', error)
  }
}

async function addItem() {
  if (!current.value) return
  // 加载有库存的物料（按物料汇总）
  try {
    const resp = await http.get('/inventory/summary/by-material')
    stockedMaterials.value = (resp.data || []).filter((r: any) => r.total_available > 0)
  } catch (e) { console.error(e) }
  itemForm.value = { materialCode: '', qty: 1, scrapRate: 0 }
  dlgItem.value = true
}

async function saveItem() {
  try {
    if (!current.value) throw new Error('请先选择要新增行的BOM')
    const detail = await bomApi.detail(current.value!.id)
    // 将选择的物料编码映射为 material_id
    const mat = allMaterials.value.find(m => m.code === itemForm.value.materialCode)
    if (!mat) throw new Error('未找到该物料，请检查物料编码')
    const newItem = {
      material_id: Number(mat.id),
      quantity: Number(itemForm.value.qty || 0),
      sequence: (detail.items?.length || 0) + 1,
      scrap_rate: Number(itemForm.value.scrapRate || 0)
    }
    const payload = { items: [...(detail.items || []).map((it: any) => ({ material_id: it.material_id, quantity: it.quantity, sequence: it.sequence, scrap_rate: it.scrap_rate })), newItem] }
    await bomApi.update(current.value!.id, payload)
    const latest = await bomApi.detail(current.value!.id)
    const mats = await materialApi.list()
    items.value = (latest.items || []).map((it:any)=>{
      const m = mats.find(mm => String(mm.id) === String(it.material_id))
      return { ...it, material_code: m?.code || '', material_name: m?.name || '' }
    })
    dlgItem.value = false
  } catch (error) {
    console.error('保存BOM明细失败:', error)
  }
}

onMounted(() => { load() })
</script>

<style scoped>
.head{display:flex;align-items:center;justify-content:space-between}
</style>
