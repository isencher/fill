#!/usr/bin/env python3
"""
测试回滚功能
"""

import subprocess
from pathlib import Path
from executor import ExecutorEngine

def run_git(cmd):
    """运行 git 命令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result

def test_rollback():
    print("=" * 60)
    print("回滚功能测试")
    print("=" * 60)

    # 清理环境
    for f in ["test_file.txt", "test_rollback.txt"]:
        if Path(f).exists():
            Path(f).unlink()

    # 初始化 git 并创建初始提交
    print("\n[步骤1] 初始化 Git 仓库并创建基础提交")
    run_git("add -A")
    run_git("commit -m 'Initial commit'")

    # 创建初始文件
    Path("test_file.txt").write_text("原始内容\n")
    run_git("add test_file.txt")
    run_git("commit -m 'Add test file'")

    print(f"✓ 初始状态: {Path('test_file.txt').read_text().strip()}")

    # 创建引擎
    engine = ExecutorEngine()

    # 测试1: 成功的操作不应该回滚
    print("\n[步骤2] 测试成功操作（不触发回滚）")
    result = engine.execute({
        "type": "add_function",
        "description": "测试成功操作",
        "file_path": "test_success.py"
    })
    print(f"结果: {result['status']}")
    print(f"文件已创建: {Path('test_success.py').exists()}")

    # 测试2: 模拟失败的操作
    print("\n[步骤3] 测试失败操作（触发回滚）")

    # 修改测试文件
    Path("test_rollback.txt").write_text("这应该被回滚\n")
    run_git("add test_rollback.txt")
    run_git("commit -m 'Before rollback test'")

    print(f"修改前: {Path('test_rollback.txt').read_text().strip()}")

    # 手动测试回滚点创建
    print("\n[步骤3.1] 创建回滚点")
    rollback_point = engine._create_rollback_point()
    if rollback_point:
        print(f"✓ 回滚点创建成功: {rollback_point}")
    else:
        print("✗ 回滚点创建失败（可能没有可暂存的更改）")

    # 创建一些更改
    Path("test_rollback.txt").write_text("修改后的内容 - 应该被回滚\n")
    print(f"修改后: {Path('test_rollback.txt').read_text().strip()}")

    # 执行回滚
    print("\n[步骤3.2] 执行回滚")
    if rollback_point:
        success = engine._rollback_to(rollback_point)
        if success:
            print(f"✓ 回滚成功")
            print(f"回滚后: {Path('test_rollback.txt').read_text().strip()}")
        else:
            print("✗ 回滚失败")

    # 测试3: 测试自动回滚（模拟操作失败）
    print("\n[步骤4] 测试操作失败时的自动回滚")

    # 保存当前内容
    original_content = "自动回滚测试 - 原始内容\n"
    Path("auto_rollback_test.txt").write_text(original_content)
    run_git("add auto_rollback_test.txt")
    run_git("commit -m 'Before auto rollback test'")

    print(f"原始内容: {original_content.strip()}")

    # 创建一个会失败的操作模拟
    # 我们需要临时修改 _measure_result 来返回 False
    import types

    original_measure = engine._measure_result
    def failing_measure(self, operation, result):
        # 只对这个特定操作返回 False
        if "should_fail" in operation.get("description", ""):
            print("  [模拟] 测量结果: 失败")
            return False
        return original_measure(operation, result)

    # 绑定方法
    engine._measure_result = types.MethodType(failing_measure, engine)

    # 执行会失败的操作
    result = engine.execute({
        "type": "add_function",
        "description": "这个操作应该失败",
        "file_path": "auto_rollback_test.txt"  # 覆盖现有文件
    })

    # 恢复原始方法
    engine._measure_result = original_measure

    print(f"操作结果: {result['status']}")

    # 检查文件是否被回滚
    if Path("auto_rollback_test.txt").exists():
        current_content = Path("auto_rollback_test.txt").read_text()
        print(f"文件内容: {current_content.strip()}")
        if current_content == original_content:
            print("✓ 自动回滚成功 - 文件已恢复")
        else:
            print("✗ 自动回滚失败 - 文件内容已改变")
    else:
        print("✗ 文件被删除（回滚失败）")

    # 清理
    print("\n[清理] 测试文件")
    for f in ["test_file.txt", "test_success.py", "test_rollback.txt", "auto_rollback_test.txt"]:
        if Path(f).exists():
            Path(f).unlink()

    # 检查 git stash 状态
    stash_list = run_git("stash list")
    print(f"\nGit stash 状态:")
    if stash_list.stdout.strip():
        for line in stash_list.stdout.strip().split('\n'):
            print(f"  {line}")
    else:
        print("  (无 stash)")

    print("\n" + "=" * 60)
    print("回滚功能测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_rollback()
