#!/usr/bin/env python3
"""
演示批量决策 UI
"""

from executor import ExecutorEngine
from datetime import datetime

def demo_batch_ui():
    engine = ExecutorEngine()

    print("=" * 60)
    print("批量决策 UI 演示")
    print("=" * 60)

    # 临时增加触发阈值，避免自动弹出UI
    original_threshold = engine.rules["batching"]["max_queue_size"]
    engine.rules["batching"]["max_queue_size"] = 100

    # 添加多个操作到队列
    operations = [
        {"type": "add_dependency", "description": "添加 Web 框架", "package": "fastapi"},
        {"type": "add_dependency", "description": "添加 ASGI 服务器", "package": "uvicorn"},
        {"type": "add_dependency", "description": "添加 ORM", "package": "sqlalchemy"},
        {"type": "add_dependency", "description": "添加数据库驱动", "package": "psycopg2"},
        {"type": "add_dependency", "description": "添加验证库", "package": "pydantic"},
    ]

    print(f"\n添加 {len(operations)} 个操作到决策队列...\n")

    for op in operations:
        engine.execute(op)
        print(f"[QUEUE] {op['package']}")

    print(f"\n决策队列大小: {len(engine.decision_queue)}")
    print(f"触发阈值: {engine.rules['batching']['max_queue_size']}")

    # 展示批量决策 UI（不等待输入）
    print("\n" + "=" * 60)
    print("批量决策审批 UI")
    print("=" * 60)

    if not engine.decision_queue:
        print("\n✓ 决策队列为空")
        return

    print(f"\n批量决策审批 ({len(engine.decision_queue)} 项待处理)")
    print("=" * 60)

    for i, item in enumerate(engine.decision_queue, 1):
        op = item["operation"]
        print(f"\n{i}. [{op['type']}] {op.get('description', '')}")
        if "package" in op:
            print(f"   包: {op['package']}")

    print("\n" + "-" * 60)
    print("处理选项:")
    print("  1. 批准全部 - 执行所有操作")
    print("  2. 拒绝全部 - 清空队列")
    print("  3. 逐个审查 - 单独处理每项")
    print("  4. 取消 - 稍后处理")

    print("\n[演示] 选择选项 1（批准全部）...\n")

    # 模拟选择选项 1
    approved = []
    for item in engine.decision_queue:
        result = engine._execute_auto(item["operation"])
        approved.append(result)
        print(f"  ✓ {item['operation']['package']}: {result['status']}")

    engine.decision_queue.clear()
    print(f"\n✓ 已执行 {len(approved)} 项操作")

    # 显示结果
    print("\n" + "=" * 60)
    print("执行结果")
    print("=" * 60)

    # 检查 requirements.txt
    from pathlib import Path
    req_file = Path("requirements.txt")
    if req_file.exists():
        print("\nrequirements.txt 已更新:")
        for line in req_file.read_text().strip().split('\n'):
            print(f"  - {line}")

    # 更新后的信任分数
    print("\n信任分数更新:")
    for op_type, history in engine.trust_db["operation_history"].items():
        if history:
            recent = history[-20:]
            success_rate = sum(h["success"] for h in recent) / len(recent)
            status = "🟢 自动" if success_rate >= 0.95 else "🟡 通知"
            print(f"  {status} {op_type}: {success_rate:.1%}")

    # 恢复原始阈值
    engine.rules["batching"]["max_queue_size"] = original_threshold

if __name__ == "__main__":
    demo_batch_ui()
