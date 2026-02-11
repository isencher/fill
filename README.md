# 自动化开发执行系统

> **核心理念**：知识不是文档，而是持续执行的行为

这个系统将负反馈控制理念转化为实际可执行的开发工作流，确保规则不仅仅是纸上谈兵。

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
