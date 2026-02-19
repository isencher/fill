# Git 提交规范

## Conventional Commits 格式

Fill 项目遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

### 提交消息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具链相关
- `perf`: 性能优化
- `ci`: CI 配置

### 示例

```bash
# 简单提交
git commit -m "feat: add file upload endpoint"

# 带描述的提交
git commit -m "fix: resolve memory leak in batch processor

The batch processor was not properly cleaning up resources
after processing large files, causing memory accumulation.
This commit fixes the issue by ensuring proper cleanup."

# 带破坏性变更的提交
git commit -m "feat: change API response format

BREAKING CHANGE: The API response format has changed from
{'data': {...}} to {...}. Clients need to update their code."
```

---

## ⚠️ 禁止使用 Co-Authored-By

### 规则
**严禁在提交消息中使用 `Co-Authored-By:`**。

### ❌ 错误示例
```bash
git commit -m "feat: add new feature

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Co-Authored-By: Another Developer <email@example.com>"
```

### ✅ 正确示例
```bash
git commit -m "feat: add new feature

Description of the feature and implementation details.

The feature includes:
- Automatic field mapping
- Confidence indicators
- Manual override support

Testing:
- Added 15 new unit tests
- Integration tests pass
- E2E tests validated"
```

### 原因

1. **明确的责任归属**
   - 每个提交应该有明确的单一作者
   - 便于追踪问题和代码审查
   - 清晰的贡献历史

2. **简化工作流程**
   - 减少提交消息的复杂性
   - 避免作者归属争议
   - 更清晰的 Git 历史

3. **项目规范**
   - Fill 项目采用严格的作者责任制度
   - 所有贡献都应该有明确的来源
   - 便于维护和长期发展

---

## 例外情况

### 何时可以使用 Co-Authored-By

只有在以下**所有条件**都满足时，才允许使用 `Co-Authored-By`：

1. **真实的多人协作**
   - 两个或更多开发者**同时**在同一个功能上工作
   - 每个人的贡献量相当（各占约 50%）
   - 不是简单的代码审查或建议

2. **明确的工作分工**
   - 每个作者负责不同的部分
   - 可以明确区分各自的工作
   - 双方都同意共同署名

3. **提交前沟通**
   - 在提交前已经达成共识
   - 双方都了解并认可共同署名
   - 有书面或聊天记录证明协作

### 例外示例

```bash
# ✅ 可以使用 Co-Authored-By 的情况
# Alice 实现了核心逻辑，Bob 实现了错误处理
# 两人在同一个分支上协作，各占约 50% 工作量
git commit -m "feat: implement batch processing with error handling

Co-Authored-By: Alice <alice@example.com>
Co-Authored-By: Bob <bob@example.com>"

# ❌ 不应该使用 Co-Authored-By 的情况
# Bob 只是帮 Alice 审查了代码
git commit -m "feat: implement batch processing

Co-Authored-By: Alice <alice@example.com>
Co-Authored-By: Bob <bob@example.com>"

# 正确做法：只有 Alice 署名
git commit -m "feat: implement batch processing

Reviewed-by: Bob <bob@example.com>"
```

---

## 检查清单

提交前请确认：

- [ ] 提交消息遵循 Conventional Commits 格式
- [ ] Type 类型选择正确（feat/fix/docs/refactor等）
- [ ] Subject 清晰描述变更内容
- [ ] Body（如果需要）包含足够的细节
- [ ] **没有使用 Co-Authored-By**（除非满足例外条件）
- [ ] 破坏性变更使用 BREAKING CHANGE 标记
- [ ] 代码已通过所有测试
- [ ] 文档已同步更新

---

## 强制执行

### Git Hook（可选）

项目提供了 pre-commit hook 来检查提交消息格式。

```bash
# 安装 Git hooks
cp .git_hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

### 手动检查

提交前手动检查：

```bash
# 查看即将提交的消息
git commit -v

# 如果消息格式不正确，取消并重写
# (编辑器打开后，修改消息保存)
```

---

## 常见问题

### Q: AI 辅助生成的代码需要 Co-Authored-By 吗？

**A**: 不需要。AI 是工具，不是协作者。你作为开发者对提交的代码负全部责任。

**正确做法**:
```bash
git commit -m "feat: add data validation

Implemented input validation for all user-facing endpoints.
Validation includes type checking, range validation, and format checks."
```

### Q: 我参考了别人的代码怎么办？

**A**: 在提交消息的 Body 中说明参考来源即可。

**正确做法**:
```bash
git commit -m "feat: add fuzzy matching algorithm

Implementation inspired by the approach in
https://github.com/example/project but completely
rewritten for our use case."
```

### Q: 代码审查者需要署名吗？

**A**: 不需要。审查者可以在 Body 中提及，但不使用 Co-Authored-By。

**正确做法**:
```bash
git commit -m "fix: resolve memory leak

Fixed by ensuring proper cleanup in batch processor.
Reviewed-by: John Doe <john@example.com>"
```

---

## 模板

### 功能开发
```bash
git commit -m "feat: add automatic field mapping

Implement intelligent field matching between CSV columns
and template placeholders using fuzzy matching algorithm.

Features:
- Confidence-based matching (high/medium/low)
- Manual override capability
- Real-time preview

Testing:
- Added 25 unit tests
- Integration tests validated
- E2E tests pass"
```

### Bug 修复
```bash
git commit -m "fix: resolve file upload timeout

Fixed timeout issue when uploading large files by
implementing chunked upload and progress tracking.

Root cause: Synchronous file reading blocked event loop
Solution: Async file I/O with progress callbacks

Testing:
- Verified with 10MB files
- Tested slow network conditions
- All existing tests pass"
```

### 文档更新
```bash
git commit -m "docs: update API documentation with examples

Added comprehensive examples for all endpoints including:
- Request/response formats
- Error scenarios
- Authentication requirements
- Rate limiting information"
```

---

**版本**: 1.0
**最后更新**: 2026-02-19
**状态**: ✅ 生效中
