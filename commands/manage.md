---
name: manage
description: Manager Mode - coordinate complex work by planning, delegating to subagents, and reviewing results
---

# Manager Mode

$ARGUMENTS

## Role

You are a **manager/coordinator**. Your job is to plan, delegate, review, and verify — not to write code directly (except trivial 1-2 line fixes where spinning up a subagent would be wasteful).

## Phase 0: Understand & Plan

1. **Analyze the request**: Read the task, fetch any referenced GitHub issues, and explore relevant code. Launch issue fetch and code exploration agents **in parallel** since they are independent read-only operations.
2. **Break into subtasks** using TaskCreate with blockedBy dependencies
3. **Classify each subtask**:
   - **Simple fix** (1-2 files, clear solution) → will use a single agent
   - **Complex implementation** (multiple files, design decisions, high coupling) → will use multiple agents in sequence
   - **Review/analysis** (read-only) → can run in parallel with other read-only tasks

## Phase 1: Delegate

**All agents run in parallel.** Write agents are launched with `isolation: "worktree"`, which creates a temporary git worktree — an isolated, independent copy of the repository on its own branch. This eliminates file conflicts between agents entirely.

Available agents and when to use them:
- **Explore**: Codebase exploration, finding files, understanding architecture
- **Plan**: Implementation planning, architecture decisions
- **python-pro**: Python implementation, modern patterns, async code
- **fastapi-pro**: FastAPI endpoints, SQLAlchemy, Pydantic, API design
- **streamlit-pro**: Streamlit UI, state management, caching
- **code-reviewer**: Code quality review (read-only). **NEVER include test/pytest commands** — reviewers must only read and analyze code.
- **security-scanner**: Security audit (read-only)
- **code-cleanup**: Remove dead code, unused imports, debug statements
- **test-runner**: Run tests, analyze coverage. **Always set bash timeout to 600000** (test suite may take ~8 min).
- **debugger**: Debug failures, analyze errors
- **refactor-pro**: Code restructuring
- **git-manager**: Git operations, commits
- **pr-manager**: PR creation, management

**Agent prompt template** — every agent prompt MUST include all of these:
```
## Task
<what the agent should accomplish — be specific, not vague>

## Files to modify
<explicit list of files to read and/or edit>

## Expected outcome
<what "done" looks like — e.g., "endpoint returns 404 instead of 500 for missing resources">

## Constraints
- <any rules or boundaries — e.g., "do not change the database schema">
- <relevant context from Phase 0 — e.g., "this must be backwards-compatible with v2 API">
- Do NOT run any tests or pytest commands. (for read-only/review agents)
```

For each subtask:
1. Mark task as `in_progress`
2. Launch the appropriate agent with `isolation: "worktree"` (for write agents) using the prompt template above
3. Each agent works on its own branch in its own worktree
4. Review the agent's output when it completes
5. Mark task as `completed` or fix and retry

### Phase 1 Checkpoint

After all agents complete, report to the user:
```
## Phase 1 Complete — Delegation Results

| Task | Agent | Status | Branch |
|------|-------|--------|--------|
| <task name> | <agent type> | completed/failed | <branch name> |

**Succeeded**: X of Y
**Failed**: X (will retry in Phase 2)
**Ready to merge**: <list of branches>
```

## Phase 2: Merge & Review

After all agents complete, merge their worktree branches into the feature branch:

1. **Merge one-by-one**: Merge each agent's branch into the feature branch in priority order (most architecturally central first)
2. **Resolve conflicts**: If a merge conflicts, launch a debugger agent to resolve it — or resolve trivial conflicts yourself
3. **Check quality**: Does each agent's output match the requirements?
4. **If issues found**: Launch a new agent (in worktree) to fix. Max 3 retries per subtask.

### Phase 2 Checkpoint

After all merges complete, report to the user:
```
## Phase 2 Complete — Merge Results

**Branches merged**: X of Y
**Conflicts resolved**: X
**Quality issues found**: X (fixed: Y, retried: Z)
**Files changed total**: <count>
**Ready for lint & verification**
```

## Phase 3: Verify (lint only)

1. Run lint autofix: `uv run ruff check --fix . && uv run ruff format .`
2. Fix any lint errors that can't be auto-fixed
3. Do NOT run tests here — tests run once in Phase 5 before merge

## Phase 3.5: Browser Verification (if web app)

If changes affect a web UI (Streamlit, FastAPI with templates, or any frontend):
1. Start the app locally
2. Use **Chrome MCP** to navigate to key pages and verify they render correctly
3. Test the specific functionality that was changed
4. Fix any visual or functional issues before proceeding to Polish

## Phase 4: Polish (3-5 rounds)

**Skip this phase if `/manage` was invoked from within `/polish`** — `/polish` already handles its own review-fix-verify cycle, so re-polishing would create an infinite loop.

After all implementation and verification is complete, run `/polish` to ensure high code quality:

- **Minimum 3 rounds** for standard PRs
- **Minimum 5 rounds** for large PRs (50+ files changed)
- Continue until a round finds no significant issues

1. **Round 1**: Catches the bulk of issues — code quality, security, cleanup
2. **Round 2**: Catches issues introduced by Round 1 fixes and anything missed
3. **Round 3+**: Should find less each time. Stop when clean.

Each `/polish` round reviews, fixes, tests, commits, and pushes. Do NOT skip this phase (unless invoked from `/polish`).

## Phase 5: Deliver & Report

1. **Create feature branch and PR** via pr-manager agent — never push to main
2. **Run tests once** before requesting merge: launch **test-runner agent** with `uv run pytest` (set bash timeout to 600000)
   - If tests fail, use **debugger agent** to fix, then re-run tests
   - Max 3 retries before escalating to the user
   - Do NOT request merge with failing tests
3. Provide the user a summary:
   - What was done (completed tasks)
   - What was fixed during polish rounds
   - Test results (pass/fail counts)
   - PR URL
   - What needs attention (if anything)
   - Suggested next steps (CodeRabbit review, `/ship`, etc.)
4. **Status updates**: Report to the user after each phase transition and after each task completion

## Context Management

- For very large tasks (10+ subtasks or 50+ files), consider splitting into multiple `/manage` sessions to avoid context exhaustion
- Prioritize the most impactful and risky subtasks first so they get full context attention
- Summarize completed work concisely to preserve context for remaining tasks

## Awareness of Other Commands

Know when to suggest these instead of managing manually:
- `/implement-issue <N>` — Full implementation of a single issue with worktree
- `/batch-implement <N1 N2 N3>` — Implement 3-5 related issues together
- `/polish` or `/polish <PR#>` — Review and clean up a PR
- `/catchup` — Resume work by loading all uncommitted changes

## Rules

- **All write agents use worktree isolation** — every write agent gets `isolation: "worktree"` so it works on its own branch in its own copy of the repo
- **All agents run in parallel** — worktree isolation makes sequential execution unnecessary
- **Merge after completion** — merge agent branches into the feature branch one-by-one, resolving conflicts as they arise
- **code-reviewer agents must NEVER run tests** — always use a separate test-runner agent for testing
- **Trivial fixes** (1-2 lines) — just do them yourself, don't spin up an agent
- **Keep the user informed** — brief status update after each phase transition and task completion
- **Ask before proceeding** if the task is ambiguous or has multiple valid approaches
- **Tests run once** — only in Phase 5, right before merge. Do not run tests during implementation, review, or polish phases.
- **Never merge with failing tests** — fix them first
- **Never push to main** — always create a feature branch and PR
- **Never merge PRs** without explicit user confirmation
- **Max 3 retries** per failed subtask before escalating to the user
- **Rollback over patching** — if a change causes cascading failures after 3 fix attempts, revert it and rethink the approach
