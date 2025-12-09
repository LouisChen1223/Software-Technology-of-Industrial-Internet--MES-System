import { createRouter, createWebHistory } from 'vue-router'

const WorkOrderList = () => import('@/views/WorkOrderList.vue')
const WorkstationHMI = () => import('@/views/WorkstationHMI.vue')
const WIPBoard = () => import('@/views/WIPBoard.vue')
const Inventory = () => import('@/views/Inventory.vue')
// master data
const Materials = () => import('@/views/master/Materials.vue')
const BOMList = () => import('@/views/master/BOMList.vue')
const RoutingList = () => import('@/views/master/RoutingList.vue')
const Operations = () => import('@/views/master/Operations.vue')
const EquipmentList = () => import('@/views/master/EquipmentList.vue')
const ToolingList = () => import('@/views/master/ToolingList.vue')
const PersonnelList = () => import('@/views/master/PersonnelList.vue')
const Shifts = () => import('@/views/master/Shifts.vue')
const Warehouses = () => import('@/views/master/Warehouses.vue')
const Uoms = () => import('@/views/master/Uoms.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/work-orders' },
    { path: '/work-orders', component: WorkOrderList },
    { path: '/hmi', component: WorkstationHMI },
    { path: '/wip', component: WIPBoard },
    { path: '/inventory', component: Inventory },
    {
      path: '/master',
      children: [
        { path: 'materials', component: Materials },
        { path: 'bom', component: BOMList },
        { path: 'routing', component: RoutingList },
        { path: 'operations', component: Operations },
        { path: 'equipment', component: EquipmentList },
        { path: 'tooling', component: ToolingList },
        { path: 'personnel', component: PersonnelList },
        { path: 'shifts', component: Shifts },
        { path: 'warehouses', component: Warehouses },
        { path: 'uoms', component: Uoms }
      ]
    }
  ]
})

export default router
