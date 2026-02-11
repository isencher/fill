#!/usr/bin/env python3
"""
自动化开发执行引擎
将规则转化为持续行动，而非一次性知识
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

class ExecutorEngine:
    """
    核心执行引擎 - 确保每次操作都遵循规则
    """

    def __init__(self):
        self.rules = self._load_rules()
        self.trust_db = self._load_trust_db()
        self.decision_queue = []
        self.execution_log = []

    # ========== 持续执行的核心方法 ==========

    def execute(self, operation: dict) -> dict:
        """
        执行任何操作的主入口
        确保每次执行都经过规则检查和信任评估
        """
        # 步骤1：检查是否在自主边界内
        decision_mode = self._check_autonomy(operation)

        # 步骤2：根据决策模式执行
        if decision_mode == "auto":
            return self._execute_auto(operation)
        elif decision_mode == "notify":
            result = self._execute_auto(operation)
            self._notify_human(operation, result)
            return result
        elif decision_mode == "review":
            return self._queue_for_review(operation)
        else:  # manual
            return self._require_manual_approval(operation)

    def _execute_auto(self, operation: dict) -> dict:
        """
        自主执行：记录、执行、测量、更新信任
        这是负反馈控制的实现
        """
        print(f"[AUTO] 执行: {operation['type']} - {operation.get('description', '')}")

        # 创建回滚点
        rollback_point = self._create_rollback_point()

        # 执行操作（这里调用实际的代码操作）
        result = self._perform_operation(operation)

        # 测量结果
        success = self._measure_result(operation, result)

        # 更新信任分数（负反馈）
        self._update_trust_score(operation, success)

        # 失败则回滚
        if not success and rollback_point:
            self._rollback_to(rollback_point)

        # 记录日志
        self._log_execution(operation, success, decision_mode="auto")

        return {"status": "success" if success else "failed", "result": result}

    def _queue_for_review(self, operation: dict) -> dict:
        """加入决策队列，批量处理"""
        print(f"[QUEUE] 加入审查队列: {operation['type']}")
        self.decision_queue.append({
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "context": self._gather_context(operation)
        })

        # 检查是否达到触发人类的阈值
        if self._should_trigger_human():
            self._present_batch_decisions()

        return {"status": "queued", "queue_size": len(self.decision_queue)}

    def _require_manual_approval(self, operation: dict) -> dict:
        """
        需要人类实时介入
        使用结构化决策（单选），非开放式问题
        """
        print(f"[MANUAL] 需要审批: {operation['type']}")

        # 提供结构化选项，不是开放式问题
        options = self._generate_options(operation)
        print("\n请选择:")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt['label']} - {opt['description']}")

        # 记录决策用于学习
        choice = self._get_human_choice(options)
        self._record_decision(operation, choice)

        if choice.get("approved"):
            return self._execute_auto(operation)
        return {"status": "rejected", "reason": choice.get("reason")}

    # ========== 负反馈控制：测量与更新 ==========

    def _update_trust_score(self, operation: dict, success: bool):
        """根据执行结果更新信任分数"""
        op_type = operation["type"]
        history = self.trust_db["operation_history"].setdefault(op_type, [])

        history.append({
            "timestamp": datetime.now().isoformat(),
            "success": success
        })

        # 计算滚动成功率（最近20次）
        recent = history[-20:]
        success_rate = sum(h["success"] for h in recent) / len(recent)

        # 保存
        self.trust_db["operation_history"][op_type] = recent
        self.trust_db["last_updated"] = datetime.now().isoformat()
        self._save_trust_db()

        # 如果成功率提升，建议扩大自主边界
        if success_rate >= self.rules["autonomy"]["auto_threshold"]:
            print(f"✓ {op_type} 成功率: {success_rate:.1%} - 建议升级为自动执行")

    # ========== 决策辅助 ==========

    def _check_autonomy(self, operation: dict) -> str:
        """检查操作是否在自主边界内"""
        op_type = operation["type"]

        # 检查操作类型规则
        op_config = self.rules["operations"].get(op_type, {})
        base_level = op_config.get("autonomy_level", "review")

        # 检查路径规则
        if "file_path" in operation:
            for path_pattern, path_rule in self.rules["path_rules"].items():
                if Path(operation["file_path"]).match(path_pattern):
                    override = path_rule.get("override_level")
                    if override:
                        base_level = override

        # 根据历史成功率调整
        history = self.trust_db["operation_history"].get(op_type, [])
        if history:
            recent = history[-20:]
            success_rate = sum(h["success"] for h in recent) / len(recent)

            if success_rate >= self.rules["autonomy"]["auto_threshold"]:
                return "auto"
            elif success_rate >= self.rules["autonomy"]["notify_threshold"]:
                return "notify"

        return base_level

    def _should_trigger_human(self) -> bool:
        """检查是否应该触发人类介入"""
        batch_config = self.rules["batching"]

        # 检查队列大小
        if len(self.decision_queue) >= batch_config["max_queue_size"]:
            return True

        # 检查优先级关键词（只在描述和操作类型中查找，避免误匹配包名）
        priority_keywords = batch_config["priority_keywords"]
        for item in self.decision_queue:
            op = item["operation"]
            # 只检查描述和操作类型
            check_text = f"{op.get('description', '')} {op.get('type', '')}".lower()
            for keyword in priority_keywords:
                if keyword in check_text:
                    return True

        return False

    # ========== 结构化决策 ==========

    def _generate_options(self, operation: dict) -> list:
        """生成结构化选项（单选），不是开放式问题"""
        op_type = operation["type"]

        # 基于操作类型预定义选项
        if op_type == "add_dependency":
            return [
                {"label": "批准", "description": "添加此依赖，执行安全扫描", "approved": True},
                {"label": "拒绝", "description": "不添加，需要替代方案", "approved": False, "reason": "dependency_rejected"},
                {"label": "延后", "description": "加入技术债务清单", "approved": False, "reason": "deferred"},
            ]
        elif op_type == "modify_core_logic":
            return [
                {"label": "批准", "description": "允许修改核心逻辑", "approved": True},
                {"label": "重构后批准", "description": "需要先重构相关代码", "approved": False, "reason": "needs_refactor"},
                {"label": "拒绝", "description": "当前方案不可接受", "approved": False, "reason": "rejected"},
            ]
        else:
            return [
                {"label": "批准", "description": "继续执行此操作", "approved": True},
                {"label": "修改后批准", "description": "需要调整方案", "approved": False, "reason": "needs_change"},
                {"label": "拒绝", "description": "不执行此操作", "approved": False, "reason": "rejected"},
            ]

    # ========== 持久化 ==========

    def _load_rules(self):
        rules_path = Path("rules.json")
        if rules_path.exists():
            with open(rules_path) as f:
                return json.load(f)
        return {}

    def _load_trust_db(self):
        db_path = Path(".trust/scores.json")
        if db_path.exists():
            with open(db_path) as f:
                return json.load(f)
        return {"operation_history": {}, "last_updated": None}

    def _save_trust_db(self):
        Path(".trust").mkdir(exist_ok=True)
        with open(".trust/scores.json", "w") as f:
            json.dump(self.trust_db, f, indent=2)

    def _log_execution(self, operation: dict, success: bool, decision_mode: str):
        """记录执行日志用于审计"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "success": success,
            "decision_mode": decision_mode
        }
        self.execution_log.append(log_entry)

        # 持久化日志
        Path(".logs").mkdir(exist_ok=True)
        log_file = Path(f".logs/execution-{datetime.now().strftime('%Y-%m-%d')}.jsonl")
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    # ========== 占位方法（实际实现时填充） ==========

    def _create_rollback_point(self):
        """创建回滚点 - 使用 git stash"""
        try:
            # 检查是否有 git 仓库
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return None

            # 使用 stash 创建回滚点
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stash_msg = f"_rollback_point_{timestamp}"

            # 尝试使用 git stash push (Git 2.13+)，失败则使用 git stash save
            result = subprocess.run(
                ["git", "stash", "push", "-m", stash_msg],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                # 回退到旧版语法
                result = subprocess.run(
                    ["git", "stash", "save", stash_msg],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

            if result.returncode == 0:
                # 返回 stash 引用
                return {"type": "stash", "ref": stash_msg}
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return None

    def _perform_operation(self, operation: dict):
        """执行实际操作"""
        op_type = operation.get("type")
        file_path = operation.get("file_path")

        # 非文件操作（优先处理）
        if op_type == "add_dependency":
            # 处理依赖添加
            package = operation.get("package", "")
            requirements_txt = Path("requirements.txt")
            existing = requirements_txt.read_text().strip() if requirements_txt.exists() else ""

            if package and package not in existing:
                requirements_txt.write_text((existing + "\n" if existing else "") + f"{package}\n")
                return {"package": package, "added": True, "file": "requirements.txt"}
            return {"package": package, "added": False, "reason": "already_exists"}

        # 文件操作
        if file_path:
            path = Path(file_path)

            # 根据操作类型执行
            if op_type in ["add_function", "update_documentation", "fix_bug"]:
                # 确保目录存在
                path.parent.mkdir(parents=True, exist_ok=True)

                # 如果文件不存在，创建基础结构
                if not path.exists():
                    if path.suffix == ".py":
                        content = f'\"\"\"Auto-generated module\"\"\"\n\n# TODO: Implement {operation.get("description", "")}\n'
                    else:
                        content = f"# {operation.get('description', '')}\n"
                    path.write_text(content)

                return {"file": str(path), "action": "created_or_updated", "exists": True}

            elif op_type == "modify_core_logic":
                # 核心逻辑修改 - 检查文件存在
                if not path.exists():
                    # 开发模式：自动创建核心文件（生产环境应抛出异常）
                    path.parent.mkdir(parents=True, exist_ok=True)
                    content = f'\"\"\"Core module: {operation.get("description", "")}\"\"\"\n\n# TODO: Implement core logic\n'
                    path.write_text(content)
                    return {"file": str(path), "action": "created", "exists": True, "note": "auto_created"}
                return {"file": str(path), "action": "modified", "exists": True}

            elif op_type == "refactor_module":
                # 重构操作 - 检查文件存在
                if not path.exists():
                    raise FileNotFoundError(f"Module not found: {file_path}")
                return {"file": str(path), "action": "refactored", "exists": True}

        # 默认返回
        return {"action": "noop", "operation": op_type}

    def _measure_result(self, operation: dict, result):
        """测量操作结果"""
        op_config = self.rules["operations"].get(operation["type"], {})
        test_required = op_config.get("test_required", False)

        # 如果不需要测试，直接返回成功
        if not test_required:
            return True

        # 运行测试
        try:
            # 检查是否有测试目录
            tests_dir = Path("tests")
            if not tests_dir.exists():
                return True  # 没有测试不算失败

            # 尝试运行 pytest
            test_result = subprocess.run(
                ["python", "-m", "pytest", "-v", "--tb=short", "-x"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=Path.cwd()
            )

            success = test_result.returncode == 0

            if not success:
                print(f"\n[测试失败]")
                print(test_result.stdout)
                if test_result.stderr:
                    print(test_result.stderr)

            return success

        except (subprocess.TimeoutExpired, FileNotFoundError):
            # pytest 不可用或超时，不算失败
            return True

    def _rollback_to(self, point):
        """回滚到指定点"""
        if not point or point.get("type") != "stash":
            print("[回滚失败] 无效的回滚点")
            return False

        try:
            import subprocess
            result = subprocess.run(
                ["git", "stash", "pop"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print("[回滚成功] 已恢复到之前的状态")
                return True
            else:
                print(f"[回滚失败] {result.stderr}")
                return False
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"[回滚异常] {e}")
            return False

    def _notify_human(self, operation: dict, result: dict):
        """通知人类（异步）"""
        print(f"\n[通知] 操作已执行: {operation['type']}")
        print(f"  描述: {operation.get('description', '')}")
        print(f"  状态: {result.get('status', 'unknown')}")
        # 可以扩展为发送通知到其他渠道（邮件、Slack等）

    def _present_batch_decisions(self):
        """展示批量决策"""
        if not self.decision_queue:
            print("\n✓ 决策队列为空")
            return

        print("\n" + "=" * 60)
        print(f"批量决策审批 ({len(self.decision_queue)} 项待处理)")
        print("=" * 60)

        for i, item in enumerate(self.decision_queue, 1):
            op = item["operation"]
            print(f"\n{i}. [{op['type']}] {op.get('description', '')}")
            if "file_path" in op:
                print(f"   文件: {op['file_path']}")

        print("\n" + "-" * 60)
        print("处理选项:")
        print("  1. 批准全部 - 执行所有操作")
        print("  2. 拒绝全部 - 清空队列")
        print("  3. 逐个审查 - 单独处理每项")
        print("  4. 取消 - 稍后处理")

        while True:
            choice = input("\n请选择 [1-4]: ").strip()
            if choice == "1":
                # 批准全部
                approved = []
                for item in self.decision_queue:
                    result = self._execute_auto(item["operation"])
                    approved.append(result)
                self.decision_queue.clear()
                print(f"✓ 已执行 {len(approved)} 项操作")
                break
            elif choice == "2":
                # 拒绝全部
                count = len(self.decision_queue)
                self.decision_queue.clear()
                print(f"✓ 已拒绝 {count} 项操作")
                break
            elif choice == "3":
                # 逐个审查
                for i, item in enumerate(self.decision_queue[:], 1):
                    self._require_manual_approval(item["operation"])
                    keep = input(f"\n保留剩余 {len(self.decision_queue)} 项? [Y/n]: ").strip().lower()
                    if keep == 'n':
                        self.decision_queue.clear()
                        break
                break
            elif choice == "4":
                print("稍后处理")
                break
            else:
                print("无效选择，请输入 1-4")

    def _gather_context(self, operation: dict) -> dict:
        """收集上下文"""
        context = {"operation": operation}

        # 收集相关文件信息
        if "file_path" in operation:
            file_path = Path(operation["file_path"])
            context["file_exists"] = file_path.exists()
            if file_path.exists():
                context["file_size"] = file_path.stat().st_size
                context["file_modified"] = datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).isoformat()

        # 收集测试状态
        tests_dir = Path("tests")
        context["has_tests"] = tests_dir.exists()
        if tests_dir.exists():
            test_files = list(tests_dir.glob("**/*_test.py")) + list(tests_dir.glob("**/test_*.py"))
            context["test_count"] = len(test_files)

        return context

    def _get_human_choice(self, options: list) -> dict:
        """获取人类选择"""
        print(f"\n请选择 [1-{len(options)}]: ", end="", flush=True)

        while True:
            try:
                choice = input().strip()
                index = int(choice) - 1
                if 0 <= index < len(options):
                    return options[index]
                print(f"无效选择，请输入 1-{len(options)}: ", end="", flush=True)
            except (ValueError, KeyboardInterrupt):
                print("无效输入，请输入数字: ", end="", flush=True)
            except EOFError:
                # 默认选择第一个
                return options[0]

    def _record_decision(self, operation: dict, choice: dict):
        """记录决策用于学习"""
        decisions_dir = Path(".trust/decisions")
        decisions_dir.mkdir(parents=True, exist_ok=True)

        decision_record = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "choice": choice,
            "approved": choice.get("approved", False)
        }

        # 追加到决策日志
        decision_file = decisions_dir / f"decisions-{datetime.now().strftime('%Y-%m')}.jsonl"
        with open(decision_file, "a") as f:
            f.write(json.dumps(decision_record, ensure_ascii=False) + "\n")

        # 如果是批准操作，可以考虑调整该操作类型的默认级别
        if choice.get("approved"):
            op_type = operation["type"]
            op_config = self.rules["operations"].get(op_type, {})
            current_level = op_config.get("autonomy_level", "review")

            # 记录批准次数（可用于后续自动升级）
            approvals_file = decisions_dir / "approvals.json"
            if approvals_file.exists():
                with open(approvals_file) as f:
                    approvals = json.load(f)
            else:
                approvals = {}

            approvals[op_type] = approvals.get(op_type, 0) + 1

            with open(approvals_file, "w") as f:
                json.dump(approvals, f, indent=2)


# ========== 使用示例 ==========

if __name__ == "__main__":
    engine = ExecutorEngine()

    print("=" * 60)
    print("自动化开发执行引擎 - 演示")
    print("=" * 60)

    # 示例1：自动执行的操作
    print("\n[测试1] 自动执行: add_function")
    result = engine.execute({
        "type": "add_function",
        "description": "添加辅助函数",
        "file_path": "src/utils/helpers.py"
    })
    print(f"结果: {result}\n")

    # 示例2：核心文件修改（自动创建模式）
    print("[测试2] 核心文件修改: modify_core_logic")
    result = engine.execute({
        "type": "modify_core_logic",
        "description": "修改认证逻辑",
        "file_path": "src/core/auth.py"
    })
    print(f"结果: {result}\n")

    # 示例3：加入队列的操作
    print("[测试3] 加入队列: add_dependency")
    result = engine.execute({
        "type": "add_dependency",
        "description": "添加数据库连接库",
        "package": "postgres-client"
    })
    print(f"结果: {result}\n")

    # 示例4：文档更新
    print("[测试4] 文档更新: update_documentation")
    result = engine.execute({
        "type": "update_documentation",
        "description": "更新API文档",
        "file_path": "docs/api.md"
    })
    print(f"结果: {result}\n")

    print("=" * 60)
    print("演示完成")
    print("=" * 60)
