# Fill 项目快速参考

**⚠️ 警告**: 在修改任何代码之前，请先阅读 `PROJECT_CONTEXT.md` 获取完整上下文。

---

## 一分钟了解 Fill

### 是什么
智能表格数据自动填充工具 - 批量将 Excel/CSV 数据填充到 Word/Excel 模板

### 核心流程
```
上传文件 → 选择模板 → 字段映射 → 批量处理 → 下载文档
```

### 技术栈
- 后端: Python 3.11 + FastAPI
- 前端: 原生 JavaScript (无框架)
- 数据库: SQLite (可切换 PostgreSQL)
- 测试: pytest + playwright

---

## 禁止事项 ⚠️

### ❌ 不要做
1. **不要简化 main.py** - 必须保留所有 API 端点
2. **不要删除测试文件** - 所有测试都必须保留
3. **不要移除数据库层** - 必须使用持久化存储
4. **不要跳过字段映射** - 这是核心功能
5. **不要删除前端页面** - 所有 HTML/JS 文件都要保留
6. **不要引入前端框架** - 使用纯 JavaScript
7. **不要降低测试覆盖率** - 当前 88.46%，必须 ≥85%

### ✅ 必须做
1. 保留完整的分层架构
2. 运行完整测试套件
3. 遵循 PEP 8 代码规范
4. 使用 Conventional Commits
5. 保持文档同步更新

---

## 关键文件清单

### 核心代码（不能简化）
```
src/main.py                      # ⚠️ 所有端点
src/models/*.py                  # 所有模型
src/repositories/*.py            # 所有仓储
src/services/*.py                # 所有服务
src/static/*.html                # 所有页面
src/static/*.js                  # 所有脚本
```

### 测试文件（不能删除）
```
tests/unit/*.py                  # ~700 个单元测试
tests/integration/*.py           # ~88 个集成测试
tests/e2e/*.py                   # ~470 个 E2E 测试
```

---

## 快速启动

### 安装依赖
```bash
pip install -r requirements.txt
```

### 初始化数据库
```bash
python -c "from src.repositories.database import init_db; init_db()"
```

### 启动服务器
```bash
python -m uvicorn src.main:app --reload
```

### 运行测试
```bash
# 完整测试套件
pytest tests/ -v

# 单元测试
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# E2E 测试 (TestClient - 不需要服务器)
pytest tests/e2e/test_upload_page.py -v
pytest tests/e2e/test_mapping_page.py -v
```

---

## API 端点速查

### 必须保留的端点（完整版）

**基础**:
```
GET  /                          # 健康检查
GET  /docs                      # Swagger UI
GET  /redoc                     # ReDoc
```

**文件管理**:
```
POST /api/v1/upload             # 上传文件
GET  /api/v1/files              # 文件列表
GET  /api/v1/files/{id}         # 文件详情
DELETE /api/v1/files/{id}       # 删除文件
```

**模板管理**:
```
GET  /api/v1/templates          # 模板列表
GET  /api/v1/templates/{id}     # 模板详情
POST /api/v1/templates          # 上传模板
DELETE /api/v1/templates/{id}   # 删除模板
```

**字段映射**:
```
POST /api/v1/parse              # 解析文件 ⭐
POST /api/v1/suggest-mapping    # 智能匹配 ⭐
POST /api/v1/mappings           # 创建映射 ⭐
```

**批量处理**:
```
POST /api/v1/jobs               # 创建任务 ⭐
GET  /api/v1/jobs/{id}          # 任务详情
GET  /api/v1/jobs/{id}/progress # 进度查询
```

**前端页面**:
```
GET  /templates.html            # 模板选择 ⭐
GET  /mapping.html              # 字段映射 ⭐
GET  /processing.html           # 处理进度 ⭐
```

**⭐ = 核心功能，绝对不能删除**

---

## 常见问题

### Q: 我可以简化 main.py 吗？
**A**: 不可以。main.py 包含所有端点，删除任何端点都会破坏功能。

### Q: 我可以删除测试文件吗？
**A**: 不可以。测试覆盖率达到 88.46%，删除测试会降低覆盖率。

### Q: 我可以只保留 TestClient 测试吗？
**A**: 不可以。Playwright 测试验证浏览器中的实际行为。

### Q: 我可以用 React 重写前端吗？
**A**: 不可以。项目使用纯 JavaScript，保持轻量级。

### Q: 我可以移除数据库，只用内存吗？
**A**: 不可以。数据库持久化是生产环境的必需功能。

---

## 测试状态

### 当前指标
```
总测试: 823
通过: 822 ✅
跳过: 1
失败: 0
通过率: 99.88%
覆盖率: 88.46%
```

### 测试分类
```
单元测试: ~700 (100% 通过)
集成测试: ~88 (100% 通过)
E2E 测试: ~470 (98.7% 通过)
```

---

## 紧急联系

### 遇到问题？
1. 先查看 `PROJECT_CONTEXT.md` 完整文档
2. 检查测试是否通过: `pytest tests/ -v`
3. 查看日志: `.ralph/logs/ralph.log`
4. 检查 git 历史了解最近更改

### 提交 Bug
1. 提供完整错误信息
2. 说明复现步骤
3. 附加测试结果
4. 提及环境信息（OS, Python 版本）

---

## 版本信息

```
当前版本: v0.1.0-beta
Git 提交: d621cf2
分支: master
状态: 生产就绪 ✅
```

---

**记住**: 如果不确定，请查阅 `PROJECT_CONTEXT.md` 完整文档！

**最后更新**: 2026-02-19
