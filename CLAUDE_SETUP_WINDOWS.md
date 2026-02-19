# Windows 环境下 Claude Code 配置修复

## 问题说明

在 Windows 上使用 Claude Code 时，可能会遇到以下错误：

```
Settings Error: hooks format incorrect
PostToolUse: Expected array, but received object
PreToolUse: Expected array, but received object
UserPromptSubmit: Expected array, but received object
```

这是因为：
1. `.claude/settings.json` 使用了旧的 hooks 格式
2. 配置路径指向 Linux 容器路径
3. Windows 环境不支持自动化脚本

---

## 解决方案

### 方案 1：使用简化的配置（推荐）

将 `.claude/settings.json` 替换为以下内容：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": {
          "tools": ["BashTool", "TaskTool"]
        },
        "hooks": []
      }
    ],
    "PostToolUse": [
      {
        "matcher": {
          "tools": ["BashTool", "TaskTool"]
        },
        "hooks": []
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": {},
        "hooks": []
      }
    ]
  }
}
```

**优点**：
- ✅ 符合新的 hooks 格式
- ✅ 禁用自动化（Windows 环境不需要）
- ✅ 不会干扰正常使用

### 方案 2：完全移除 hooks

将 `.claude/settings.json` 替换为以下内容：

```json
{
  "mcpServers": {}
}
```

或者直接删除 hooks 部分，只保留基本配置。

---

## 详细步骤

### Windows PowerShell

```powershell
# 1. 进入项目目录
cd D:\.dev\fill

# 2. 备份当前配置
copy .claude\settings.json .claude\settings.json.backup

# 3. 创建新的配置文件
@'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": {
          "tools": ["BashTool", "TaskTool"]
        },
        "hooks": []
      }
    ],
    "PostToolUse": [
      {
        "matcher": {
          "tools": ["BashTool", "TaskTool"]
        },
        "hooks": []
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": {},
        "hooks": []
      }
    ]
  }
}
'@ | Out-File -FilePath .claude\settings.json -Encoding UTF8

# 4. 重启 Claude Code
```

### Git Bash

```bash
# 1. 进入项目目录
cd /.dev/fill

# 2. 备份当前配置
cp .claude/settings.json .claude/settings.json.backup

# 3. 创建新的配置文件
cat > .claude/settings.json << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": {
          "tools": ["BashTool", "TaskTool"]
        },
        "hooks": []
      }
    ],
    "PostToolUse": [
      {
        "matcher": {
          "tools": ["BashTool", "TaskTool"]
        },
        "hooks": []
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": {},
        "hooks": []
      }
    ]
  }
}
EOF

# 4. 重启 Claude Code
```

---

## 为什么需要修复？

### 旧格式（不兼容）
```json
{
  "hooks": {
    "PreToolUse": {
      "command": "...",
      "args": [...]
    }
  }
}
```

### 新格式（兼容）
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": {
          "tools": ["BashTool"]
        },
        "hooks": [
          {
            "type": "command",
            "command": "echo Done"
          }
        ]
      }
    ]
  }
}
```

---

## Windows 环境注意事项

### 路径问题
Linux 路径（容器）:
```
/app/fill/.claude/hooks/automation.py
```

Windows 路径:
```
D:\.dev\fill\.claude\hooks\automation.py
```

建议：Windows 环境下禁用自动化脚本

### Python 命令
- Linux: `python3`
- Windows: `python`

建议：使用跨平台写法 `python`

---

## 验证配置

### 检查配置文件

```powershell
# PowerShell
Get-Content .claude\settings.json | ConvertFrom-Json

# Git Bash
cat .claude/settings.json | python -m json.tool
```

### 重启 Claude Code

修改配置后，必须重启 Claude Code 才能生效：

1. 关闭 Claude Code
2. 重新打开项目
3. 确认没有错误提示

---

## 完整的 Windows 配置示例

创建文件：`.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": {
          "tools": ["BashTool", "TaskTool", "ReadTool", "WriteTool", "EditTool"]
        },
        "hooks": []
      }
    ],
    "PostToolUse": [
      {
        "matcher": {
          "tools": ["BashTool", "TaskTool", "ReadTool", "WriteTool", "EditTool"]
        },
        "hooks": []
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": {},
        "hooks": []
      }
    ]
  },
  "mcpServers": {}
}
```

这个配置：
- ✅ 符合新的 hooks 格式
- ✅ 禁用所有自动化（Windows 不需要）
- ✅ 允许正常使用所有工具
- ✅ 不会产生错误

---

## 常见问题

### Q: 为什么要禁用 hooks？

**A**: fill-dev-env 的自动化系统是为 Linux 容器环境设计的。Windows 环境下：
- 没有 automation.py 脚本
- 路径格式不兼容
- Python 命令不同
- 不需要负反馈控制系统

### Q: 我可以使用自动化吗？

**A**: 可以，但需要：
1. 重写 automation.py 为 Windows 兼容
2. 调整所有路径为 Windows 格式
3. 修改 Python 命令为 `python`
4. 或者使用 WSL2（推荐）

### Q: 不修复会有什么影响？

**A**:
- ❌ Claude Code 无法加载配置
- ⚠️ hooks 被完全跳过
- ⚠️ 其他设置可能也被忽略

---

## 推荐做法

### 对于 Windows 开发

**选项 1：禁用 hooks（推荐）**
- 简化配置
- 避免错误
- 专注于开发

**选项 2：使用 WSL2**
- 在 WSL2 中运行 fill 项目
- 保持完整的自动化功能
- 使用 Linux 环境的所有特性

---

## 更新项目文档

将此文档添加到项目，方便 Windows 用户：

1. 保存为 `CLAUDE_SETUP_WINDOWS.md`
2. 添加到 README.md 的文档链接
3. 在 WINDOWS_SETUP_CHECKLIST.md 中引用

---

**最后更新**: 2026-02-19
**版本**: 1.0
**适用于**: Claude Code 最新版本
