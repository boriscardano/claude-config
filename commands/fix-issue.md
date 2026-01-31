---
name: fix-issue
description: Quick fix for a GitHub issue without full worktree workflow
---

Fix GitHub issue #$ARGUMENTS with minimal overhead:

## Phase 0: Create Task Plan

Before any work, create a task for tracking:
- Use TaskCreate to create a task for this issue fix
- Update task status as you progress (in_progress -> completed)

## Workflow

1. **Fetch issue**: `gh issue view $ARGUMENTS --json title,body,labels`
2. **Create branch**: `git checkout -b fix/issue-$ARGUMENTS`
3. **Analyze and implement the fix**
4. **Run tests**: `uv run pytest`
5. **Run lint**: `uv run ruff check --fix .`
6. **Commit with conventional message**
7. **Push and create PR**

Keep it simple - no worktrees, no parallel agents. For complex issues, use /implement-issue instead.

Current issue: $ARGUMENTS
