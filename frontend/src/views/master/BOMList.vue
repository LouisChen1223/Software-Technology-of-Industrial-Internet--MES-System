<template>
  <el-card>
    <template #header>
      <div class="head">
        <span>BOM 管理</span>
        <el-button type="primary" @click="openHeader">新建BOM</el-button>
      </div>
    </template>
    <el-row :gutter="16">
      <el-col :span="10">
        <el-table :data="headers" height="60vh" @row-click="selectHeader">
          <el-table-column prop="productCode" label="产品编码"/>
          <el-table-column prop="version" label="版本" width="100"/>
          <el-table-column prop="status" label="状态" width="120"/>
        </el-table>
      </el-col>
      <el-col :span="14">
        <el-table :data="items" height="60vh">
          <el-table-column prop="materialCode" label="物料编码"/>
          <el-table-column prop="qty" label="用量" width="100"/>
          <el-table-column prop="scrapRate" label="损耗%" width="100"/>
        </el-table>
        <div style="margin-top:8px">
          <el-button size="small" @click="addItem" :disabled="!current">新增行</el-button>
        </div>
      </el-col>
    </el-row>

    <el-dialog v-model="dlgHeader" title="新建BOM" width="500px">
      <el-form :model="headerForm" label-width="90px">
        <el-form-item label="产品编码"><el-input v-model="headerForm.productCode"/></el-form-item>
        <el-form-item label="产品名称"><el-input v-model="headerForm.productName"/></el-form-item>
        <el-form-item label="版本"><el-input v-model="headerForm.version"/></el-form-item>
        <el-form-item label="状态"><el-select v-model="headerForm.status"><el-option value="draft"/><el-option value="released"/></el-select></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlgHeader=false">取消</el-button>
        <el-button type="primary" @click="saveHeader">保存</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="dlgItem" title="新增BOM行" width="480px">
      <el-form :model="itemForm" label-width="90px">
        <el-form-item label="物料编码"><el-input v-model="itemForm.materialCode"/></el-form-item>
        <el-form-item label="物料名称"><el-input v-model="itemForm.materialName"/></el-form-item>
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
import type { BomHeader, BomItem } from '@/types/master'
import { bomApi } from '@/api/masterData'

const headers = ref<BomHeader[]>([])
const items = ref<BomItem[]>([])
const current = ref<BomHeader | null>(null)

const dlgHeader = ref(false)
const headerForm = ref<Partial<BomHeader>>({ status: 'draft', version: 'A' })

const dlgItem = ref(false)
const itemForm = ref<Partial<BomItem>>({ qty: 1, scrapRate: 0 })

async function load() {
  try {
    headers.value = await bomApi.headers()
    if (current.value) {
      items.value = await bomApi.items(current.value.id)
    }
  } catch (error) {
    console.error('加载BOM失败:', error)
  }
}

async function selectHeader(row: BomHeader) {
  try {
    current.value = row
    items.value = await bomApi.items(row.id)
  } catch (error) {
    console.error('加载BOM明细失败:', error)
  }
}

function openHeader() {
  headerForm.value = { status: 'draft', version: 'A' } as any
  dlgHeader.value = true
}

async function saveHeader() {
  try {
    const h = await bomApi.createHeader(headerForm.value as any)
    current.value = h
    await load()
    dlgHeader.value = false
  } catch (error) {
    console.error('保存BOM头失败:', error)
  }
}

function addItem() {
  if (!current.value) return
  itemForm.value = { bomId: current.value.id, qty: 1, scrapRate: 0 } as any
  dlgItem.value = true
}

async function saveItem() {
  try {
    await bomApi.addItem(current.value!.id, itemForm.value as any)
    items.value = await bomApi.items(current.value!.id)
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
