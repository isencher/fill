.PHONY: help init execute check-trust audit batch-decisions clean

help:
	@echo "自动化开发命令:"
	@echo "  make init              - 初始化项目结构"
	@echo "  make execute           - 运行执行引擎"
	@echo "  make check-trust       - 查看信任分数"
	@echo "  make audit             - 审计本周自主决策"
	@echo "  make batch-decisions   - 处理批量决策队列"
	@echo "  make clean             - 清理临时文件"

init:
	@echo "初始化自动化开发环境..."
	mkdir -p .trust .logs decisions src tests docs
	@echo "✓ 目录结构已创建"

execute:
	python3 executor.py

check-trust:
	@echo "当前信任分数:"
	@echo "=================="
	@if [ -f .trust/scores.json ]; then \
		python3 -c "import json; d=json.load(open('.trust/scores.json')); \
		import json; [print(f'{k}: {sum(h[\"success\"] for h in v[-20:])/len(v[-20:]):.1%}') \
		for k,v in d.get('operation_history',{}).items() if v]"; \
	else \
		echo "暂无数据"; \
	fi

audit:
	@echo "本周自主决策审计:"
	@echo "=================="
	@if [ -d .logs ]; then \
		find .logs -name "*.jsonl" -mtime -7 -exec cat {} \; | \
		jq -r 'select(.decision_mode == "auto") | "\(.timestamp) - \(.operation.type) - \(.success)"' | \
		sort || true; \
	fi

batch-decisions:
	@echo "当前决策队列:"
	@echo "=============="
	@if [ -d decisions ]; then \
		ls -la decisions/ 2>/dev/null || echo "队列为空"; \
	fi

clean:
	rm -rf .logs/* .trust/*.bak decisions/*.tmp
	@echo "✓ 清理完成"
