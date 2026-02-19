# Fill - 智能表格数据填充工具

> **自动化 + 智能填充**：让重复的文档工作自动化

Fill 是一款智能工具，可以自动将 Excel/CSV 数据填充到模板文件中，节省大量重复工作时间。

## 🎯 核心功能

- 📤 **智能上传**：支持 CSV 和 Excel 文件
- 🎯 **智能映射**：自动识别并映射字段名
- 📋 **内置模板**：发票、合同、报表等
- ⚡ **批量处理**：一次性生成多个文件
- 📥 **快速下载**：批量下载所有输出

## 📚 文档导航

### 重要文档 ⚠️
- **[项目完整上下文](PROJECT_CONTEXT.md)** ⭐ **开发前必读！**
- **[快速参考](QUICK_REFERENCE.md)** - 快速查找和检查清单

### 用户文档
- [用户指南](#)
- [API 文档](api.md)
- [Beta 测试反馈](BETA_FEEDBACK.md) ← **正在测试中！**

### 开发文档
- [开发快速参考](CLAUDE_QUICKREF.md)
- [测试报告](TEST_REPORT.md)
- [更新日志](CHANGELOG.md)

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
python3 start.py

# 3. 访问应用
# 浏览器打开 http://localhost:8000
```

## 🧪 测试

```bash
# 运行所有测试
python3 -m pytest

# 运行单元测试
python3 -m pytest tests/unit

# 查看覆盖率
python3 -m pytest --cov=src tests/
```

## 📦 项目信息

- **版本**：v0.1.0-beta
- **仓库**：https://github.com/isencher/fill
- **文档**：[GitHub Wiki](https://github.com/isencher/fill/wiki)

## 🏗️ 自动化开发系统

Fill 使用负反馈控制系统进行开发，详情见：[fill-dev-env](https://github.com/isencher/fill-dev-env)

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        持续执行层                              │
├─────────────────────────────────────────────────────────────┤
│  watcher.py         - 监控文件变化，自动触发规则检查            │
│  .git/hooks/pre-commit - Git提交时强制执行规则                 │
│  Makefile           - 快捷命令集成到开发流程                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        决策引擎层                              │
├─────────────────────────────────────────────────────────────┤
│  executor.py        - 核心执行引擎：检查规则、执行操作、更新信任 │
│  rules.json        - 自主决策边界配置                         │
│  .trust/scores.json - 操作历史和信任分数                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        负反馈循环                              │
├─────────────────────────────────────────────────────────────┤
│  执行 → 测量 → 更新信任 → 调整边界 → 再次执行                   │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

```bash
# 1. 初始化项目
make init

# 2. 安装Git hooks（让每次提交自动检查规则）
python3 devops.py install

# 3. 启动持续监控（可选）
python3 watcher.py --mode watch

# 4. 查看系统状态
python3 devops.py trust    # 信任分数
python3 devops.py queue     # 决策队列
python3 devops.py audit     # 执行审计
```

## 核心机制

### 1. 渐进式自主

操作根据历史成功率自动升级权限级别：

| 成功率 | 级别 | 行为 |
|--------|------|------|
| >95% | 自动 | 完全自主执行 |
| 80-95% | 通知 | 执行后通知人类 |
| <80% | 审批 | 需要人类批准 |

### 2. 批量决策

低延迟的秘诀：不逐个打扰人类

```bash
# 当决策队列达到阈值或超时时，一次性展示所有待审批项
python3 devops.py approve
```

### 3. 结构化反馈

人类只做单选题，不填空：

```
[MANUAL] 需要审批: modify_core_logic

请选择:
  1. 批准 - 允许修改核心逻辑
  2. 重构后批准 - 需要先重构相关代码
  3. 拒绝 - 当前方案不可接受
```

### 4. 自动回滚

优先快速迭代，而非完美决策：

- 每次操作自动创建回滚点
- 测试失败触发自动回滚
- 人类只处理无法回滚的情况

## 使用示例

### 在AI工作流中使用

```python
from executor import ExecutorEngine

engine = ExecutorEngine()

# AI生成代码后自动检查
result = engine.execute({
    "type": "add_function",
    "description": "添加用户验证函数",
    "file_path": "src/auth/verify.py"
})

# 根据结果决定下一步
if result['status'] == 'success':
    print("✓ 已自动执行")
elif result['status'] == 'queued':
    print("→ 已加入决策队列，等待批量审批")
```

### 作为开发者使用

```bash
# 日常开发
git add .
git commit -m "添加新功能"    # 自动触发规则检查

# 查看系统状态
python3 devops.py trust       # 哪些操作已升级为自动？
python3 devops.py audit       # 本周自动化程度如何？

# 批量审批决策
python3 devops.py approve
```

## 工作流集成

### 方式1：Git Hook（推荐）
```bash
python3 devops.py install
```
每次 `git commit` 自动执行规则检查

### 方式2：文件监控
```bash
python3 watcher.py --mode watch
```
文件修改时自动检查

### 方式3：Make命令
```bash
make check-trust    # 查看信任分数
make audit          # 审计本周执行记录
make batch-decisions # 处理批量决策
```

## 知识如何变成持续行动

| 传统方式 | 本系统 |
|----------|--------|
| 写在文档中 | 写在可执行的规则中 |
| 人类主动记忆 | Git Hook 强制执行 |
| 一次性配置 | 负反馈持续优化 |
| 静态规则 | 根据历史动态调整 |
| 逐个审批 | 批量决策 |

## 配置说明

编辑 `rules.json` 调整：

- `autonomy.*_threshold`: 自主执行的信任阈值
- `operations.*.autonomy_level`: 各操作的默认级别
- `path_rules`: 基于路径的规则覆盖
- `batching`: 批量决策触发条件

## 监控和调试

```bash
# 执行日志
ls .logs/

# 信任数据库
cat .trust/scores.json

# 决策队列
ls decisions/
```

## 理念

> "The best process is the one that runs without you thinking about it."

这个系统的目标不是让开发者学习新工具，而是让规则在后台自动运行，只在真正需要时才打扰人类。
