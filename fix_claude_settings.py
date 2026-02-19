#!/usr/bin/env python3
"""
Claude Code 配置快速修复脚本 - Windows 版本

自动修复 settings.json 格式问题
"""

import os
import sys
from pathlib import Path


def fix_settings():
    """修复 .claude/settings.json 格式"""
    settings_file = Path(".claude/settings.json")

    if not settings_file.exists():
        print("❌ 未找到 .claude/settings.json")
        return False

    # 备份原文件
    backup_file = settings_file.with_suffix(".backup")
    import shutil
    shutil.copy(settings_file, backup_file)
    print(f"✅ 已备份到: {backup_file}")

    # 新的正确配置
    new_settings = """{
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
}"""

    # 写入新配置
    settings_file.write_text(new_settings, encoding='utf-8')
    print(f"✅ 已修复: {settings_file}")

    # 验证
    import json
    try:
        data = json.loads(new_settings)
        hooks = data.get("hooks", {})

        # 检查格式
        if isinstance(hooks.get("PreToolUse"), list):
            print("✅ PreToolUse 格式正确")
        else:
            print("❌ PreToolUse 格式错误")
            return False

        if isinstance(hooks.get("PostToolUse"), list):
            print("✅ PostToolUse 格式正确")
        else:
            print("❌ PostToolUse 格式错误")
            return False

        if isinstance(hooks.get("UserPromptSubmit"), list):
            print("✅ UserPromptSubmit 格式正确")
        else:
            print("❌ UserPromptSubmit 格式错误")
            return False

        return True
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式错误: {e}")
        return False

    return True


def main():
    print("=" * 60)
    print("Claude Code 配置修复 - Windows 版本")
    print("=" * 60)

    print("\n🔧 正在修复 .claude/settings.json...\n")

    if fix_settings():
        print("\n" + "=" * 60)
        print("✅ 修复成功！")
        print("=" * 60)
        print("\n📋 下一步:")
        print("1. 关闭当前的 Claude Code 窗口")
        print("2. 重新打开项目 (D:\\.dev\\fill)")
        print("3. 验证无错误提示")
        print("\n🎉 配置问题已解决！")
        return 0
    else:
        print("\n❌ 修复失败")
        print("\n请手动修复:")
        print("1. 删除 .claude/settings.json")
        print("2. 从 .claude/settings.json.backup 恢复")
        print("3. 重启 Claude Code")
        return 1


if __name__ == "__main__":
    sys.exit(main())
