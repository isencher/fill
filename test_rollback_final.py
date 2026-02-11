#!/usr/bin/env python3
"""
回滚功能演示 - 清晰版
"""

import subprocess
from pathlib import Path
from executor import ExecutorEngine

def run_git(cmd):
    result = subprocess.run(f"git {cmd}", shell=True, capture_output=True, text=True)
    return result

def demo_rollback():
    print("=" * 60)
    print("回滚功能演示")
    print("=" * 60)

    engine = ExecutorEngine()

    # 清理
    for f in Path(".").glob("demo_rollback*"):
        f.unlink()

    # 提交现有更改
    run_git("add -A")
    run_git("commit -m 'Before rollback demo'")

    # 场景1: 手动创建回滚点并回滚
    print("\n[场景1] 手动回滚")
    print("-" * 60)

    demo_file = Path("demo_rollback.txt")
    demo_file.write_text("状态A: 初始版本\n")
    run_git("add demo_rollback.txt")
    run_git("commit -m 'Commit: 状态A'")

    print(f"初始状态: {demo_file.read_text().strip()}")

    # 修改但未提交
    demo_file.write_text("状态B: 修改但未提交\n")
    print(f"修改状态: {demo_file.read_text().strip()} (未提交)")

    # 创建回滚点
    point = engine._create_rollback_point()
    print(f"创建回滚点: {'✓ 成功' if point else '✗ 失败'}")

    # 进行一些修改
    demo_file.write_text("状态C: 操作后的修改\n")
    print(f"操作后状态: {demo_file.read_text().strip()}")

    # 回滚
    print("执行回滚...")
    success = engine._rollback_to(point)

    if success:
        print(f"✓ 回滚成功")
        print(f"回滚后状态: {demo_file.read_text().strip()}")
        print(f"✓ 验证: {'正确' if '状态B' in demo_file.read_text() else '失败'}")
    else:
        print("✗ 回滚失败")

    # 场景2: 自动回滚（模拟操作失败）
    print("\n[场景2] 自动回滚（操作失败时）")
    print("-" * 60)

    auto_file = Path("demo_auto_rollback.txt")
    auto_file.write_text("重要内容 - 已提交\n")
    run_git("add demo_auto_rollback.txt")
    run_git("commit -m 'Commit: 自动回滚测试'")

    committed_content = auto_file.read_text()
    print(f"已提交内容: {committed_content.strip()}")

    # 创建未提交更改（用于 stash）
    auto_file.write_text("工作区更改 - 将被 stash 保存\n")
    working_content = auto_file.read_text()
    rollback_point = engine._create_rollback_point()
    print(f"创建回滚点: {'✓ 成功' if rollback_point else '✗ 失败'}")

    # 注意：stash 后工作目录恢复到已提交状态
    print(f"Stash 后工作区: {auto_file.read_text().strip()}")

    # 模拟操作（会破坏文件）
    auto_file.write_text("错误内容 - 应该被回滚\n")
    print(f"操作失败后: {auto_file.read_text().strip()}")

    # 执行回滚
    print("执行自动回滚...")
    success = engine._rollback_to(rollback_point)

    if success:
        restored = auto_file.read_text()
        print(f"✓ 自动回滚成功")
        print(f"恢复后内容: {restored.strip()}")
        # 验证恢复到 stash 保存的内容
        print(f"✓ 内容验证: {'正确' if restored == working_content else '失败'}")
    else:
        print("✗ 自动回滚失败")

    # 场景3: 显示回滚策略
    print("\n[场景3] 回滚策略说明")
    print("-" * 60)

    print("""
系统采用 git stash 作为回滚机制：

1. 创建回滚点时：
   - git stash push -m "_rollback_point_TIMESTAMP"
   - 保存当前未提交的更改

2. 执行操作时：
   - 修改文件/运行代码
   - 如果测试失败，触发回滚

3. 回滚时：
   - git stash pop
   - 恢复到 stash 之前的状态

优点：
   ✓ 快速 - 不需要创建完整提交
   ✓ 安全 - 保存所有更改
   ✓ 简单 - 利用 Git 原生功能

限制：
   - 需要 Git 仓库
   - 需要工作目录干净或有可 stash 的更改
    """)

    # 清理
    print("\n[清理]")
    for f in Path(".").glob("demo_rollback*"):
        f.unlink()
    print("✓ 测试文件已清理")

    # 显示 stash 状态
    stash_result = run_git("stash list")
    stashes = stash_result.stdout.strip().split('\n') if stash_result.stdout.strip() else []
    print(f"\n剩余 stash: {len(stashes)} 个")
    if stashes:
        for s in stashes[-3:]:  # 显示最近3个
            print(f"  {s}")

    print("\n" + "=" * 60)
    print("回滚功能演示完成")
    print("=" * 60)

if __name__ == "__main__":
    demo_rollback()
