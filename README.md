# DRG 分组服务

DRG（Diagnosis Related Groups）疾病诊断相关分组工具，包含前后端完整实现。

## 项目结构

```
drg-project/
├── frontend/         # Vue 3 前端应用
│   ├── src/         # 源代码
│   │   ├── components/  # Vue 组件
│   │   ├── views/       # 页面视图
│   │   ├── router/      # 路由配置
│   │   ├── stores/      # Pinia 状态管理
│   │   └── services/    # API 服务
│   ├── public/      # 静态资源
│   └── package.json # 前端依赖配置
├── backend/         # FastAPI 后端服务
│   ├── app/         # 应用源代码
│   │   ├── api/     # API 路由
│   │   ├── models/  # 数据模型
│   │   ├── services/ # 业务逻辑
│   │   └── utils/   # 工具函数
│   ├── run.py       # 启动脚本
│   └── test.py      # 测试文件
└── engine/          # DRG 分组引擎
    ├── ruzu.py      # 核心分组逻辑
    ├── GET_*.py     # PDF 解析工具
    └── *.json       # 分组规则数据
```

## 技术栈

### 前端
- **框架**: Vue 3
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP 客户端**: Axios

### 后端
- **框架**: FastAPI
- **编程语言**: Python
- **API 文档**: 自动生成的 OpenAPI/Swagger 文档

### 引擎
- **PDF 解析**: pdfplumber
- **数据格式**: JSON

## 功能特性

- DRG 疾病诊断相关分组
- RESTful API 接口
- CORS 跨域支持
- 实时分组服务
- 响应式前端界面
- PDF 分组规则解析工具

## API 端点

- `GET /` - 服务状态检查
- `POST /api/group` - DRG 分组接口

## 使用说明

### 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 启动后端服务

```bash
cd backend
python run.py
```

### 安装引擎依赖

```bash
cd engine
pip install -r requirements.txt
```

### 安装前端依赖

```bash
cd frontend
npm install
```

### 启动前端开发服务器

```bash
cd frontend
npm run dev
```

### 访问应用

- **前端界面**: `http://localhost:5173`
- **后端 API 文档**: `http://localhost:8000/docs`

## 开发环境

### 后端
- Python 虚拟环境位于 `backend/.venv/`
- 依赖包已预装在虚拟环境中
- 主要依赖：
  - fastapi==0.104.1
  - uvicorn==0.24.0
  - python-multipart==0.0.6

### 引擎
- 使用 Python 标准库（json, re, typing）
- 第三方库：pdfplumber（用于解析 PDF 分组规则）

### 前端
- Node.js 版本要求：^20.19.0 || >=22.12.0
- 依赖包通过 `npm install` 安装

## 许可证

本项目仅供学习和研究使用。
