---
name: polish
description: Review all changes, fix issues, commit and push to origin. Optionally pass a PR number to polish a specific pull request.
---

Execute the complete code polishing workflow.

## Phase 0: Task Plan

Create tasks with TaskCreate:
- Task 1: "Review and scan changes"
- Task 2: "Fix identified issues" (blockedBy: 1)
- Task 3: "Verify fixes and push" (blockedBy: 2)

Update task status as you progress.

## Phase 1: Setup

1. **If PR number provided in $ARGUMENTS**:
   ```bash
   gh pr checkout $ARGUMENTS
   gh pr diff $ARGUMENTS
   ```
   If no PR number, work on the current branch.

2. **Determine working directory**: Check if inside a worktree or main repo:
   ```bash
   git rev-parse --show-toplevel
   ```
   Use this as `$WORK_DIR` for all subsequent commands.

3. **Get the diff to review**:
   ```bash
   git diff origin/main...HEAD --stat
   ```

## Phase 2: Parallel Review (read-only, single message)

Launch ALL in parallel:

1. **code-reviewer agent**: Review all changed files for quality, bugs, and best practices
2. **security-scanner agent**: Scan for secrets, vulnerabilities, OWASP issues, dependency security
3. **code-cleanup agent**: Scan for unused imports, debug statements, commented code, stale TODOs
4. **test-runner agent**: Run `uv run pytest` (no `-x` — show ALL failures)
5. Run lint: `uv run ruff check .` (identify only, don't fix yet)

## Phase 3: Fix Issues (SEQUENTIAL writes, max 3 iterations)

Collect all findings from Phase 2, then fix **sequentially** (one agent at a time):

1. **Pick the right agent** per issue type:
   - Security vulnerabilities → **python-pro agent** (with security context from scanner)
   - Python code quality → **python-pro agent**
   - API issues → **fastapi-pro agent**
   - UI issues → **streamlit-pro agent**
   - Code structure → **refactor-pro agent**
   - Cleanup (dead code, imports) → **code-cleanup agent**
   - Test failures → **debugger agent**

2. Group fixes that touch the same files into one agent call to avoid conflicts.

3. After all fixes, run lint: `uv run ruff check --fix .`

## Phase 4: Verify (read-only parallel, then loop if needed)

Launch in parallel:
1. **test-runner agent**: Run full test suite, verify coverage
2. **code-reviewer agent**: Quick review of the fixes
3. **security-scanner agent**: Re-scan for remaining issues

**If any agent reports failures**: loop back to Phase 3 (max 3 total iterations). Do NOT proceed with failing tests.

## Phase 5: Commit & Push

1. **Stage specific files** (NOT `git add -A`):
   ```bash
   git add <list of changed files by name>
   ```

2. **Commit** with conventional message:
   ```
   chore: polish code quality, fix <summary of main fixes>
   ```

3. **Push**: `git push origin HEAD`

4. **Monitor CI**:
   ```bash
   gh pr checks 2>/dev/null || gh run list --limit 3
   ```

5. **If CI fails**: use **debugger agent** to analyze logs, fix, and loop back to Phase 4.

## Phase 6: CodeRabbit Review (if PR exists)

1. Use **coderabbit-monitor agent** to check review status
2. If CodeRabbit has comments:
   - Fix issues sequentially (one agent at a time)
   - Push fixes
   - Re-check review status (max 3 iterations)

Usage:
- `/polish` — Polish current branch
- `/polish 123` — Polish pull request #123

Current task context: $ARGUMENTS
