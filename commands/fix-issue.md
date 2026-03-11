---
name: fix-issue
description: Quick fix for a GitHub issue without full worktree workflow
---

Fix GitHub issue #$ARGUMENTS with minimal overhead.

## Phase 0: Task Plan

Create a single task with TaskCreate for tracking this fix. Update status as you progress.

## Phase 1: Fetch & Understand

1. **Fetch issue details**:
   ```bash
   gh issue view $ARGUMENTS --json title,body,labels,comments
   ```

2. **Determine commit prefix from labels**:
   - `bug` label → `fix:`
   - `enhancement`/`feature` label → `feat:`
   - `refactor` label → `refactor:`
   - `docs` label → `docs:`
   - No clear label → read the issue body and pick the best prefix

3. **Assess complexity**: If the issue touches 5+ files, requires architectural changes, or has security implications, tell the user and suggest `/implement-issue $ARGUMENTS` instead. Proceed only if it's genuinely simple.

## Phase 2: Branch & Implement

1. **Ensure clean state**: `git status` — stash or warn if dirty
2. **Create branch**:
   ```bash
   git fetch origin main && git checkout -b fix/issue-$ARGUMENTS origin/main
   ```
   If branch already exists: `git checkout fix/issue-$ARGUMENTS && git merge origin/main`
3. **Read the relevant code**, then implement the fix

## Phase 3: Validate

1. **Run tests**: `uv run pytest`
2. **Run lint**: `uv run ruff check --fix .`
3. **If tests fail**: debug and fix. Do NOT proceed to Phase 4 with failing tests.

## Phase 4: Commit & PR

1. **Commit** with conventional message: `<prefix>(scope): <description> (#$ARGUMENTS)`
2. **Push**: `git push -u origin fix/issue-$ARGUMENTS`
3. **Create PR**:
   ```bash
   gh pr create --base main --title "<prefix>(scope): <description>" --body "$(cat <<'EOF'
   Closes #$ARGUMENTS

   ## Summary
   <1-3 bullet points describing what changed and why>

   ## Testing
   - [x] Unit tests pass
   - [x] Linting passes

   Generated with Claude Code
   EOF
   )"
   ```

Keep it simple — no worktrees, no parallel agents. For complex issues, use `/implement-issue` instead.

Current issue: $ARGUMENTS
