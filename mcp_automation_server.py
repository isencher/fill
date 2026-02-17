#!/usr/bin/env python3
"""
MCP 服务器 - 将自动化开发系统暴露给 Claude Code

这个 MCP 服务器允许 Claude Code 直接调用自动化系统的功能。
"""

import asyncio
import json
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 导入自动化系统
import sys
sys.path.insert(0, str(Path(__file__).parent))
from executor import ExecutorEngine

class AutomationMCPServer:
    """自动化开发系统 MCP 服务器"""

    def __init__(self):
        self.server = Server("automation-dev")
        self.engine = ExecutorEngine()
        self.setup_handlers()

    def setup_handlers(self):
        """设置 MCP 处理器"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """列出可用的自动化工具"""
            return [
                Tool(
                    name="automation_execute",
                    description="执行自动化开发操作，带负反馈控制",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation_type": {
                                "type": "string",
                                "description": "操作类型 (add_function, modify_core_logic, etc.)",
                                "enum": ["add_function", "modify_core_logic", "refactor_module",
                                        "fix_bug", "add_dependency", "update_documentation"]
                            },
                            "description": {
                                "type": "string",
                                "description": "操作描述"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "文件路径（如果适用）"
                            },
                            "package": {
                                "type": "string",
                                "description": "包名（仅用于 add_dependency）"
                            }
                        },
                        "required": ["operation_type", "description"]
                    }
                ),
                Tool(
                    name="automation_get_trust",
                    description="获取操作信任分数和自动执行状态",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation_type": {
                                "type": "string",
                                "description": "要查询的操作类型（留空查询所有）"
                            }
                        }
                    }
                ),
                Tool(
                    name="automation_get_queue",
                    description="获取当前决策队列状态",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="automation_approve_queue",
                    description="批量批准决策队列中的所有操作",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "approve_all": {
                                "type": "boolean",
                                "description": "是否批准所有操作",
                                "default": true
                            }
                        }
                    }
                ),
                Tool(
                    name="automation_get_audit",
                    description="获取执行审计报告",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "days": {
                                "type": "number",
                                "description": "查询最近多少天",
                                "default": 7
                            }
                        }
                    }
                ),
                Tool(
                    name="automation_create_rollback",
                    description="创建回滚点（基于 git stash）",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="automation_rollback",
                    description="回滚到指定的回滚点",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "rollback_point": {
                                "type": "string",
                                "description": "回滚点引用"
                            }
                        },
                        "required": ["rollback_point"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """处理工具调用"""
            try:
                if name == "automation_execute":
                    return await self.execute_operation(arguments)
                elif name == "automation_get_trust":
                    return await self.get_trust(arguments)
                elif name == "automation_get_queue":
                    return await self.get_queue(arguments)
                elif name == "automation_approve_queue":
                    return await self.approve_queue(arguments)
                elif name == "automation_get_audit":
                    return await self.get_audit(arguments)
                elif name == "automation_create_rollback":
                    return await self.create_rollback(arguments)
                elif name == "automation_rollback":
                    return await self.rollback(arguments)
                else:
                    return [TextContent(
                        type="text",
                        text=f"未知工具: {name}"
                    )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"错误: {str(e)}"
                )]

    async def execute_operation(self, arguments: dict) -> list[TextContent]:
        """执行自动化操作"""
        operation = {
            "type": arguments["operation_type"],
            "description": arguments["description"]
        }
        if "file_path" in arguments:
            operation["file_path"] = arguments["file_path"]
        if "package" in arguments:
            operation["package"] = arguments["package"]

        result = self.engine.execute(operation)

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    async def get_trust(self, arguments: dict) -> list[TextContent]:
        """获取信任分数"""
        op_type = arguments.get("operation_type")

        trust_data = {}
        for optype, history in self.engine.trust_db.get("operation_history", {}).items():
            if op_type is None or optype == op_type:
                if history:
                    recent = history[-20:]
                    success_rate = sum(h["success"] for h in recent) / len(recent)
                    trust_data[optype] = {
                        "success_rate": f"{success_rate:.1%}",
                        "total_count": len(history),
                        "status": "auto" if success_rate >= 0.95 else "notify" if success_rate >= 0.8 else "review"
                    }

        return [TextContent(
            type="text",
            text=json.dumps(trust_data, ensure_ascii=False, indent=2)
        )]

    async def get_queue(self, arguments: dict) -> list[TextContent]:
        """获取决策队列"""
        queue_data = {
            "size": len(self.engine.decision_queue),
            "items": [
                {
                    "operation": item["operation"],
                    "timestamp": item["timestamp"]
                }
                for item in self.engine.decision_queue
            ]
        }

        return [TextContent(
            type="text",
            text=json.dumps(queue_data, ensure_ascii=False, indent=2)
        )]

    async def approve_queue(self, arguments: dict) -> list[TextContent]:
        """批准决策队列"""
        approve_all = arguments.get("approve_all", True)

        if approve_all:
            approved = []
            for item in self.engine.decision_queue:
                result = self.engine._execute_auto(item["operation"])
                approved.append(result)

            self.engine.decision_queue.clear()

            result = {
                "approved_count": len(approved),
                "results": approved
            }
        else:
            result = {"message": "使用 devops.py approve 进行交互式审批"}

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    async def get_audit(self, arguments: dict) -> list[TextContent]:
        """获取审计报告"""
        days = arguments.get("days", 7)

        logs_dir = Path(".logs")
        if not logs_dir.exists():
            return [TextContent(
                type="text",
                text=json.dumps({"message": "暂无日志"}, ensure_ascii=False)
            )]

        total = 0
        auto_count = 0
        success_count = 0

        for log_file in logs_dir.glob("*.jsonl"):
            for line in log_file.read_text().splitlines():
                entry = json.loads(line)
                total += 1
                if entry.get("decision_mode") == "auto":
                    auto_count += 1
                if entry.get("success"):
                    success_count += 1

        audit = {
            "days": days,
            "total_executions": total,
            "auto_rate": f"{auto_count / total * 100:.1f}%" if total > 0 else "0%",
            "success_rate": f"{success_count / total * 100:.1f}%" if total > 0 else "0%"
        }

        return [TextContent(
            type="text",
            text=json.dumps(audit, ensure_ascii=False, indent=2)
        )]

    async def create_rollback(self, arguments: dict) -> list[TextContent]:
        """创建回滚点"""
        rollback_point = self.engine._create_rollback_point()

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": rollback_point is not None,
                "rollback_point": rollback_point
            }, ensure_ascii=False, indent=2)
        )]

    async def rollback(self, arguments: dict) -> list[TextContent]:
        """执行回滚"""
        # 这里需要回滚点对象，但 MCP 只能传递字符串
        # 实际使用中可能需要更复杂的处理
        rollback_ref = arguments.get("rollback_point")

        # 尝试从 git stash 列表中找到匹配的
        import subprocess
        result = subprocess.run(
            ["git", "stash", "list"],
            capture_output=True,
            text=True
        )

        if rollback_ref in result.stdout:
            # 找到了，执行 pop
            pop_result = subprocess.run(
                ["git", "stash", "pop"],
                capture_output=True,
                text=True
            )

            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": pop_result.returncode == 0,
                    "message": "回滚成功" if pop_result.returncode == 0 else pop_result.stderr
                }, ensure_ascii=False, indent=2)
            )]
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "message": f"未找到回滚点: {rollback_ref}"
                }, ensure_ascii=False, indent=2)
            )]


async def main():
    """启动 MCP 服务器"""
    server = AutomationMCPServer()

    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            server.server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
