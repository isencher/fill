#!/usr/bin/env python3
"""
持续执行守护进程
监控项目变化并自动应用规则
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ContinuousExecutionHandler(FileSystemEventHandler):
    """
    监听文件变化，自动触发执行检查
    """

    def __init__(self, engine):
        self.engine = engine
        self.last_triggered = {}

    def on_modified(self, event):
        """文件修改时触发"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # 忽略临时文件和日志
        if any(skip in str(file_path) for skip in ['.git', '.logs', '__pycache__', '.pyc', '.swp']):
            return

        # 防抖：避免同一个文件频繁触发
        now = time.time()
        if file_path in self.last_triggered and now - self.last_triggered[file_path] < 2:
            return
        self.last_triggered[file_path] = now

        print(f"\n[检测变化] {file_path}")

        # 根据文件类型决定操作
        operation = self._infer_operation(file_path)
        if operation:
            result = self.engine.execute(operation)
            print(f"[自动处理] {result['status']}")

    def _infer_operation(self, file_path: Path) -> dict:
        """根据文件路径推断操作类型"""
        path_str = str(file_path)

        # 文档修改 -> 自动执行
        if path_str.endswith('.md'):
            return {
                "type": "update_documentation",
                "description": f"更新文档: {file_path.name}",
                "file_path": path_str
            }

        # 测试文件 -> 自动执行
        if 'tests' in path_str or path_str.endswith('_test.py'):
            return {
                "type": "add_function",
                "description": f"测试相关: {file_path.name}",
                "file_path": path_str
            }

        # 核心文件 -> 需要人工
        if 'src/core' in path_str:
            return {
                "type": "modify_core_logic",
                "description": f"核心文件修改: {file_path.name}",
                "file_path": path_str
            }

        # 工具文件 -> 通知
        if 'src/utils' in path_str or 'helpers' in path_str:
            return {
                "type": "add_function",
                "description": f"工具函数: {file_path.name}",
                "file_path": path_str
            }

        return None


class ContinuousRunner:
    """
    持续运行器 - 确保规则持续生效
    """

    def __init__(self, watch_paths=None):
        from executor import ExecutorEngine
        self.engine = ExecutorEngine()
        self.watch_paths = watch_paths or ["src", "tests", "docs"]
        self.observer = Observer()

    def start(self):
        """启动持续监控"""
        print("启动自动化开发守护进程...")
        print(f"监控目录: {', '.join(self.watch_paths)}")
        print("按 Ctrl+C 停止\n")

        handler = ContinuousExecutionHandler(self.engine)

        for path in self.watch_paths:
            if Path(path).exists():
                self.observer.schedule(handler, path, recursive=True)

        self.observer.start()

        try:
            while True:
                # 定期检查决策队列
                if len(self.engine.decision_queue) > 0:
                    print(f"\n[待处理] 决策队列: {len(self.engine.decision_queue)} 项")

                time.sleep(10)
        except KeyboardInterrupt:
            self.observer.stop()
            print("\n\n守护进程已停止")

        self.observer.join()

    def start_batch_mode(self):
        """批量处理模式 - 定时触发"""
        print("批量处理模式启动...")

        while True:
            # 执行队列中的操作
            print(f"\n检查决策队列... ({len(self.engine.decision_queue)} 项待处理)")

            # 如果达到阈值，触发人类审批
            if len(self.engine.decision_queue) >= self.engine.rules["batching"]["max_queue_size"]:
                print("\n" + "="*50)
                print("决策队列已满，需要人工审批:")
                print("="*50)
                for i, item in enumerate(self.engine.decision_queue, 1):
                    op = item["operation"]
                    print(f"{i}. {op['type']}: {op.get('description', '')}")

                print("\n处理选项:")
                print("  1. 批准全部")
                print("  2. 逐个审查")
                print("  3. 跳过")

                choice = input("\n选择 [1-3]: ").strip()

                if choice == "1":
                    # 批准全部
                    for item in self.engine.decision_queue:
                        self.engine.execute(item["operation"])
                    self.engine.decision_queue.clear()
                elif choice == "2":
                    # 逐个审查
                    self.engine._present_batch_decisions()
                else:
                    print("跳过本次处理")

            time.sleep(60)  # 每分钟检查一次


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="持续执行自动化开发规则")
    parser.add_argument("--mode", choices=["watch", "batch"], default="watch",
                        help="运行模式: watch(监控) 或 batch(批量)")
    parser.add_argument("--paths", nargs="+", default=["src", "tests", "docs"],
                        help="要监控的目录路径")

    args = parser.parse_args()

    runner = ContinuousRunner(watch_paths=args.paths)

    if args.mode == "watch":
        runner.start()
    else:
        runner.start_batch_mode()
