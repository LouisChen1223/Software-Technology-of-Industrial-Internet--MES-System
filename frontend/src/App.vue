<template>
  <el-config-provider namespace="el">
    <el-container style="height: 100vh">
      <el-header height="56px" class="app-header">
        <div class="brand">MES 前端 · Vue3</div>
        <div class="spacer"></div>
        <el-button type="primary" link @click="goHome">主页</el-button>
        <el-button link @click="toggleDark">{{ isDark ? '浅色' : '深色' }}</el-button>
      </el-header>
      <el-container>
        <el-aside width="240px" class="app-aside">
          <el-menu :default-active="$route.path" class="el-menu-vertical-demo" router>
            <el-menu-item index="/work-orders">工单台账</el-menu-item>
            <el-menu-item index="/scheduling">排班/排程</el-menu-item>
            <el-menu-item index="/hmi">工位HMI</el-menu-item>
            <el-menu-item index="/wip">WIP看板</el-menu-item>
            <el-menu-item index="/inventory">库存/出入库</el-menu-item>
            <el-sub-menu index="/master">
              <template #title>基础主数据</template>
              <el-sub-menu index="/master/dict">
                <template #title>基础字典</template>
                <el-menu-item index="/master/uoms">计量单位</el-menu-item>
                <el-menu-item index="/master/material-types">物料类型</el-menu-item>
              </el-sub-menu>
              <el-sub-menu index="/master/org">
                <template #title>组织与资源</template>
                <el-menu-item index="/master/departments">部门</el-menu-item>
                <el-menu-item index="/master/workshops">车间</el-menu-item>
                <el-menu-item index="/master/personnel">人员</el-menu-item>
                <el-menu-item index="/master/shifts">班次</el-menu-item>
                <el-menu-item index="/master/equipment">设备</el-menu-item>
                <el-menu-item index="/master/tooling">工装治具</el-menu-item>
                <el-menu-item index="/master/warehouses">仓库</el-menu-item>
              </el-sub-menu>
              <el-sub-menu index="/master/process">
                <template #title>工艺管理</template>
                <el-menu-item index="/master/operations">工序</el-menu-item>
                <el-menu-item index="/master/routing">工艺路线</el-menu-item>
              </el-sub-menu>
              <el-sub-menu index="/master/material">
                <template #title>物料管理</template>
                <el-menu-item index="/master/materials">物料</el-menu-item>
                <el-menu-item index="/master/bom">BOM</el-menu-item>
              </el-sub-menu>
            </el-sub-menu>
          </el-menu>
        </el-aside>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const isDark = ref(false)
const router = useRouter()

function toggleDark() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
}

function goHome() {
  router.push('/work-orders')
}
</script>

<style>
:root.dark {
  filter: invert(1) hue-rotate(180deg);
}
html,
body,
#app {
  margin: 0;
  padding: 0;
  height: 100%;
}
.app-header {
  display: flex;
  align-items: center;
  padding: 0 12px;
  border-bottom: 1px solid #eee;
}
.brand {
  font-weight: 600;
}
.spacer {
  flex: 1;
}
.app-aside {
  border-right: 1px solid #eee;
}
</style>

