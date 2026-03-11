---
name: implement-issue
description: Implement a GitHub issue comprehensively using parallel subagents
---

Implement GitHub issue #$ARGUMENTS comprehensively using parallel subagents.

## Phase 0: Task Plan (CRITICAL - DO THIS FIRST)

Create tasks with TaskCreate and set up blockedBy dependencies:
- Task 1: "Setup worktree for issue #$ARGUMENTS"
- Task 2: "Fetch and analyze issue" (blockedBy: 1)
- Task 3: "Implement changes" (blockedBy: 2)
- Task 4: "QA and fix loop" (blockedBy: 3)
- Task 5: "Commit and create PR" (blockedBy: 4)
- Task 6: "Polish" (blockedBy: 5)

Update task status as you progress (in_progress -> completed).

## Phase 1: Setup Worktree

Store paths as shell variables for all subsequent commands:

```bash
MAIN_REPO=$(git rev-parse --show-toplevel)
PROJECT_NAME=$(basename "$MAIN_REPO")
WORKTREE_DIR="$MAIN_REPO/../$PROJECT_NAME-issue-$ARGUMENTS"
BRANCH_NAME="feature/issue-$ARGUMENTS"
```

1. **Fetch latest main**: `git fetch origin main`

2. **Check if branch exists**:
   ```bash
   git branch --list "$BRANCH_NAME" && echo "EXISTS" || echo "NEW"
   ```
   - If EXISTS: `git worktree add "$WORKTREE_DIR" "$BRANCH_NAME"` (reuse branch)
   - If NEW: `git worktree add "$WORKTREE_DIR" -b "$BRANCH_NAME" origin/main`

3. **Install dependencies in worktree**:
   ```bash
   cd "$WORKTREE_DIR" && uv sync
   ```

4. **Verify**: `pwd && git branch --show-current`

**CRITICAL**: All subsequent bash commands MUST use `cd "$WORKTREE_DIR" &&` prefix since cd does not persist between tool calls.

## Phase 2: Fetch & Analyze (PARALLEL read-only agents)

1. **Fetch issue**: `gh issue view $ARGUMENTS --json title,body,labels,assignees`

2. **Launch read-only analysis agents in parallel** (single message, multiple Task calls):
   - **Explore agent** (thoroughness: "very thorough"): Map all files relevant to this issue
   - **Plan agent**: Create implementation plan from the issue description and codebase analysis
   - **security-scanner agent**: Pre-scan affected areas for existing vulnerabilities

3. **Determine commit prefix** from issue labels:
   - `bug` → `fix:`, `enhancement`/`feature` → `feat:`, `refactor` → `refactor:`, `docs` → `docs:`

## Phase 3: Implement (SEQUENTIAL writes)

**IMPORTANT**: Write operations must be sequential to avoid file conflicts. Do NOT launch multiple writing agents in parallel.

1. **Pick the right agent** based on issue type and implement:
   - Frontend/UI → **streamlit-pro agent**
   - Backend/API → **fastapi-pro agent** or **python-pro agent**
   - Security → **python-pro agent** (with security context from Phase 2)
   - Refactoring → **refactor-pro agent**

2. If the implementation is large, break it into sequential steps — each step using one writing agent at a time.

3. After implementation, run a **code-cleanup agent** to remove any debug code or unused imports.

## Phase 4: QA Loop (max 3 iterations)

Launch read-only QA agents **in parallel** (single message):
1. **test-runner agent**: `cd "$WORKTREE_DIR" && uv run pytest`
2. **code-reviewer agent**: Review all changes
3. **security-scanner agent**: Scan for new vulnerabilities
4. Run lint: `cd "$WORKTREE_DIR" && uv run ruff check --fix .`

**If any agent reports failures**:
- Use **debugger agent** to analyze failures
- Fix the issues (sequential writes)
- Re-run this phase (max 3 iterations total)
- Do NOT proceed to Phase 5 with failing tests

## Phase 5: Commit & PR

1. **git-manager agent**: Create atomic commits with conventional messages referencing #$ARGUMENTS

2. **Push**:
   ```bash
   cd "$WORKTREE_DIR" && git push -u origin "$BRANCH_NAME"
   ```

3. **Create PR**:
   ```bash
   cd "$WORKTREE_DIR" && gh pr create --base main --title "<prefix>(scope): <title from issue>" --body "$(cat <<'EOF'
   Closes #$ARGUMENTS

   ## Summary
   <bullet points of changes>

   ## Testing
   - [x] Unit tests pass
   - [x] Linting passes
   - [x] Security scan passed

   Generated with Claude Code
   EOF
   )"
   ```

## Phase 6: Polish

1. Run `/polish` on the PR
2. Use **coderabbit-monitor agent** to wait for CodeRabbit review
3. Address feedback, push fixes

## Phase 7: Cleanup Worktree

After PR is merged or abandoned:

```bash
cd "$MAIN_REPO" && git worktree remove "$WORKTREE_DIR"
git fetch --prune && git branch -d "$BRANCH_NAME"
```

## Key Rules

- **Read-only agents run in parallel, write agents run sequentially**
- **Always `cd "$WORKTREE_DIR" &&`** before every bash command (cd doesn't persist)
- **Always `uv sync`** after creating a worktree
- **Never proceed with failing tests** — fix them first (max 3 QA loops)
- **Never work on main branch**
- **Clean up worktree** after PR is merged

Current issue: $ARGUMENTS
