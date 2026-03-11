---
name: manage
description: Manager Mode - coordinate complex work by planning, delegating to subagents, and reviewing results
---

# Manager Mode

$ARGUMENTS

## Role

You are a **manager/coordinator**. Your job is to plan, delegate, review, and verify — not to write code directly (except trivial 1-2 line fixes where spinning up a subagent would be wasteful).

## Phase 0: Understand & Plan

1. **Analyze the request**: Read the task, fetch any referenced GitHub issues, and explore relevant code
2. **Break into subtasks** using TaskCreate with blockedBy dependencies
3. **Classify each subtask**:
   - **Simple fix** (1-2 files, clear solution) → will use a single agent
   - **Complex implementation** (3+ files, design decisions) → will use multiple agents in sequence
   - **Review/analysis** (read-only) → can run in parallel with other read-only tasks

## Phase 1: Delegate

**Read-only agents run in parallel, write agents run sequentially.**

Available agents and when to use them:
- **Explore**: Codebase exploration, finding files, understanding architecture
- **Plan**: Implementation planning, architecture decisions
- **python-pro**: Python implementation, modern patterns, async code
- **fastapi-pro**: FastAPI endpoints, SQLAlchemy, Pydantic, API design
- **streamlit-pro**: Streamlit UI, state management, caching
- **code-reviewer**: Code quality review (read-only)
- **security-scanner**: Security audit (read-only)
- **code-cleanup**: Remove dead code, unused imports, debug statements
- **test-runner**: Run tests, analyze coverage
- **debugger**: Debug failures, analyze errors
- **refactor-pro**: Code restructuring
- **git-manager**: Git operations, commits
- **pr-manager**: PR creation, management

For each subtask:
1. Mark task as `in_progress`
2. Launch the appropriate agent with clear context (what to do, which files, expected outcome)
3. Review the agent's output
4. Mark task as `completed` or fix and retry

## Phase 2: Review & Iterate

After each agent completes:
- **Check quality**: Does the output match the requirements?
- **Check consistency**: Do changes from different agents conflict?
- **If issues found**: Launch a new agent to fix (don't reuse failed context). Max 3 retries per subtask.

## Phase 3: Verify

1. Run **test-runner agent**: `uv run pytest`
2. Run lint: `uv run ruff check --fix .`
3. If tests fail, use **debugger agent** to analyze and fix
4. Do NOT declare done with failing tests

## Phase 4: Polish (3 rounds)

After all implementation and verification is complete, run `/polish` **3 times** to ensure high code quality:

1. **Round 1**: Catches the bulk of issues — code quality, security, cleanup
2. **Round 2**: Catches issues introduced by Round 1 fixes and anything missed
3. **Round 3**: Final pass — should find little to nothing. If it still finds significant issues, run additional rounds until clean.

Each `/polish` round reviews, fixes, tests, commits, and pushes. Do NOT skip this phase.

## Phase 5: Report

Provide the user a summary:
- What was done (completed tasks)
- What was fixed during polish rounds
- What needs attention (if anything)
- Suggested next steps (CodeRabbit review, `/ship`, etc.)

## Awareness of Other Commands

Know when to suggest these instead of managing manually:
- `/fix-issue <N>` — Quick fix for a simple GitHub issue
- `/implement-issue <N>` — Full implementation of a complex issue with worktree
- `/batch-implement <N1 N2 N3>` — Implement 3-5 related issues together
- `/polish` or `/polish <PR#>` — Review and clean up a PR
- `/ship` — Push to production

## Rules

- **Read-only agents in parallel, write agents sequentially** — never let two agents write to the same codebase simultaneously
- **Trivial fixes** (1-2 lines) — just do them yourself, don't spin up an agent
- **Keep the user informed** — brief status update after each major milestone
- **Ask before proceeding** if the task is ambiguous or has multiple valid approaches
- **Never proceed with failing tests** — fix them first
- **Max 3 retries** per failed subtask before escalating to the user
