---
name: batch-implement
description: Implement multiple related GitHub issues in a single feature branch
argument-hint: <issue1> <issue2> [issue3...]
---

Implement multiple related GitHub issues in a single feature branch.

Arguments: $ARGUMENTS (space-separated issue numbers, e.g., "97 98 99")

## Phase 0: Task Plan (CRITICAL - DO THIS FIRST)

Parse issue numbers from `$ARGUMENTS`. Extract FIRST and LAST for naming.

**Validate batch size**: If more than 5 issues are provided, warn the user and suggest splitting into multiple runs. Do not proceed with >5 issues without explicit confirmation.

Create tasks with TaskCreate and set up blockedBy dependencies. **IMPORTANT**: TaskCreate returns dynamic IDs — capture each returned ID and use it in subsequent `blockedBy` arrays. Do NOT hardcode IDs.

```
task_setup     = TaskCreate("Setup worktree for batch issues")           → returns ID_A
task_fetch     = TaskCreate("Fetch and plan all issues", blockedBy=[ID_A])  → returns ID_B
task_analyze   = TaskCreate("Analyze codebase", blockedBy=[ID_B])           → returns ID_C
task_implement = TaskCreate("Implement issues sequentially", blockedBy=[ID_C]) → returns ID_D
task_qa        = TaskCreate("QA and fix loop", blockedBy=[ID_D])            → returns ID_E
task_pr        = TaskCreate("Create PR", blockedBy=[ID_E])                  → returns ID_F
task_polish    = TaskCreate("Polish", blockedBy=[ID_F])                     → returns ID_G
```

Update task status as you progress (in_progress -> completed).

## Phase 1: Setup Worktree

Compute paths in a single bash call and **remember the resolved values** for use in all subsequent commands. Shell variables do NOT persist between Bash tool calls, so you must inline the actual paths in every subsequent command.

```bash
MAIN_REPO=$(git rev-parse --show-toplevel) && \
PROJECT_NAME=$(basename "$MAIN_REPO") && \
echo "MAIN_REPO=$MAIN_REPO" && \
echo "WORKTREE_DIR=$MAIN_REPO/../$PROJECT_NAME-batch-<first>-<last>" && \
echo "BRANCH_NAME=feature/batch-<first>-<last>-$(date +%s)"
```

**CRITICAL**: Note the resolved paths from the output above. In ALL subsequent Bash calls, use the literal resolved paths (e.g., `/Users/foo/project-batch-97-99`), NOT shell variables like `$WORKTREE_DIR`.

1. **Fetch latest main**: `git fetch origin main`

2. **Check if branch exists** (use the literal resolved branch name):
   ```bash
   git branch --list "<BRANCH_NAME>" && echo "EXISTS" || echo "NEW"
   ```
   - If EXISTS: `git worktree add <WORKTREE_DIR> <BRANCH_NAME>`
   - If NEW: `git worktree add <WORKTREE_DIR> -b <BRANCH_NAME> origin/main`

3. **Install dependencies**:
   ```bash
   cd <WORKTREE_DIR> && uv sync
   ```

4. **Verify**: `cd <WORKTREE_DIR> && pwd && git branch --show-current`

## Phase 2: Fetch & Plan (PARALLEL read-only)

1. **Fetch all issues in parallel** (single message, one Agent call per issue):
   - Each **general-purpose agent**: `gh issue view <number> --json title,body,labels,comments`

2. After all fetched, launch **Plan agent**:
   - Analyze all issues together
   - Identify common files, dependencies between issues
   - Determine implementation order
   - Decide commit prefix per issue from labels (`bug`→`fix:`, `enhancement`→`feat:`, etc.)

## Phase 3: Parallel Analysis (read-only, single message)

Launch in parallel:
1. **Explore agent** (thoroughness: "very thorough"): Map all files affected across all issues
2. **code-reviewer agent**: Pre-review existing code in affected areas. **IMPORTANT: Include in prompt: "Do NOT run any tests or pytest commands. Only read and analyze code."**
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

3. **Commit the issue's changes** immediately after implementation:
   ```bash
   cd <WORKTREE_DIR> && git add -A && git commit -m "<prefix>(<scope>): <description> (#<issue_number>)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```
   Use the commit prefix determined in Phase 2 (`fix:`, `feat:`, `refactor:`, etc.).

4. After all issues implemented, run **code-cleanup agent** across all modified files.

## Phase 5: QA (read-only review + lint)

Launch QA agents **in parallel** (single message):
1. **code-reviewer agent**: Review all changes holistically. **IMPORTANT: Include in prompt: "Do NOT run any tests or pytest commands. Only read and analyze code."**
2. **security-scanner agent**: Final security scan
3. Run lint and format: `cd <WORKTREE_DIR> && uv run ruff check --fix . && uv run ruff format .`

**If any agent reports issues**:
- Fix issues (sequential writes)
- Re-run review (max 3 iterations)

Do NOT run tests here — tests run once in Phase 6 before PR creation.

## Phase 6: Test, Push & Create PR

Commits were already created per-issue in Phase 4. Now test, push, and create the PR.

1. **Run tests once** before creating PR: launch **test-runner agent** with `cd <WORKTREE_DIR> && uv run pytest` (set Bash timeout to 600000ms)
   - If tests fail, use **debugger agent** to fix, then re-run tests (max 3 retries)
   - Do NOT create PR with failing tests

2. **Push**:
   ```bash
   cd <WORKTREE_DIR> && git push -u origin <BRANCH_NAME>
   ```

3. **Create PR** — choose the title prefix based on the dominant issue type (e.g., if 2/3 issues are bugs, use `fix:`; if mixed, use `chore:`):
   ```bash
   cd <WORKTREE_DIR> && gh pr create --base main --title "<prefix>: implement issues #<first>-#<last>" --body "$(cat <<'EOF'
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

1. Run `/polish` on the PR (use the Skill tool with skill="polish" and the PR number as args)
2. Use **coderabbit-monitor agent** to wait for CodeRabbit review
3. Address feedback, push fixes
4. For large PRs (50+ files), run `/polish` at least 3-5 times before considering it ready

## Phase 8: Cleanup Worktree

After PR is merged or abandoned:

```bash
cd <MAIN_REPO> && git worktree remove <WORKTREE_DIR> && git fetch --prune && git branch -d <BRANCH_NAME>
```

**NOTE**: Do NOT clean up automatically. Ask the user before removing the worktree.

## Error Handling

- **Worktree creation fails**: Check if branch already exists or worktree path conflicts. Clean up stale worktrees with `git worktree prune` and retry.
- **Dependency install fails**: Check for Python version mismatches or lock file issues. Report to user if unresolvable.
- **Issue implementation fails**: Skip the problematic issue, note it in the PR description, and continue with remaining issues. Ask the user how to proceed.
- **All 3 QA iterations fail**: Stop and report. Do not force-create the PR.

## Key Rules

- **Read-only agents run in parallel, write agents run sequentially**
- **Always `cd <WORKTREE_DIR> &&`** before every bash command (cd doesn't persist between Bash calls)
- **Never use shell variables** (`$WORKTREE_DIR`) in subsequent Bash calls — inline the resolved literal paths
- **Always `uv sync`** after creating a worktree
- **Tests run once** — only in Phase 6, right before PR creation. Do not run tests during implementation, review, or polish phases.
- **Never create PR with failing tests** — fix them first (max 3 retries)
- **Commit immediately after each issue** — one commit per issue, no deferred batch commits
- **Limit batch size to 3-5 issues** — reject >5 without explicit user confirmation
- **Never work on main branch**
- **Ask before cleaning up worktree**
- **code-reviewer agents must NEVER run tests** — always include "Do NOT run any tests or pytest commands" in their prompts
- **Set Bash timeout to 600000** for the pytest command in Phase 6 (test suite may take ~8 min)
- **Never merge PRs without explicit user confirmation**
- **Use `/polish` skill** (via Skill tool) for PR polishing, not manual review
- **Use `/manage` skill** when coordinating >3 parallel agents or when the implementation plan is complex

## Agent Worktree Isolation

When launching agents that need to read/write files in the worktree, you can use `isolation: "worktree"` on the Agent tool to give them their own isolated copy. This is especially useful for:
- Parallel read-only analysis agents in Phases 2-3
- The code-cleanup agent in Phase 4

For write agents in Phase 4, do NOT use worktree isolation — they must write to the shared worktree sequentially.

## Parallel Execution Safety

Multiple `/batch-implement` commands can run simultaneously in separate terminals:
- Each gets its own worktree and branch (unique due to timestamp suffix in branch name)
- No file conflicts between instances
- Each creates a separate PR

## Skill Integration

- Use `/manage` (Skill tool, skill="manage") at the start if the batch involves >3 issues or cross-cutting concerns. Let it coordinate the planning and delegation.
- Use `/polish` (Skill tool, skill="polish") in Phase 7 for automated review-fix-verify cycles.

Current issues: $ARGUMENTS
