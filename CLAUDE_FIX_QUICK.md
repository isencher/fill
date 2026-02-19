# ⚡ Claude Code 配置错误 - 立即修复

## 🔥 问题

Windows 上使用 Claude 时遇到：
```
Settings Error
  └ hooks
    ├ PostToolUse: Expected array, but received object
    ├ PreToolUse: Expected array, but received object
    └─UserPromptSubmit: Expected array, but received object
```

---

## ✅ 解决方案（3 步）

### 第 1 步：拉取最新代码
```bash
cd D:\.dev\fill
git pull origin master
```

**预期输出**:
```
Updating d46d355..31e9f8e
Fast-forward
 .claude/settings.json | 26 ++++--------------------
 fix_claude_settings.py | 120 +++++++++++++++++++++++++++++++
```

### 第 2 步：运行自动修复脚本
```bash
python fix_claude_settings.py
```

**预期输出**:
```
============================================================
Claude Code 配置修复 - Windows 版本
============================================================

🔧 正在修复 .claude/settings.json...

✅ 已备份到: .claude\settings.json.backup
✅ 已修复: .claude\settings.json
✅ PreToolUse 格式正确
✅ PostToolUse 格式正确
✅ UserPromptSubmit 格式正确

============================================================
✅ 修复成功！
============================================================

📋 下一步:
1. 关闭当前的 Claude Code 窗口
2. 重新打开项目 (D:\.dev\fill)
3. 验证无错误提示

🎉 配置问题已解决！
```

### 第 3 步：重启 Claude Code

1. 关闭 Claude Code
2. 重新打开项目
3. 确认无错误提示

---

## 🎯 验证修复成功

### Claude Code 应该正常打开
```
✅ Settings loaded successfully
✅ No configuration errors
✅ All tools available
```

---

## ⚠️ 如果第 1 步 git pull 后没有新文件

### 手动修复方案

创建文件 `.claude/settings.json`，内容如下：

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

---

## 📝 完整操作命令（复制粘贴）

```bash
# 一键修复
cd D:\.dev\fill
git pull origin master
python fix_claude_settings.py
```

然后重启 Claude Code。

---

## 🔍 故障排查

### 如果 git pull 显示 "Already up to date"

说明远程没有新内容，请运行：

```bash
# 强制更新到最新
git fetch origin
git reset --hard origin/master
```

### 如果 python fix_claude_settings.py 失败

说明脚本未拉取下来，请手动创建配置文件（见"手动修复方案"）

---

## ✅ 成功标志

执行修复后，重启 Claude Code 应该看到：

- ✅ 项目正常打开
- ✅ 无配置错误
- ✅ 所有工具可用
- ✅ 可以开始开发

---

**快速命令**:
```bash
git pull origin master && python fix_claude_settings.py
```

**然后重启 Claude Code**

---

**修复版本**: 31e9f8e
**最后更新**: 2026-02-19
**Windows 兼容性**: ✅ 完全支持
