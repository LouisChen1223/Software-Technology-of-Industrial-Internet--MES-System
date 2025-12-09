# MES API 使用指南

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_db.py
```

### 3. 启动服务

```bash
python run.py
# 或
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 模块说明

### 基础主数据 API

#### 单位管理
- `POST /api/v1/uoms` - 创建单位
- `GET /api/v1/uoms` - 获取单位列表
- `GET /api/v1/uoms/{id}` - 获取单位详情
- `PUT /api/v1/uoms/{id}` - 更新单位
- `DELETE /api/v1/uoms/{id}` - 删除单位

#### 仓库管理
- `POST /api/v1/warehouses` - 创建仓库
- `GET /api/v1/warehouses` - 获取仓库列表
- `GET /api/v1/warehouses/{id}` - 获取仓库详情
- `PUT /api/v1/warehouses/{id}` - 更新仓库
- `DELETE /api/v1/warehouses/{id}` - 删除仓库

#### 物料管理
- `POST /api/v1/materials` - 创建物料
- `GET /api/v1/materials` - 获取物料列表（支持按类型筛选）
- `GET /api/v1/materials/{id}` - 获取物料详情
- `PUT /api/v1/materials/{id}` - 更新物料
- `DELETE /api/v1/materials/{id}` - 删除物料

#### BOM 管理
- `POST /api/v1/boms` - 创建 BOM（含明细）
- `GET /api/v1/boms` - 获取 BOM 列表
- `GET /api/v1/boms/{id}` - 获取 BOM 详情
- `PUT /api/v1/boms/{id}` - 更新 BOM（含明细）
- `DELETE /api/v1/boms/{id}` - 删除 BOM

#### 工序管理
- `POST /api/v1/operations` - 创建工序
- `GET /api/v1/operations` - 获取工序列表
- `GET /api/v1/operations/{id}` - 获取工序详情
- `PUT /api/v1/operations/{id}` - 更新工序
- `DELETE /api/v1/operations/{id}` - 删除工序

#### 设备管理
- `POST /api/v1/equipment` - 创建设备
- `GET /api/v1/equipment` - 获取设备列表
- `GET /api/v1/equipment/{id}` - 获取设备详情
- `PUT /api/v1/equipment/{id}` - 更新设备
- `DELETE /api/v1/equipment/{id}` - 删除设备

#### 工装管理
- `POST /api/v1/tooling` - 创建工装
- `GET /api/v1/tooling` - 获取工装列表
- `GET /api/v1/tooling/{id}` - 获取工装详情
- `PUT /api/v1/tooling/{id}` - 更新工装
- `DELETE /api/v1/tooling/{id}` - 删除工装

#### 人员管理
- `POST /api/v1/personnel` - 创建人员
- `GET /api/v1/personnel` - 获取人员列表
- `GET /api/v1/personnel/{id}` - 获取人员详情
- `PUT /api/v1/personnel/{id}` - 更新人员
- `DELETE /api/v1/personnel/{id}` - 删除人员

#### 班次管理
- `POST /api/v1/shifts` - 创建班次
- `GET /api/v1/shifts` - 获取班次列表
- `GET /api/v1/shifts/{id}` - 获取班次详情
- `PUT /api/v1/shifts/{id}` - 更新班次
- `DELETE /api/v1/shifts/{id}` - 删除班次

#### 工艺路线管理
- `POST /api/v1/routings` - 创建工艺路线（含明细）
- `GET /api/v1/routings` - 获取工艺路线列表
- `GET /api/v1/routings/{id}` - 获取工艺路线详情
- `PUT /api/v1/routings/{id}` - 更新工艺路线（含明细）
- `DELETE /api/v1/routings/{id}` - 删除工艺路线

### 工单管理 API

#### 工单基础操作
- `POST /api/v1/work-orders` - 创建工单
- `GET /api/v1/work-orders` - 获取工单列表（支持按状态筛选）
- `GET /api/v1/work-orders/{id}` - 获取工单详情
- `PUT /api/v1/work-orders/{id}` - 更新工单
- `DELETE /api/v1/work-orders/{id}` - 删除工单

#### 工单状态操作
- `POST /api/v1/work-orders/{id}/release` - 下达工单
- `POST /api/v1/work-orders/{id}/start` - 开始工单
- `POST /api/v1/work-orders/{id}/complete` - 完成工单
- `POST /api/v1/work-orders/{id}/cancel` - 取消工单

#### 报工管理
- `POST /api/v1/work-reports` - 创建报工记录（扫码报工）
- `GET /api/v1/work-reports` - 获取报工记录列表
- `GET /api/v1/work-reports/{id}` - 获取报工记录详情

#### 在制品管理
- `POST /api/v1/wip-tracking` - 创建在制品记录
- `GET /api/v1/wip-tracking` - 获取在制品列表
- `GET /api/v1/wip-tracking/{id}` - 获取在制品详情
- `PUT /api/v1/wip-tracking/{id}` - 更新在制品
- `GET /api/v1/wip-tracking/batch/{batch_number}` - 按批次号追溯
- `GET /api/v1/wip-tracking/serial/{serial_number}` - 按序列号追溯

### 物料仓储管理 API

#### 库存管理
- `POST /api/v1/inventory` - 创建库存记录
- `GET /api/v1/inventory` - 查询库存（支持多条件筛选）
- `GET /api/v1/inventory/{id}` - 获取库存详情
- `PUT /api/v1/inventory/{id}` - 更新库存
- `GET /api/v1/inventory/summary/by-warehouse` - 按仓库汇总库存
- `GET /api/v1/inventory/summary/by-material` - 按物料汇总库存

#### 物料事务
- `POST /api/v1/material-transactions` - 创建物料事务
- `GET /api/v1/material-transactions` - 获取物料事务列表

#### 领料管理
- `POST /api/v1/material-picks` - 创建领料单
- `GET /api/v1/material-picks` - 获取领料单列表
- `GET /api/v1/material-picks/{id}` - 获取领料单详情
- `PUT /api/v1/material-picks/{id}` - 更新领料单
- `POST /api/v1/material-picks/{id}/confirm` - 确认领料单
- `POST /api/v1/material-picks/{id}/complete` - 完成领料（实际出库）
- `POST /api/v1/material-picks/bom` - 按 BOM 自动生成领料单

#### 退料管理
- `POST /api/v1/material-returns` - 退料

## 使用示例

### 1. 创建工单

```bash
curl -X POST "http://localhost:8000/api/v1/work-orders" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "WO20241208001",
    "product_id": 6,
    "bom_id": 1,
    "routing_id": 1,
    "planned_quantity": 10,
    "priority": 5,
    "customer": "客户A",
    "sales_order": "SO20241208001"
  }'
```

### 2. 下达工单

```bash
curl -X POST "http://localhost:8000/api/v1/work-orders/1/release"
```

### 3. 扫码报工

```bash
curl -X POST "http://localhost:8000/api/v1/work-reports" \
  -H "Content-Type: application/json" \
  -d '{
    "work_order_id": 1,
    "work_order_operation_id": 1,
    "report_type": "start",
    "operator_id": 1,
    "equipment_id": 1,
    "shift_id": 1,
    "barcode": "WO20241208001-OP01"
  }'
```

### 4. 按 BOM 生成领料单

```bash
curl -X POST "http://localhost:8000/api/v1/material-picks/bom?work_order_id=1&warehouse_id=1"
```

### 5. 查询库存

```bash
curl -X GET "http://localhost:8000/api/v1/inventory?warehouse_id=1&material_id=1"
```

### 6. 在制品追溯

```bash
# 按批次号追溯
curl -X GET "http://localhost:8000/api/v1/wip-tracking/batch/B20240101"

# 按序列号追溯
curl -X GET "http://localhost:8000/api/v1/wip-tracking/serial/SN20240101001"
```

## 业务流程示例

### 完整的生产流程

1. **准备主数据**
   - 创建物料、BOM、工艺路线等基础数据

2. **创建工单**
   ```
   POST /api/v1/work-orders
   ```

3. **按 BOM 生成领料单**
   ```
   POST /api/v1/material-picks/bom
   ```

4. **确认并完成领料**
   ```
   POST /api/v1/material-picks/{id}/confirm
   POST /api/v1/material-picks/{id}/complete
   ```

5. **下达工单**
   ```
   POST /api/v1/work-orders/{id}/release
   ```

6. **扫码开工**
   ```
   POST /api/v1/work-reports
   {
     "report_type": "start",
     ...
   }
   ```

7. **扫码完工**
   ```
   POST /api/v1/work-reports
   {
     "report_type": "complete",
     "quantity": 10,
     ...
   }
   ```

8. **完成工单**
   ```
   POST /api/v1/work-orders/{id}/complete
   ```

9. **追溯查询**
   ```
   GET /api/v1/wip-tracking?work_order_id={id}
   ```

## 错误处理

API 使用标准的 HTTP 状态码：

- `200` - 成功
- `201` - 创建成功
- `400` - 请求参数错误
- `404` - 资源不存在
- `500` - 服务器错误

错误响应格式：
```json
{
  "detail": "错误信息描述"
}
```

## 数据库管理

### 初始化数据库（含示例数据）
```bash
python init_db.py
```

### 清空数据库
```bash
python drop_db.py
```

## 开发提示

1. 所有日期时间字段使用 ISO 8601 格式
2. 分页参数：`skip` 和 `limit`
3. 筛选参数直接作为查询参数传递
4. 使用 Swagger UI 进行交互式测试
5. 查看 `DATABASE_DESIGN.md` 了解数据库设计详情
