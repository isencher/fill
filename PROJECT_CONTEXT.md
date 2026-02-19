# Fill 项目完整上下文

**重要提示**: 本文档提供了 Fill 项目的完整上下文信息。在 Windows/Linux/macOS 任何环境下进行开发、测试或修改之前，**请务必完整阅读本文档**，避免创建简化版本。

---

## 项目概述

### 核心定位
Fill 是一个**智能表格数据自动填充 Web 应用**，用于将 Excel/CSV 数据批量填充到 Word/Excel 模板中。

### 目标用户
- 需要批量生成文档的企业（发票、合同、报告等）
- HR 部门（员工信息录入）
- 销售团队（客户资料生成）
- 行政人员（表单自动填写）

### 核心价值
1. **自动化**: 替代手动复制粘贴，节省 90% 时间
2. **智能化**: 自动字段映射，模糊匹配
3. **可靠性**: 完整的错误处理和验证
4. **易用性**: 简单的 Web 界面，无需编程

---

## 完整功能清单

### 必须保留的核心功能 ⚠️

#### 1. 文件上传模块
- [x] 支持 CSV 文件上传
- [x] 支持 Excel (.xlsx) 文件上传
- [x] 文件类型验证（仅限 .csv, .xlsx）
- [x] 文件大小限制（10MB）
- [x] 文件存储（内存 + 数据库持久化）
- [x] 数据预览（前 5 行）
- [x] 上传进度显示
- [x] 拖拽上传支持
- [x] 错误提示

#### 2. 模板管理模块
- [x] 内置模板示例（发票、合同、通知）
- [x] 自定义模板上传（.docx, .xlsx, .txt）
- [x] 模板预览
- [x] 模板占位符识别（{{字段名}}）
- [x] 模板列表展示
- [x] 模板删除功能
- [x] 模板文件存储

#### 3. 字段映射模块 ⭐ 核心功能
- [x] 文件列自动识别
- [x] 模板占位符自动识别
- [x] 智能字段匹配（模糊匹配算法）
- [x] 置信度显示（高/中/低）
- [x] 手动映射调整
- [x] 映射预览
- [x] 数据预览（前 5 行）
- [x] 映射验证
- [x] 一键自动匹配

#### 4. 批量处理模块
- [x] 逐行数据处理
- [x] 模板填充（Word/Excel）
- [x] 错误处理（跳过错误行）
- [x] 进度追踪
- [x] 成功/失败统计
- [x] 批量下载（ZIP）
- [x] 单个文件下载

#### 5. API 端点（完整版）

**基础端点**:
```
GET  /                          - 健康检查
GET  /docs                      - Swagger UI
GET  /redoc                     - ReDoc 文档
GET  /openapi.json              - OpenAPI 规范
```

**文件管理**:
```
POST /api/v1/upload             - 文件上传
GET  /api/v1/files              - 文件列表
GET  /api/v1/files/{id}         - 文件详情
DELETE /api/v1/files/{id}       - 删除文件
```

**模板管理**:
```
GET  /api/v1/templates          - 模板列表
GET  /api/v1/templates/{id}     - 模板详情
POST /api/v1/templates          - 上传模板
DELETE /api/v1/templates/{id}   - 删除模板
GET  /api/v1/templates/built-in - 内置模板列表
```

**字段映射**:
```
POST /api/v1/parse              - 解析上传文件
POST /api/v1/mappings           - 创建字段映射
POST /api/v1/suggest-mapping    - 智能映射建议
GET  /api/v1/mappings/{id}      - 获取映射详情
```

**批量处理**:
```
POST /api/v1/jobs               - 创建批处理任务
GET  /api/v1/jobs               - 任务列表
GET  /api/v1/jobs/{id}          - 任务详情
GET  /api/v1/jobs/{id}/progress - 任务进度
GET  /api/v1/jobs/{id}/outputs  - 任务输出文件
GET  /api/v1/outputs/{id}/download - 下载单个输出
```

**模板页面**:
```
GET  /templates.html            - 模板选择页面 (需要 ?file_id=)
GET  /mapping.html              - 字段映射页面 (需要 ?file_id=&template_id=)
GET  /processing.html           - 处理进度页面 (需要 ?job_id=)
```

#### 6. 用户界面（完整版）
- [x] 上传页面 (`/` 或 `/index.html`)
  - 拖拽上传区域
  - 文件类型选择
  - 上传按钮
  - 数据预览区域
  - "选择模板"按钮

- [x] 模板选择页面 (`/templates.html`)
  - 模板卡片展示
  - 内置模板列表
  - 自定义模板上传
  - 模板预览
  - "使用此模板"按钮

- [x] 字段映射页面 (`/mapping.html`)
  - 数据列展示
  - 模板占位符展示
  - 智能匹配结果
  - 置信度指示器
  - 手动下拉选择
  - 数据预览表格
  - "确认生成"按钮
  - "取消"按钮

- [x] 处理进度页面 (`/processing.html`)
  - 进度条
  - 当前处理状态
  - 成功/失败统计
  - 完成后下载按钮

#### 7. 高级功能
- [x] 首次用户引导（Onboarding）
- [x] 响应式设计（移动端支持）
- [x] 无障碍支持（WCAG AA）
- [x] 键盘导航
- [x] 错误恢复机制
- [x] 撤销/重做功能
- [x] 性能优化（懒加载）
- [x] Service Worker（离线支持）
- [x] 数据验证
- [x] 并发处理支持

#### 8. 数据库功能
- [x] SQLite 持久化
- [x] 文件元数据存储
- [x] 模板元数据存储
- [x] 映射配置存储
- [x] 任务状态存储
- [x] Alembic 迁移支持
- [x] 数据库清理机制

---

## 技术栈

### 后端
```
Python 3.11+
FastAPI          - Web 框架
SQLAlchemy 2.x   - ORM
Alembic          - 数据库迁移
Pydantic v2      - 数据验证
pytest           - 测试框架
```

### 前端
```
原生 JavaScript (ES6+)  - 无框架依赖
HTML5                 - 页面结构
CSS3                  - 样式（Grid/Flexbox）
CSS Grid              - 响应式布局
A11y                  - 无障碍支持
```

### 数据处理
```
openpyxl     - Excel 读写
python-docx  - Word 文档生成
pandas       - 数据处理（可选）
```

### 数据库
```
SQLite 3     - 开发/测试环境
PostgreSQL   - 生产环境（可选）
```

### 测试
```
pytest            - 单元测试
pytest-playwright - E2E 测试
FastAPI TestClient - API 测试
```

---

## 项目目录结构

```
fill/
├── src/
│   ├── main.py                      # FastAPI 应用入口（⚠️ 必须保留所有端点）
│   ├── models/                      # 数据模型
│   │   ├── file.py                 # 文件模型
│   │   ├── template.py             # 模板模型
│   │   ├── mapping.py              # 映射模型
│   │   └── job.py                  # 任务模型
│   ├── repositories/               # 数据访问层
│   │   ├── database.py             # 数据库管理
│   │   ├── file_repository.py      # 文件仓储
│   │   ├── template_repository.py  # 模板仓储
│   │   ├── mapping_repository.py   # 映射仓储
│   │   └── job_repository.py       # 任务仓储
│   ├── services/                   # 业务逻辑层
│   │   ├── file_storage.py         # 文件存储服务
│   │   ├── csv_parser.py           # CSV 解析器
│   │   ├── excel_parser.py         # Excel 解析器
│   │   ├── docx_generator.py       # Word 文档生成器
│   │   ├── excel_template_filler.py # Excel 填充器
│   │   ├── batch_processor.py      # 批量处理器
│   │   ├── output_storage.py       # 输出文件存储
│   │   ├── fuzzy_matcher.py        # 模糊匹配算法
│   │   ├── mapping_validator.py    # 映射验证器
│   │   ├── placeholder_parser.py   # 占位符解析器
│   │   ├── template_store.py       # 模板存储
│   │   └── template_filler.py      # 模板填充器
│   ├── core/                       # 核心功能
│   │   └── processor.py            # 数据处理器
│   ├── utils/                      # 工具函数
│   │   └── helpers.py              # 辅助函数
│   └── static/                     # 前端静态文件
│       ├── index.html              # 主页（上传页面）
│       ├── upload.js               # 上传逻辑
│       ├── templates.html          # 模板选择页面
│       ├── templates.js            # 模板选择逻辑
│       ├── mapping.html            # 字段映射页面
│       ├── mapping.js              # 映射配置逻辑
│       ├── processing.html         # 处理进度页面
│       ├── components/             # UI 组件
│       │   ├── a11y-utils.js       # 无障碍工具
│       │   ├── a11y.css            # 无障碍样式
│       │   ├── keyboard-nav.js     # 键盘导航
│       │   ├── animations.css      # 动画样式
│       │   ├── error-recovery.js   # 错误恢复
│       │   ├── performance-utils.js # 性能优化
│       │   ├── progress.css        # 进度条样式
│       │   ├── progress.js         # 进度条逻辑
│       │   └── ...                 # 其他组件
│       └── samples/                # 示例文件
│           └── sample-customer-data.csv
├── tests/                          # 测试套件
│   ├── unit/                       # 单元测试（~700 个）
│   ├── integration/                # 集成测试（~88 个）
│   ├── e2e/                        # E2E 测试（~470 个）
│   │   ├── test_docs_endpoint.py   # API 文档测试
│   │   ├── test_upload_page.py     # 上传页面测试
│   │   ├── test_mapping_page.py    # 映射页面测试
│   │   ├── test_accessibility.py   # 无障碍测试
│   │   ├── test_complete_workflow.py # 完整工作流测试
│   │   └── ...                     # 其他 E2E 测试
│   └── conftest.py                 # pytest 配置
├── migrations/                     # Alembic 迁移
│   └── alembic.ini
├── data/                           # 数据文件
│   └── fill.db                     # SQLite 数据库
├── pyproject.toml                  # 项目配置
├── requirements.txt                # Python 依赖
├── README.md                       # 项目说明
├── TEST_REPORT.md                  # 测试报告
└── BETA_FEEDBACK.md                # Beta 反馈文档
```

---

## 关键设计决策 ⚠️ 必须遵守

### 1. 架构模式
**分层架构**（不要简化）：
```
API 层 (FastAPI 路由)
    ↓
业务逻辑层 (Services)
    ↓
数据访问层 (Repositories)
    ↓
数据模型层 (Models)
```

**为什么**: 这种架构提供了清晰的关注点分离，便于测试和维护。

### 2. 数据流
**完整的工作流**（不要跳过步骤）：
```
1. 用户上传 CSV/Excel 文件
2. 系统解析文件，提取列名和数据预览
3. 用户选择模板（内置或自定义）
4. 系统显示字段映射界面（自动匹配 + 手动调整）
5. 用户确认映射
6. 系统批量处理数据，生成文档
7. 用户下载生成的文档（ZIP 或单个文件）
```

**为什么**: 每个步骤都有其目的，跳过会破坏用户体验。

### 3. 错误处理策略
**多层错误处理**（不要移除）：
```python
# API 层错误处理
try:
    result = service.process(data)
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
except ProcessingError as e:
    raise HTTPException(status_code=500, detail=str(e))

# Service 层错误处理
try:
    result = repository.save(data)
except DatabaseError as e:
    log.error(f"Database error: {e}")
    raise ProcessingError("Failed to save data")
```

**为什么**: 错误处理是生产环境的关键。

### 4. 测试策略
**三层测试**（不要只运行 E2E 测试）：
```
单元测试     - 测试单个函数/类
集成测试     - 测试 API 端点 + 数据库
E2E 测试      - 测试完整用户流程
```

**为什么**: 每层测试捕获不同类型的问题。

### 5. 前端架构
**纯 JavaScript**（不要引入框架）：
- 无 React/Vue/Angular
- 使用原生 ES6+ JavaScript
- 模块化组件（但不是框架组件）
- 渐进式增强

**为什么**: 保持轻量级，易于部署。

---

## 常见陷阱 ⚠️

### 陷阱 1: 简化 main.py
**错误做法**:
```python
# ❌ 只保留基本端点
@app.post("/upload")
async def upload(file):
    return {"status": "ok"}
```

**正确做法**:
```python
# ✅ 保留所有端点
@app.post("/api/v1/upload")
@app.get("/api/v1/files")
@app.post("/api/v1/parse")
@app.post("/api/v1/mappings")
@app.post("/api/v1/suggest-mapping")
@app.post("/api/v1/jobs")
# ... 所有其他端点
```

### 陷阱 2: 删除测试文件
**错误做法**:
```bash
# ❌ 删除"不需要"的测试
rm tests/e2e/test_docs_playwright.py
rm tests/e2e/test_workflow_fixes.py
```

**正确做法**:
```bash
# ✅ 保留所有测试，标记 xfail 如果需要
pytest tests/e2e/test_docs_playwright.py -v
```

### 陷阱 3: 忽略数据库层
**错误做法**:
```python
# ❌ 只使用内存存储
_uploaded_files = {}
```

**正确做法**:
```python
# ✅ 使用数据库持久化
from src.repositories.database import get_db_manager
db_manager = get_db_manager()
with db_manager.get_session() as db:
    file = FileModel(...)
    db.add(file)
    db.commit()
```

### 陷阱 4: 跳过字段映射
**错误做法**:
```python
# ❌ 直接处理，跳过映射步骤
@app.post("/process")
async def process(file_id):
    # 直接生成，没有用户确认
    return generate_documents(file_id)
```

**正确做法**:
```python
# ✅ 完整的映射流程
@app.post("/api/v1/parse")
async def parse_file(file_id): ...

@app.post("/api/v1/suggest-mapping")
async def suggest_mapping(file_id, template_id): ...

@app.post("/api/v1/mappings")
async def create_mapping(mapping): ...

@app.post("/api/v1/jobs")
async def create_job(mapping_id): ...
```

### 陷阱 5: 移除前端页面
**错误做法**:
```python
# ❌ 只保留 index.html
# 删除 templates.html, mapping.html, processing.html
```

**正确做法**:
```python
# ✅ 保留所有页面
/static/index.html         - 上传页面
/static/templates.html     - 模板选择
/static/mapping.html       - 字段映射
/static/processing.html    - 处理进度
```

---

## 开发规范

### Git 提交规范
```bash
# 使用 Conventional Commits
feat: add new feature
fix: fix bug
docs: update documentation
test: add tests
refactor: code refactoring
chore: maintenance tasks
```

### 代码风格
```python
# 遵循 PEP 8
# 使用类型注解
def process_file(file_id: UUID) -> ProcessResult:
    ...
```

### 测试规范
```python
# 每个 API 端点都要有测试
def test_upload_endpoint():
    response = client.post("/api/v1/upload", ...)
    assert response.status_code == 201

# 每个服务函数都要有单元测试
def test_csv_parser():
    parser = CSVParser()
    result = parser.parse("file.csv")
    assert len(result.columns) > 0
```

---

## 重要文件清单 ⚠️

### 必须保留的文件

**核心代码**（不要删除或简化）:
```
src/main.py                     # FastAPI 应用（所有端点）
src/models/*.py                 # 所有数据模型
src/repositories/*.py           # 所有仓储
src/services/*.py               # 所有服务
src/core/processor.py           # 核心处理器
```

**前端页面**（不要删除）:
```
src/static/index.html           # 上传页面
src/static/templates.html       # 模板选择
src/static/mapping.html         # 字段映射
src/static/processing.html      # 处理进度
src/static/*.js                 # 所有 JavaScript
src/static/components/*.js      # 所有组件
```

**测试文件**（不要删除）:
```
tests/unit/*.py                 # 所有单元测试
tests/integration/*.py          # 所有集成测试
tests/e2e/*.py                  # 所有 E2E 测试
```

**配置文件**（不要修改）:
```
pyproject.toml                  # pytest 配置
requirements.txt                # Python 依赖
alembic.ini                     # 数据库迁移
migrations/versions/*.py        # 迁移脚本
```

---

## 测试覆盖率目标

### 当前覆盖率: 88.46%
```
总体目标: ≥85%
Repository 层: ≥90%
Service 层: ≥85%
Model 层: ≥90%
```

### 需要关注的模块
```
src/main.py                          - 72.82% (需要提升)
src/services/excel_template_filler.py - 79.41% (接近目标)
src/services/template_filler.py      - 82.04% (接近目标)
```

---

## 性能要求

### API 响应时间
```
文件上传: <2 秒 (10MB)
文件解析: <1 秒 (1000 行)
智能匹配: <500 毫秒
批量处理: <100 毫秒/行
```

### 内存使用
```
空闲: <100MB
处理 1000 行: <200MB
处理 10000 行: <500MB
```

---

## 安全要求

### 输入验证
```python
# 文件类型验证
ALLOWED_EXTENSIONS = {".csv", ".xlsx"}

# 文件大小限制
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# SQL 注入防护
# 使用 SQLAlchemy ORM（自动防护）

# XSS 防护
# FastAPI 自动转义 JSON 响应
```

### CORS 配置
```python
# 生产环境：指定实际域名
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000")
```

---

## 部署建议

### 开发环境
```bash
# 使用 SQLite
python -m uvicorn src.main:app --reload
```

### 生产环境
```bash
# 使用 PostgreSQL + Gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker 部署
```dockerfile
# 使用提供的 Dockerfile
docker-compose up -d
```

---

## 故障排查

### 问题: 测试失败
```bash
# 检查数据库
rm data/fill.db
python -c "from src.repositories.database import init_db; init_db()"

# 重新运行测试
pytest tests/unit tests/integration -v
```

### 问题: 端点 404
```bash
# 检查 main.py 是否包含所有端点
curl http://localhost:8000/docs
curl http://localhost:8000/api/v1/templates/built-in
```

### 问题: Playwright 测试超时
```bash
# 确保服务器在运行
python -m pytest tests/e2e/test_docs_playwright.py -v
# 或使用 TestClient（不需要服务器）
pytest tests/e2e/test_upload_page.py -v
```

---

## 联系信息

### 项目维护
- **主要开发**: Claude Sonnet 4.5
- **测试环境**: Linux (WSL2), Windows, macOS
- **Python 版本**: 3.11+

### 重要文档
- `README.md` - 项目概述
- `TEST_REPORT.md` - 测试报告
- `BETA_FEEDBACK.md` - Beta 测试反馈
- `fix_plan.md` - 开发计划（在 .ralph/ 目录）

### Git 仓库
- **主仓库**: github.com:isencher/fill.git
- **分支策略**: master (主分支), main (备用)
- **最新提交**: d621cf2

---

## 快速检查清单

在开始任何工作之前，请确认：

- [ ] 已阅读完整本文档
- [ ] 理解项目架构和功能
- [ ] 知道哪些文件不能删除/简化
- [ ] 了解测试策略和覆盖率要求
- [ ] 运行了完整测试套件确认一切正常
- [ ] 查看了最新的测试报告（88.46% 覆盖率）
- [ ] 理解为什么不能创建"简化版本"

---

## 版本历史

### v0.1.0-beta (当前版本)
- 完整功能实现
- 822 个测试通过
- 88.46% 代码覆盖率
- 生产就绪

### 重要里程碑
- 2026-02-19: 恢复完整版本，拒绝简化版本
- 2026-02-18: 代码覆盖率提升到 88.46%
- 2026-02-17: Beta 版本发布

---

**最后更新**: 2026-02-19
**文档版本**: 1.0
**状态**: ✅ 当前版本（完整功能版）
