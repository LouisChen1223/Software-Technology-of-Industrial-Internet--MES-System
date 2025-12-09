# MES 系统 - 数据库设计文档

## 数据库架构概览

本 MES 系统采用关系型数据库设计，包含以下主要模块：

### 1. 基础主数据模块

#### 1.1 单位表 (uoms)
存储计量单位信息
- id: 主键
- code: 单位编码（唯一）
- name: 单位名称
- description: 描述
- created_at, updated_at: 时间戳

#### 1.2 仓库表 (warehouses)
存储仓库信息
- id: 主键
- code: 仓库编码（唯一）
- name: 仓库名称
- location: 位置
- warehouse_type: 仓库类型（原料仓、成品仓、在制品仓等）
- manager: 负责人
- description: 描述
- created_at, updated_at: 时间戳

#### 1.3 物料表 (materials)
存储物料信息
- id: 主键
- code: 物料编码（唯一）
- name: 物料名称
- specification: 规格
- material_type: 物料类型（原料、半成品、成品等）
- uom_id: 单位ID（外键）
- unit_price: 单价
- safety_stock: 安全库存
- lead_time: 提前期（天）
- supplier: 供应商
- description: 描述
- created_at, updated_at: 时间戳

#### 1.4 BOM 表头 (boms)
存储物料清单表头
- id: 主键
- code: BOM编码（唯一）
- name: BOM名称
- product_id: 产品ID（外键到 materials）
- version: 版本号
- quantity: 产出数量
- is_active: 是否激活
- description: 描述
- created_at, updated_at: 时间戳

#### 1.5 BOM 明细 (bom_items)
存储物料清单明细
- id: 主键
- bom_id: BOM ID（外键）
- material_id: 物料ID（外键）
- quantity: 用量
- sequence: 序号
- scrap_rate: 损耗率
- description: 描述
- created_at: 时间戳

#### 1.6 工序表 (operations)
存储工序信息
- id: 主键
- code: 工序编码（唯一）
- name: 工序名称
- operation_type: 工序类型（加工、装配、检验等）
- standard_time: 标准工时（分钟）
- description: 描述
- created_at, updated_at: 时间戳

#### 1.7 设备表 (equipment)
存储设备信息
- id: 主键
- code: 设备编码（唯一）
- name: 设备名称
- equipment_type: 设备类型
- model: 型号
- manufacturer: 制造商
- capacity: 产能
- status: 状态（idle, running, maintenance, fault）
- location: 位置
- description: 描述
- created_at, updated_at: 时间戳

#### 1.8 工装表 (tooling)
存储工装信息
- id: 主键
- code: 工装编码（唯一）
- name: 工装名称
- tooling_type: 工装类型
- specification: 规格
- quantity: 数量
- status: 状态（available, in-use, maintenance）
- location: 位置
- description: 描述
- created_at, updated_at: 时间戳

#### 1.9 人员表 (personnel)
存储人员信息
- id: 主键
- code: 人员编码（唯一）
- name: 姓名
- department: 部门
- position: 职位
- skill_level: 技能等级
- phone: 电话
- email: 邮箱
- status: 状态（active, inactive）
- created_at, updated_at: 时间戳

#### 1.10 班次表 (shifts)
存储班次信息
- id: 主键
- code: 班次编码（唯一）
- name: 班次名称
- start_time: 开始时间（HH:MM）
- end_time: 结束时间（HH:MM）
- description: 描述
- created_at, updated_at: 时间戳

#### 1.11 工艺路线表头 (routings)
存储工艺路线表头
- id: 主键
- code: 工艺路线编码（唯一）
- name: 工艺路线名称
- product_id: 产品ID（外键到 materials）
- version: 版本号
- is_active: 是否激活
- description: 描述
- created_at, updated_at: 时间戳

#### 1.12 工艺路线明细 (routing_items)
存储工艺路线明细
- id: 主键
- routing_id: 工艺路线ID（外键）
- operation_id: 工序ID（外键）
- sequence: 序号
- equipment_id: 设备ID（外键，可选）
- standard_time: 标准工时（分钟）
- setup_time: 准备时间（分钟）
- description: 描述
- created_at: 时间戳

### 2. 工单管理模块

#### 2.1 工单表 (work_orders)
存储工单信息
- id: 主键
- code: 工单编码（唯一）
- product_id: 产品ID（外键）
- bom_id: BOM ID（外键，可选）
- routing_id: 工艺路线ID（外键，可选）
- planned_quantity: 计划数量
- completed_quantity: 完成数量
- scrapped_quantity: 报废数量
- status: 状态（draft, released, in_progress, paused, completed, cancelled）
- priority: 优先级（1-10）
- planned_start_date: 计划开始日期
- planned_end_date: 计划结束日期
- actual_start_date: 实际开始日期
- actual_end_date: 实际结束日期
- customer: 客户
- sales_order: 销售订单号
- notes: 备注
- created_by: 创建人
- created_at, updated_at: 时间戳

#### 2.2 工单工序表 (work_order_operations)
存储工单工序信息
- id: 主键
- work_order_id: 工单ID（外键）
- operation_id: 工序ID（外键）
- sequence: 序号
- equipment_id: 设备ID（外键，可选）
- planned_quantity: 计划数量
- completed_quantity: 完成数量
- scrapped_quantity: 报废数量
- status: 状态（pending, in_progress, completed）
- planned_start_date: 计划开始日期
- planned_end_date: 计划结束日期
- actual_start_date: 实际开始日期
- actual_end_date: 实际结束日期
- created_at, updated_at: 时间戳

#### 2.3 报工记录表 (work_reports)
存储报工记录（扫码报工）
- id: 主键
- work_order_id: 工单ID（外键）
- work_order_operation_id: 工单工序ID（外键，可选）
- report_type: 报工类型（start, complete, pause, resume, scrap）
- quantity: 数量
- operator_id: 操作员ID（外键，可选）
- equipment_id: 设备ID（外键，可选）
- shift_id: 班次ID（外键，可选）
- barcode: 扫码内容
- notes: 备注
- report_time: 报工时间
- created_at: 时间戳

#### 2.4 在制品追溯表 (wip_tracking)
存储在制品追踪信息
- id: 主键
- work_order_id: 工单ID（外键）
- operation_id: 工序ID（外键）
- material_id: 物料ID（外键）
- batch_number: 批次号
- serial_number: 序列号
- quantity: 数量
- status: 状态（wip, completed, scrapped）
- location: 位置
- operator_id: 操作员ID（外键，可选）
- equipment_id: 设备ID（外键，可选）
- created_at, updated_at: 时间戳

### 3. 物料仓储管理模块

#### 3.1 库存表 (inventory)
存储库存信息
- id: 主键
- warehouse_id: 仓库ID（外键）
- material_id: 物料ID（外键）
- batch_number: 批次号
- quantity: 数量
- available_quantity: 可用数量
- allocated_quantity: 已分配数量
- location: 库位
- unit_price: 单价
- production_date: 生产日期
- expiry_date: 过期日期
- created_at, updated_at: 时间戳

#### 3.2 物料事务表 (material_transactions)
存储物料交易记录
- id: 主键
- transaction_type: 交易类型（pick, return, issue, receive, adjust, transfer）
- material_id: 物料ID（外键）
- warehouse_id: 仓库ID（外键）
- work_order_id: 工单ID（外键，可选）
- batch_number: 批次号
- quantity: 数量
- unit_price: 单价
- from_location: 源位置
- to_location: 目标位置
- operator_id: 操作员ID（外键，可选）
- reference_no: 参考单号
- notes: 备注
- transaction_date: 交易日期
- created_at: 时间戳

#### 3.3 领料单表头 (material_picks)
存储领料单表头
- id: 主键
- code: 领料单号（唯一）
- work_order_id: 工单ID（外键，可选）
- warehouse_id: 仓库ID（外键）
- pick_type: 领料类型（normal, bom）
- status: 状态（draft, confirmed, completed, cancelled）
- requester_id: 申请人ID（外键，可选）
- picker_id: 领料人ID（外键，可选）
- request_date: 申请日期
- pick_date: 领料日期
- notes: 备注
- created_at, updated_at: 时间戳

#### 3.4 领料单明细表 (material_pick_items)
存储领料单明细
- id: 主键
- pick_id: 领料单ID（外键）
- material_id: 物料ID（外键）
- batch_number: 批次号
- required_quantity: 需求数量
- picked_quantity: 领料数量
- location: 库位
- notes: 备注
- created_at: 时间戳

## 关键业务流程

### 1. 工单创建到执行流程
1. 创建工单（draft 状态）
2. 下达工单（released 状态）
3. 开始工单（in_progress 状态）
4. 扫码报工（记录到 work_reports）
5. 完成工单（completed 状态）

### 2. 物料领退料流程
1. 创建领料单（可基于 BOM 自动生成）
2. 确认领料单
3. 执行领料（生成物料事务，更新库存）
4. 如需退料，创建退料事务

### 3. 在制品追溯流程
1. 在报工时创建 WIP 记录
2. 记录批次号/序列号
3. 支持正向追溯（原料 → 成品）
4. 支持反向追溯（成品 → 原料）

## 索引设计

关键字段已添加索引以优化查询性能：
- 所有表的 code 字段（唯一索引）
- 外键字段
- 常用查询字段（如 status, batch_number 等）

## 数据完整性

- 使用外键约束保证引用完整性
- 使用级联删除处理主从表关系
- 使用唯一约束防止重复数据
- 使用默认值保证数据一致性
