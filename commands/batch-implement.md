---
name: batch-implement
description: Implement multiple related GitHub issues in a single feature branch
---

Implement multiple related GitHub issues in a single feature branch.

Arguments: $ARGUMENTS (space-separated issue numbers, e.g., "97 98 99")

## Phase 0: Task Plan (CRITICAL - DO THIS FIRST)

Parse issue numbers from `$ARGUMENTS`. Extract FIRST and LAST for naming.

Create tasks with TaskCreate and set up blockedBy dependencies:
- Task 1: "Setup worktree for batch issues"
- Task 2: "Fetch and plan all issues" (blockedBy: 1)
- Task 3: "Analyze codebase" (blockedBy: 2)
- Task 4: "Implement issues sequentially" (blockedBy: 3)
- Task 5: "QA and fix loop" (blockedBy: 4)
- Task 6: "Commit and create PR" (blockedBy: 5)
- Task 7: "Polish" (blockedBy: 6)

Update task status as you progress (in_progress -> completed).

## Phase 1: Setup Worktree

Store paths as shell variables for all subsequent commands:

```bash
MAIN_REPO=$(git rev-parse --show-toplevel)
PROJECT_NAME=$(basename "$MAIN_REPO")
WORKTREE_DIR="$MAIN_REPO/../$PROJECT_NAME-batch-<first>-<last>"
BRANCH_NAME="feature/issues-<first>-to-<last>"
```

1. **Fetch latest main**: `git fetch origin main`

2. **Check if branch exists**:
   ```bash
   git branch --list "$BRANCH_NAME" && echo "EXISTS" || echo "NEW"
   ```
   - If EXISTS: `git worktree add "$WORKTREE_DIR" "$BRANCH_NAME"`
   - If NEW: `git worktree add "$WORKTREE_DIR" -b "$BRANCH_NAME" origin/main`

3. **Install dependencies**:
   ```bash
   cd "$WORKTREE_DIR" && uv sync
   ```

4. **Verify**: `cd "$WORKTREE_DIR" && pwd && git branch --show-current`

**CRITICAL**: All subsequent bash commands MUST use `cd "$WORKTREE_DIR" &&` prefix since cd does not persist between tool calls.

## Phase 2: Fetch & Plan (PARALLEL read-only)

1. **Fetch all issues in parallel** (single message, one Task call per issue):
   - Each **general-purpose agent**: `gh issue view <number> --json title,body,labels,comments`

2. After all fetched, launch **Plan agent**:
   - Analyze all issues together
   - Identify common files, dependencies between issues
   - Determine implementation order
   - Decide commit prefix per issue from labels (`bug`→`fix:`, `enhancement`→`feat:`, etc.)

## Phase 3: Parallel Analysis (read-only, single message)

Launch in parallel:
1. **Explore agent** (thoroughness: "very thorough"): Map all files affected across all issues
2. **code-reviewer agent**: Pre-review existing code in affected areas
3. **security-scanner agent**: Pre-scan for existing vulnerabilities

## Phase 4: Implement (SEQUENTIAL)

**IMPORTANT**: Implement issues one at a time to avoid file conflicts. Do NOT launch multiple writing agents in parallel.

For each issue (in the order determined by Phase 2):

1. **Pick the right agent** for the issue type:
   - Frontend/UI → **streamlit-pro agent**
   - Backend/API → **fastapi-pro agent** or **python-pro agent**
   - Security → **python-pro agent** (with security context)
   - Refactoring → **refactor-pro agent**

2. Implement the issue with that single agent.

3. Run a quick sanity check after each issue:
   ```bash
   cd "$WORKTREE_DIR" && uv run pytest -x --timeout=60
   ```
   If tests fail, fix before moving to the next issue.

4. After all issues implemented, run **code-cleanup agent** across all modified files.

## Phase 5: QA Loop (max 3 iterations)

Launch read-only QA agents **in parallel** (single message):
1. **test-runner agent**: `cd "$WORKTREE_DIR" && uv run pytest`
2. **code-reviewer agent**: Review all changes holistically
3. **security-scanner agent**: Final security scan
4. Run lint: `cd "$WORKTREE_DIR" && uv run ruff check --fix .`

**If any agent reports failures**:
- Use **debugger agent** to analyze
- Fix issues (sequential writes)
- Re-run this phase (max 3 iterations)
- Do NOT proceed to Phase 6 with failing tests

## Phase 6: Commit & PR

1. **git-manager agent**: Create one commit per issue with conventional messages:
   ```
   fix(ui): add type hints to streamlit components (#97)
   feat(api): add rate limiting endpoint (#98)
   refactor(core): extract shared validation logic (#99)
   ```

2. **Push**:
   ```bash
   cd "$WORKTREE_DIR" && git push -u origin "$BRANCH_NAME"
   ```

3. **Create PR**:
   ```bash
   cd "$WORKTREE_DIR" && gh pr create --base main --title "fix: implement issues #<first>-#<last>" --body "$(cat <<'EOF'
   ## Summary

   This PR addresses multiple related issues:

   ### Issues Addressed
   - Closes #<issue1> - <title1>
   - Closes #<issue2> - <title2>
   ...

   ## Changes
   <bullet points grouped by area>

   ## Testing
   - [x] All unit tests pass
   - [x] Linting passes
   - [x] Security scan passed

   Generated with Claude Code
   EOF
   )"
   ```

## Phase 7: Polish

1. Run `/polish` on the PR
2. Use **coderabbit-monitor agent** to wait for CodeRabbit review
3. Address feedback, push fixes

## Phase 8: Cleanup Worktree

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
- **Run sanity tests between each issue** implementation to catch problems early
- **One commit per issue** — no ambiguous grouped commits
- **Limit batch size to 3-5 issues** — for larger batches, split into multiple runs
- **Never work on main branch**
- **Clean up worktree** after PR is merged

## Parallel Execution Safety

Multiple `/batch-implement` commands can run simultaneously in separate terminals:
- Each gets its own worktree and branch
- No file conflicts between instances
- Each creates a separate PR

Current issues: $ARGUMENTS
