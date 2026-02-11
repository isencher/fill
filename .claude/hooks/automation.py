#!/usr/bin/env python3
"""
Claude Code Hooks - 自动化开发系统集成

这些 hooks 在 Claude Code 执行前后触发，实现负反馈控制。
"""

import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from executor import ExecutorEngine

# 全局引擎实例
_engine = None

def get_engine():
    """获取或创建引擎实例"""
    global _engine
    if _engine is None:
        _engine = ExecutorEngine()
    return _engine


def pre_tool_use(input_data):
    """
    PreToolUse Hook - 在 Claude 使用工具前执行

    检查操作是否符合自动化规则，返回建议或阻止
    """
    try:
        data = json.loads(input_data) if isinstance(input_data, str) else input_data
        tool_name = data.get("name", "")
        parameters = data.get("parameters", {})

        # 只处理文件写入工具
        if tool_name not in ["Write", "Edit", "NotebookEdit"]:
            return {"allowed": True, "reason": "非文件操作"}

        # 获取文件路径
        file_path = parameters.get("file_path", "")
        if not file_path:
            return {"allowed": True, "reason": "无文件路径"}

        # 推断操作类型
        engine = get_engine()
        operation = _infer_operation_from_tool(tool_name, file_path, parameters)

        if not operation:
            return {"allowed": True, "reason": "无法推断操作类型"}

        # 检查自主边界
        decision_mode = engine._check_autonomy(operation)

        response = {
            "operation": operation["type"],
            "file_path": file_path,
            "decision_mode": decision_mode
        }

        if decision_mode == "manual":
            response["allowed"] = False
            response["reason"] = "核心文件需要人工审批"
            response["suggestion"] = f"请使用 python3 devops.py approve 进行审批"
        elif decision_mode == "review":
            response["allowed"] = True
            response["queued"] = True
            response["message"] = "操作已加入决策队列"
        else:
            response["allowed"] = True
            response["message"] = "操作符合自动执行规则"

        return response

    except Exception as e:
        # 出错时不阻止 Claude，只记录
        return {
            "allowed": True,
            "error": str(e),
            "reason": "Hook 执行失败，允许继续"
        }


def post_tool_use(input_data):
    """
    PostToolUse Hook - 在 Claude 使用工具后执行

    测量结果，更新信任分数，触发回滚（如果需要）
    """
    try:
        data = json.loads(input_data) if isinstance(input_data, str) else input_data
        tool_name = data.get("name", "")
        result = data.get("result", {})

        # 只处理文件操作结果
        if tool_name not in ["Write", "Edit", "NotebookEdit"]:
            return {"processed": False, "reason": "非文件操作"}

        parameters = data.get("parameters", {})
        file_path = parameters.get("file_path", "")

        engine = get_engine()
        operation = _infer_operation_from_tool(tool_name, file_path, parameters)

        if not operation:
            return {"processed": False, "reason": "无法推断操作类型"}

        # 测量结果
        success = engine._measure_result(operation, result)

        # 更新信任分数
        engine._update_trust_score(operation, success)

        if not success:
            # 如果失败，建议回滚
            response = {
                "processed": True,
                "success": False,
                "action": "rollback_suggested",
                "message": "操作失败，建议回滚"
            }
        else:
            response = {
                "processed": True,
                "success": True,
                "trust_updated": True
            }

        return response

    except Exception as e:
        return {
            "processed": False,
            "error": str(e)
        }


def user_prompt_submit(input_data):
    """
    UserPromptSubmit Hook - 在用户提交提示时执行

    添加项目上下文到 Claude 的提示中
    """
    try:
        # 读取信任分数
        trust_file = Path(".trust/scores.json")
        if trust_file.exists():
            with open(trust_file) as f:
                trust_data = json.load(f)

            # 构建上下文
            context_parts = []

            # 添加高信任操作
            for op_type, history in trust_data.get("operation_history", {}).items():
                if history:
                    recent = history[-20:]
                    success_rate = sum(h["success"] for h in recent) / len(recent)
                    if success_rate >= 0.95:
                        context_parts.append(f"  - {op_type}: 可自动执行 (100%)")

            if context_parts:
                context = "\n".join([
                    "# 项目自动化状态",
                    "",
                    "以下操作已达到自动执行标准:",
                ] + context_parts)

                return {
                    "context_added": True,
                    "context": context
                }

        return {"context_added": False}

    except Exception as e:
        return {
            "context_added": False,
            "error": str(e)
        }


def _infer_operation_from_tool(tool_name, file_path, parameters):
    """从 Claude 工具调用推断操作类型"""
    path = Path(file_path) if file_path else None
    if not path:
        return None

    path_str = str(path)

    # 根据工具类型和路径推断
    if tool_name == "Write":
        # 新文件创建
        if "tests" in path_str or path_str.endswith("_test.py"):
            return {
                "type": "add_function",
                "description": f"创建测试文件: {path.name}",
                "file_path": path_str
            }
        elif path_str.endswith(".md"):
            return {
                "type": "update_documentation",
                "description": f"更新文档: {path.name}",
                "file_path": path_str
            }
        elif "src/core" in path_str:
            return {
                "type": "modify_core_logic",
                "description": f"创建核心文件: {path.name}",
                "file_path": path_str
            }
        else:
            return {
                "type": "add_function",
                "description": f"创建文件: {path.name}",
                "file_path": path_str
            }

    elif tool_name == "Edit":
        # 文件编辑
        if "src/core" in path_str:
            return {
                "type": "modify_core_logic",
                "description": f"修改核心文件: {path.name}",
                "file_path": path_str
            }
        else:
            return {
                "type": "add_function",
                "description": f"修改文件: {path.name}",
                "file_path": path_str
            }

    return None


# CLI 入口点
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Claude Code Automation Hooks")
    parser.add_argument("--hook", required=True, choices=["pre", "post", "prompt"])
    parser.add_argument("--input", required=True)

    args = parser.parse_args()

    # 读取输入
    with open(args.input) as f:
        input_data = f.read()

    # 执行对应的 hook
    if args.hook == "pre":
        result = pre_tool_use(input_data)
    elif args.hook == "post":
        result = post_tool_use(input_data)
    elif args.hook == "prompt":
        result = user_prompt_submit(input_data)
    else:
        result = {"error": "Unknown hook"}

    # 输出结果（JSON 格式）
    print(json.dumps(result, ensure_ascii=False, indent=2))
