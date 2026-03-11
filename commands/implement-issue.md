---
name: implement-issue
description: Implement a GitHub issue comprehensively using parallel subagents
---

Implement GitHub issue #$ARGUMENTS comprehensively using parallel subagents.

## Phase 0: Task Plan (CRITICAL - DO THIS FIRST)

Create tasks with TaskCreate and set up blockedBy dependencies. **IMPORTANT**: TaskCreate returns dynamic IDs — capture each returned ID and use it in subsequent `blockedBy` arrays. Do NOT hardcode IDs.

```
task_setup     = TaskCreate("Setup worktree for issue #$ARGUMENTS")        → returns ID_A
task_analyze   = TaskCreate("Fetch and analyze issue", blockedBy=[ID_A])   → returns ID_B
task_implement = TaskCreate("Implement changes", blockedBy=[ID_B])         → returns ID_C
task_qa        = TaskCreate("QA and fix loop", blockedBy=[ID_C])           → returns ID_D
task_pr        = TaskCreate("Create PR", blockedBy=[ID_D])                 → returns ID_E
task_polish    = TaskCreate("Polish", blockedBy=[ID_E])                    → returns ID_F
```

Update task status as you progress (in_progress -> completed).

## Phase 1: Setup Worktree

Compute paths in a single bash call and **remember the resolved values** for use in all subsequent commands. Shell variables do NOT persist between Bash tool calls, so you must inline the actual paths in every subsequent command.

```bash
MAIN_REPO=$(git rev-parse --show-toplevel) && \
PROJECT_NAME=$(basename "$MAIN_REPO") && \
echo "MAIN_REPO=$MAIN_REPO" && \
echo "WORKTREE_DIR=$MAIN_REPO/../$PROJECT_NAME-issue-$ARGUMENTS" && \
echo "BRANCH_NAME=feature/issue-$ARGUMENTS"
```

**CRITICAL**: Note the resolved paths from the output above. In ALL subsequent Bash calls, use the literal resolved paths (e.g., `/Users/foo/project-issue-42`), NOT shell variables like `$WORKTREE_DIR`.

1. **Fetch latest main**: `git fetch origin main`

2. **Check if branch exists** (use the literal resolved branch name):
   ```bash
   git branch --list "<BRANCH_NAME>" && echo "EXISTS" || echo "NEW"
   ```
   - If EXISTS: `git worktree add <WORKTREE_DIR> <BRANCH_NAME>` (reuse branch)
   - If NEW: `git worktree add <WORKTREE_DIR> -b <BRANCH_NAME> origin/main`

3. **Install dependencies in worktree**:
   ```bash
   cd <WORKTREE_DIR> && uv sync
   ```

4. **Verify**: `cd <WORKTREE_DIR> && pwd && git branch --show-current`

## Phase 2: Fetch & Analyze (PARALLEL read-only agents)

1. **Fetch issue**: `gh issue view $ARGUMENTS --json title,body,labels,assignees`

2. **Launch read-only analysis agents in parallel** (single message, multiple Agent calls):
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

## Phase 4: QA (read-only review + lint)

Launch QA agents **in parallel** (single message):
1. **code-reviewer agent**: Review all changes. **IMPORTANT: Include in prompt: "Do NOT run any tests or pytest commands. Only read and analyze code."**
2. **security-scanner agent**: Scan for new vulnerabilities
3. Run lint and format: `cd <WORKTREE_DIR> && uv run ruff check --fix . && uv run ruff format .`

**If any agent reports issues**:
- Fix the issues (sequential writes)
- Re-run review (max 3 iterations total)

Do NOT run tests here — tests run once in Phase 5 before merge.

## Phase 5: Commit, Test & PR

1. **git-manager agent**: Create atomic commits with conventional messages referencing #$ARGUMENTS

2. **Push**:
   ```bash
   cd <WORKTREE_DIR> && git push -u origin <BRANCH_NAME>
   ```

3. **Run tests once** before creating PR: launch **test-runner agent** with `cd <WORKTREE_DIR> && uv run pytest` (set Bash timeout to 600000ms)
   - If tests fail, use **debugger agent** to fix, then re-run tests (max 3 retries)
   - Do NOT create PR with failing tests

4. **Create PR**:
   ```bash
   cd <WORKTREE_DIR> && gh pr create --base main --title "<prefix>(scope): <title from issue>" --body "$(cat <<'EOF'
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

1. Run `/polish` on the PR (use the Skill tool with skill="polish" and the PR number as args)
2. Use **coderabbit-monitor agent** to wait for CodeRabbit review
3. Address feedback, push fixes
4. For large PRs (50+ files), run `/polish` at least 3-5 times before considering it ready

## Phase 7: Cleanup Worktree

After PR is merged or abandoned:

```bash
cd <MAIN_REPO> && git worktree remove <WORKTREE_DIR> && git fetch --prune && git branch -d <BRANCH_NAME>
```

**NOTE**: Do NOT clean up automatically. Ask the user before removing the worktree.

## Error Handling

- **Worktree creation fails**: Check if branch already exists or worktree path conflicts. Clean up stale worktrees with `git worktree prune` and retry.
- **Dependency install fails**: Check for Python version mismatches or lock file issues. Report to user if unresolvable.
- **Implementation fails**: Stop and report to the user. Do not force partial implementations.
- **All 3 QA iterations fail**: Stop and report. Do not force-create the PR.

## Key Rules

- **Read-only agents run in parallel, write agents run sequentially**
- **Always `cd <WORKTREE_DIR> &&`** before every bash command (cd doesn't persist between Bash calls)
- **Never use shell variables** (`$WORKTREE_DIR`) in subsequent Bash calls — inline the resolved literal paths
- **Always `uv sync`** after creating a worktree
- **Tests run once** — only in Phase 5, right before PR creation. Do not run tests during implementation or review phases.
- **Never create PR with failing tests** — fix them first (max 3 retries)
- **Never work on main branch**
- **Ask before cleaning up worktree**
- **code-reviewer agents must NEVER run tests** — always include "Do NOT run any tests or pytest commands" in their prompts
- **Set Bash timeout to 600000** for any pytest command (test suite may take ~8 min)
- **Never merge PRs without explicit user confirmation**
- **Use `/polish` skill** (via Skill tool) for PR polishing, not manual review

Current issue: $ARGUMENTS
