# MES Backend API

基于 FastAPI 的 MES（制造执行系统）后端实现

## 功能模块

### 题目1：生产订单与物流管理

1. **基础主数据管理**
   - 物料管理
   - BOM（物料清单）管理
   - 工艺路线管理
   - 工序管理
   - 设备管理
   - 工装管理
   - 人员管理
   - 班次管理
   - 单位管理
   - 仓库管理

2. **工单管理**
   - 工单创建/编辑/删除
   - 工单下达
   - 工单排程
   - 工单执行
   - 扫码报工（开工/完工/暂停/报废）

3. **物料仓储管理**
   - 领料（普通领料、按BOM领料）
   - 退料
   - 发料补料
   - 物料库存查询

4. **在制品与追溯**
   - WIP在制品查询
   - 物料正反向追溯
   - 工序追溯

## 技术栈

- Python 3.9+
- FastAPI
- SQLAlchemy 2.0
- Pydantic
- Uvicorn

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置

### 4. 初始化数据库

```bash
python init_db.py
```

### 5. 运行服务

```bash
python run.py
```

### 6. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── models/              # SQLAlchemy 模型
│   ├── schemas/             # Pydantic 模式
│   ├── api/                 # API 路由
│   ├── services/            # 业务逻辑
│   └── utils/               # 工具函数
├── requirements.txt
├── .env
└── README.md
```

## API 接口文档

详见 Swagger 文档: http://localhost:8000/docs
