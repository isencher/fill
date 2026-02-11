#!/usr/bin/env python3
"""
测试批量决策功能
"""

from executor import ExecutorEngine

def test_batch_decisions():
    engine = ExecutorEngine()

    print("=" * 60)
    print("批量决策功能测试")
    print("=" * 60)

    # 添加多个需要审查的操作到队列
    # 使用 add_dependency 因为它在 rules.json 中配置为 "review" 级别
    operations = [
        {
            "type": "add_dependency",
            "description": "添加数据库驱动",
            "package": "psycopg2-binary"
        },
        {
            "type": "add_dependency",
            "description": "添加HTTP客户端",
            "package": "httpx"
        },
        {
            "type": "add_dependency",
            "description": "添加配置管理",
            "package": "pydantic-settings"
        },
        {
            "type": "add_dependency",
            "description": "添加测试框架",
            "package": "pytest-cov"
        },
        {
            "type": "add_dependency",
            "description": "添加代码格式化工具",
            "package": "black"
        }
    ]

    print(f"\n添加 {len(operations)} 个操作到决策队列...\n")

    for i, op in enumerate(operations, 1):
        result = engine.execute(op)
        print(f"{i}. [{op['type']}] {op.get('description', '')} → {result['status']}")

    print(f"\n决策队列大小: {len(engine.decision_queue)}")
    print(f"触发阈值: {engine.rules['batching']['max_queue_size']}")

    # 手动触发批量决策
    print("\n" + "=" * 60)
    print("手动触发批量决策审批")
    print("=" * 60)

    # 展示当前队列内容
    print(f"\n当前队列 ({len(engine.decision_queue)} 项):")
    for i, item in enumerate(engine.decision_queue, 1):
        op = item["operation"]
        print(f"  {i}. [{op['type']}] {op.get('description', '')}")

    # 模拟批量批准
    print("\n[模拟] 批量批准所有操作...")

    # 批准并执行所有排队的操作
    approved_count = 0
    failed_count = 0
    results = []

    for item in engine.decision_queue[:]:
        result = engine._execute_auto(item["operation"])
        results.append(result)
        if result["status"] == "success":
            approved_count += 1
        else:
            failed_count += 1

    print(f"\n✓ 已执行 {approved_count} 项操作")
    if failed_count > 0:
        print(f"✗ 失败 {failed_count} 项操作")

    # 清空队列
    engine.decision_queue.clear()

    print(f"\n队列剩余: {len(engine.decision_queue)} 项")

    # 显示更新后的信任分数
    print("\n" + "=" * 60)
    print("更新后的信任分数:")
    print("=" * 60)
    for op_type, history in engine.trust_db["operation_history"].items():
        if history:
            recent = history[-20:]
            success_rate = sum(h["success"] for h in recent) / len(recent)
            print(f"{op_type}: {success_rate:.1%}")

    print("\n测试完成!")

if __name__ == "__main__":
    test_batch_decisions()
