#!/usr/bin/env python3
"""
测试回滚功能 - 完整版
"""

import subprocess
from pathlib import Path
from executor import ExecutorEngine

def run_git(cmd):
    """运行 git 命令"""
    result = subprocess.run(f"git {cmd}", shell=True, capture_output=True, text=True)
    return result

def test_rollback_comprehensive():
    print("=" * 60)
    print("回滚功能完整测试")
    print("=" * 60)

    engine = ExecutorEngine()

    # 清理并初始化
    print("\n[准备] 清理并初始化 Git 仓库")
    for f in Path(".").glob("rollback_test*"):
        f.unlink()

    # 提交现有更改
    run_git("add -A")
    run_git("commit -m 'Setup before rollback test'")

    # 测试1: 回滚点创建和手动回滚
    print("\n" + "=" * 60)
    print("测试1: 回滚点创建和手动回滚")
    print("=" * 60)

    # 创建初始文件
    test_file = Path("rollback_test_manual.txt")
    test_file.write_text("版本1 - 原始内容\n")
    run_git("add rollback_test_manual.txt")
    run_git("commit -m 'Initial: rollback test file'")

    print(f"步骤1: 初始内容 = '{test_file.read_text().strip()}'")

    # 创建未提交的更改（这样 stash 才能工作）
    test_file.write_text("版本2 - 修改后的内容\n")
    print(f"步骤2: 修改后内容 = '{test_file.read_text().strip()}' (未提交)")

    # 创建回滚点
    print("步骤3: 创建回滚点...")
    rollback_point = engine._create_rollback_point()

    if rollback_point:
        print(f"✓ 回滚点创建成功: {rollback_point}")

        # 修改文件以模拟操作
        test_file.write_text("版本3 - 操作失败后的内容\n")
        print(f"步骤4: 操作后内容 = '{test_file.read_text().strip()}'")

        # 执行回滚
        print("步骤5: 执行回滚...")
        success = engine._rollback_to(rollback_point)

        if success:
            restored = test_file.read_text().strip()
            print(f"✓ 回滚成功")
            print(f"步骤6: 回滚后内容 = '{restored}'")

            if restored == "版本2 - 修改后的内容":
                print("✓ 内容正确恢复到 stash 之前的状态")
            else:
                print(f"✗ 内容不匹配，预期 '版本2 - 修改后的内容'")
        else:
            print("✗ 回滚失败")
    else:
        print("✗ 回滚点创建失败")

    # 测试2: 自动回滚（操作失败时）
    print("\n" + "=" * 60)
    print("测试2: 操作失败时的自动回滚")
    print("=" * 60)

    # 创建测试文件
    auto_test_file = Path("rollback_test_auto.txt")
    original_content = "原始内容 - 不应该被破坏\n"
    auto_test_file.write_text(original_content)
    run_git("add rollback_test_auto.txt")
    run_git("commit -m 'Initial: auto rollback test'")

    print(f"步骤1: 原始内容 = '{original_content.strip()}'")

    # 临时修改 _measure_result 使其返回失败
    import types
    original_measure = engine._measure_result

    call_count = [0]
    def failing_measure(self, operation, result):
        call_count[0] += 1
        # 第一次调用返回 True（创建回滚点成功）
        # 第二次调用返回 False（测量失败）
        if call_count[0] >= 2:
            print("  [模拟] 测量结果: 失败")
            return False
        return True

    engine._measure_result = types.MethodType(failing_measure, engine)

    # 创建未提交更改（用于 stash）
    auto_test_file.write_text("临时修改 - 用于 stash\n")
    rollback_point = engine._create_rollback_point()
    print(f"步骤2: 创建回滚点 = {rollback_point is not None}")

    # 执行会失败的操作
    print("步骤3: 执行会失败的操作...")
    result = engine.execute({
        "type": "add_function",
        "description": "测试自动回滚",
        "file_path": "rollback_test_auto.txt"
    })

    # 恢复原始方法
    engine._measure_result = original_measure

    print(f"操作结果: {result['status']}")

    # 检查文件内容
    if auto_test_file.exists():
        current = auto_test_file.read_text().strip()
        print(f"步骤4: 文件内容 = '{current}'")

        # 验证回滚是否成功
        if current == "临时修改 - 用于 stash":
            print("✓ 自动回滚成功 - 文件已恢复到 stash 之前的状态")
        elif current == original_content.strip():
            print("⚠ 文件保持原内容（可能回滚点未正确创建）")
        else:
            print(f"✗ 回滚失败 - 内容被修改为 '{current}'")
    else:
        print("✗ 文件被删除")

    # 测试3: 连续操作和回滚
    print("\n" + "=" * 60)
    print("测试3: 多次回滚")
    print("=" * 60)

    multi_test = Path("rollback_test_multi.txt")
    multi_test.write_text("初始状态\n")
    run_git("add rollback_test_multi.txt")
    run_git("commit -m 'Initial: multi rollback test'")

    versions = []
    for i in range(3):
        # 修改文件
        multi_test.write_text(f"版本{i+1}\n")
        print(f"  修改为: 版本{i+1}")

        # 创建回滚点
        point = engine._create_rollback_point()
        print(f"  创建回滚点: {point is not None}")

        if point:
            versions.append((point, f"版本{i+1}"))

    # 回滚到第一个版本
    if versions:
        print(f"\n当前内容: '{multi_test.read_text().strip()}'")
        print(f"回滚到 '{versions[0][1]}'...")

        success = engine._rollback_to(versions[0][0])
        if success:
            restored = multi_test.read_text().strip()
            print(f"✓ 回滚成功，内容: '{restored}'")
        else:
            print("✗ 回滚失败")

    # 清理测试文件
    print("\n[清理] 移除测试文件")
    for f in Path(".").glob("rollback_test*"):
        f.unlink()

    # 显示 stash 状态
    stash_result = run_git("stash list")
    print(f"\n剩余 stash 条目: {len(stash_result.stdout.strip().split(chr(10))) if stash_result.stdout.strip() else 0}")

    print("\n" + "=" * 60)
    print("回滚功能测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_rollback_comprehensive()
