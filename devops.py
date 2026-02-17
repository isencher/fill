#!/usr/bin/env python3
"""
自动化开发CLI工具
让规则执行成为开发工作流的一部分
"""

import sys
import json
import argparse
from pathlib import Path
from executor import ExecutorEngine


def cmd_execute(args):
    """执行操作"""
    engine = ExecutorEngine()
    result = engine.execute({
        "type": args.type,
        "description": args.description,
        "file_path": args.file
    })
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_check(args):
    """检查规则配置"""
    engine = ExecutorEngine()
    print(f"当前规则配置:")
    print(f"  - 自动执行阈值: {engine.rules['autonomy']['auto_threshold']:.0%}")
    print(f"  - 通知阈值: {engine.rules['autonomy']['notify_threshold']:.0%}")
    print(f"  - 批量队列大小: {engine.rules['batching']['max_queue_size']}")


def cmd_trust(args):
    """查看信任分数"""
    if not Path('.trust/scores.json').exists():
        print("暂无信任数据")
        return

    with open('.trust/scores.json') as f:
        data = json.load(f)

    print("信任分数统计 (最近20次):")
    print("-" * 40)

    for op, history in data.get('operation_history', {}).items():
        if history:
            recent = history[-20:]
            success_rate = sum(h['success'] for h in recent) / len(recent)
            total = len(history)

            # 确定状态
            if success_rate >= 0.95:
                status = "🟢 自动"
            elif success_rate >= 0.8:
                status = "🟡 通知"
            else:
                status = "🔴 审批"

            print(f"{status} {op:25s} {success_rate:6.1%} ({total}次)")


def cmd_queue(args):
    """查看决策队列"""
    engine = ExecutorEngine()
    queue = engine.decision_queue

    if not queue:
        print("✓ 决策队列为空")
        return

    print(f"决策队列 ({len(queue)} 项):")
    print("-" * 40)

    for i, item in enumerate(queue, 1):
        op = item['operation']
        print(f"{i}. [{op['type']}] {op.get('description', '')}")


def cmd_audit(args):
    """审计日志"""
    logs_dir = Path('.logs')
    if not logs_dir.exists():
        print("暂无日志")
        return

    # 按日期范围筛选
    days = args.days or 7

    print(f"最近 {days} 天的执行审计:")
    print("-" * 50)

    total = 0
    auto_count = 0
    success_count = 0

    for log_file in sorted(logs_dir.glob('*.jsonl')):
        for line in log_file.read_text().splitlines():
            entry = json.loads(line)
            total += 1
            if entry.get('decision_mode') == 'auto':
                auto_count += 1
            if entry.get('success'):
                success_count += 1

    if total == 0:
        print("暂无执行记录")
        return

    auto_rate = auto_count / total * 100
    success_rate = success_count / total * 100

    print(f"总执行次数: {total}")
    print(f"自动执行率: {auto_rate:.1f}%")
    print(f"成功率: {success_rate:.1f}%")


def cmd_approve(args):
    """批量审批决策队列"""
    engine = ExecutorEngine()

    if not engine.decision_queue:
        print("✓ 决策队列为空，无需审批")
        return

    print(f"审批 {len(engine.decision_queue)} 项决策:")
    print("-" * 50)

    for i, item in enumerate(engine.decision_queue, 1):
        op = item['operation']
        print(f"{i}. {op['type']}: {op.get('description', '')}")

    choice = input("\n批准全部? [y/N]: ").strip().lower()

    if choice == 'y':
        for item in engine.decision_queue:
            engine.execute(item['operation'])
        engine.decision_queue.clear()
        print("✓ 已批准并执行全部")
    else:
        print("已取消")


def cmd_install(args):
    """安装Git hooks"""
    git_dir = Path('.git')
    if not git_dir.exists():
        print("错误: 不是Git仓库")
        return

    hooks_dir = git_dir / 'hooks'
    hooks_dir.mkdir(exist_ok=True)

    import shutil
    shutil.copy('.git_hooks/pre-commit', hooks_dir / 'pre-commit')
    os.chmod(hooks_dir / 'pre-commit', 0o755)

    print("✓ Git pre-commit hook 已安装")
    print("  每次提交前将自动检查规则")


def main():
    parser = argparse.ArgumentParser(
        description="自动化开发CLI - 让规则成为持续行动",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  devops execute add_function -f src/utils/helpers.py -d "添加辅助函数"
  devops trust          # 查看信任分数
  devops queue           # 查看决策队列
  devops approve         # 批量审批
  devops audit --days 7  # 审计最近7天
  devops install         # 安装Git hooks
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # execute 命令
    exec_parser = subparsers.add_parser('execute', help='执行操作')
    exec_parser.add_argument('type', help='操作类型')
    exec_parser.add_argument('-d', '--description', help='描述')
    exec_parser.add_argument('-f', '--file', help='文件路径')
    exec_parser.set_defaults(func=cmd_execute)

    # check 命令
    subparsers.add_parser('check', help='检查规则配置').set_defaults(func=cmd_check)

    # trust 命令
    subparsers.add_parser('trust', help='查看信任分数').set_defaults(func=cmd_trust)

    # queue 命令
    subparsers.add_parser('queue', help='查看决策队列').set_defaults(func=cmd_queue)

    # approve 命令
    subparsers.add_parser('approve', help='批量审批决策队列').set_defaults(func=cmd_approve)

    # audit 命令
    audit_parser = subparsers.add_parser('audit', help='审计执行日志')
    audit_parser.add_argument('--days', type=int, help='天数')
    audit_parser.set_defaults(func=cmd_audit)

    # install 命令
    subparsers.add_parser('install', help='安装Git hooks').set_defaults(func=cmd_install)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == '__main__':
    main()
