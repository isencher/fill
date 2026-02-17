# Claude Code + 自动化开发系统 - 快速参考

## Claude 对话示例

### 1. 创建文件（自动执行）

```
你: 创建一个用户测试文件

Claude: 我将使用自动化系统创建测试文件。

[调用 automation_execute]
操作: add_function
结果: success ✓

✓ 已创建 tests/test_user.py
信任分数: add_function → 100% (自动执行)
```

### 2. 修改核心文件（需要审批）

```
你: 更新认证模块的核心逻辑

Claude: 检测到这是核心文件修改，需要审批。

[PreToolUse Hook 返回: allowed=false, queued=true]

操作已加入决策队列。
使用 "python3 devops.py approve" 进行审批，或告诉我"批准所有排队操作"。
```

### 3. 批量审批

```
你: 批准所有待审批操作

Claude: [调用 automation_approve_queue]

✓ 已批准并执行 3 项操作:
  - modify_core_logic: src/core/auth.py
  - add_dependency: psycopg2-binary
  - refactor_module: src/user.py
```

### 4. 查看自动化状态

```
你: 自动化系统运行状态如何？

Claude: [调用 automation_get_trust 和 automation_get_audit]

自动化统计 (最近 7 天):
  总执行: 45 次
  自动率: 87%
  成功率: 96%

信任状态:
  🟢 add_function: 100% (自动)
  🟢 update_documentation: 100% (自动)
  🟡 modify_core_logic: 82% (通知后执行)
  🔴 add_dependency: 65% (需审批)
```

### 5. 创建回滚点

```
你: 在修改之前创建一个回滚点

Claude: [调用 automation_create_rollback]

✓ 回滚点已创建: _rollback_point_20260211_153000

现在可以安全地进行修改。如果需要回滚，告诉我。
```

## MCP 工具快速参考

| 工具 | 参数 | 用途 |
|------|------|------|
| `automation_execute` | operation_type, description, [file_path] | 执行操作 |
| `automation_get_trust` | [operation_type] | 查看信任分数 |
| `automation_get_queue` | - | 查看决策队列 |
| `automation_approve_queue` | [approve_all=true] | 批准队列 |
| `automation_get_audit` | [days=7] | 审计报告 |
| `automation_create_rollback` | - | 创建回滚点 |
| `automation_rollback` | rollback_point | 执行回滚 |

## Hook 行为参考

| 文件路径 | 操作类型 | 默认行为 |
|----------|----------|----------|
| `docs/*.md` | update_documentation | ✅ 自动执行 |
| `tests/*` | add_function | ✅ 自动执行 |
| `src/utils/*` | add_function | ✅ 自动执行 |
| `src/core/*` | modify_core_logic | ⚠️ 需要审批 |

## 常用命令

```bash
# 直接使用 CLI 工具
python3 devops.py trust          # 查看信任分数
python3 devops.py queue          # 查看决策队列
python3 devops.py approve       # 批量审批
python3 devops.py audit          # 审计报告

# 启动文件监控
python3 watcher.py --mode watch

# MCP 服务器（Claude Code 自动启动）
python3 mcp_automation_server.py
```

## 典型工作流

```
开始开发
    ↓
Claude: "创建测试文件"
    ↓ [PreToolUse Hook]
检查: 测试文件 → 自动执行
    ↓
Claude 执行 Write 工具
    ↓ [PostToolUse Hook]
测量: 文件已创建 ✓
更新: add_function 信任 +1
    ↓
Claude: "实现功能代码"
    ↓ [PreToolUse Hook]
检查: src/utils/ → 自动执行
    ↓
Claude 执行 Write 工具
    ↓ [PostToolUse Hook]
测量: 文件已创建 ✓
    ↓
Claude: "修改核心逻辑"
    ↓ [PreToolUse Hook]
检查: src/core/ → 需要审批
    ↓
队列操作，提示用户
    ↓
用户: "批准所有"
    ↓ [automation_approve_queue]
执行并更新信任
```

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| Hook 不触发 | 检查 `.claude/settings.json` 路径 |
| MCP 工具不可用 | 确保 `mcp_automation_server.py` 可执行 |
| 操作总是需要审批 | 增加成功次数以提升信任分数 |
| 回滚失败 | 确保有 Git 仓库且工作目录干净 |
