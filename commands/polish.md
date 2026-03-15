---
name: polish
description: Review all changes, fix issues, commit and push to origin. Optionally pass a PR number to polish a specific pull request. Use PROACTIVELY before merging PRs, when cleaning up code quality, reviewing changes before pushing, or when the user wants a thorough automated review-fix-verify cycle. Also useful after finishing a feature branch, before requesting code review, or when the user says things like "clean this up", "make it ready for review", or "fix whatever's wrong".
---

Execute the complete code polishing workflow: review changes, fix issues, verify, commit, and push.

## Phase 1: Setup

1. **If PR number provided in $ARGUMENTS**:
   ```bash
   gh pr checkout $ARGUMENTS
   gh pr diff $ARGUMENTS
   ```
   If no PR number, work on the current branch.

2. **Determine working directory**:
   ```bash
   git rev-parse --show-toplevel
   ```
   Use this as `$WORK_DIR` for all subsequent commands.

3. **Detect the base branch** — don't assume `main`:
   ```bash
   # If on a PR, get the actual base branch
   BASE=$(gh pr view --json baseRefName -q .baseRefName 2>/dev/null || echo "")
   if [ -z "$BASE" ]; then
     # Fall back to default branch
     BASE=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}')
     [ -z "$BASE" ] && BASE="main"
   fi
   ```

4. **Get the diff to review**:
   ```bash
   git diff origin/$BASE...HEAD --stat
   ```

5. **Capture the changed file list** for use in all review agents:
   ```bash
   CHANGED_FILES=$(git diff origin/$BASE...HEAD --name-only)
   ```
   Store this list — it must be included in every review agent's prompt so they know exactly which files to examine.

## Phase 2: Parallel Review (read-only, single message)

First, measure the change size:
```bash
git diff origin/$BASE...HEAD --stat | tail -1
```
Parse the number of files changed and lines modified from the summary line.

**IMPORTANT**: Every review agent prompt MUST include the list of changed files (`$CHANGED_FILES` from Phase 1) and instruct the agent to focus only on those files. This prevents agents from wasting time scanning the entire codebase.

**Agent prompt template**: Always include this block in every review agent's prompt:
```
Review ONLY the following changed files:
<changed_files>
$CHANGED_FILES
</changed_files>
Do NOT run any tests or pytest commands. Only read and analyze code.
```

Additionally, instruct each agent to **tag every finding with a severity level**:
- **CRITICAL**: Security vulnerabilities, data loss risks, crashes, broken functionality
- **HIGH**: Bugs, incorrect logic, missing error handling, race conditions
- **MEDIUM**: Code quality issues, missing types, anti-patterns, performance problems
- **LOW**: Style issues, minor cleanups, naming suggestions, TODOs

### Small changes (<10 files changed AND <200 lines modified)

Launch ALL in parallel (3 agents + lint):

1. **code-reviewer agent**: Review changed files for quality, bugs, and best practices.
2. **security-scanner agent**: Scan changed files for secrets, vulnerabilities, OWASP issues, dependency security
3. **code-cleanup agent**: Scan changed files for unused imports, debug statements, commented code, stale TODOs
4. Run lint and format check (identify only, don't fix yet):
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   ```

### Medium changes (10+ files changed OR 200+ lines modified)

Launch ALL in parallel (6 agents + lint):

1. **code-reviewer agent**: Review changed files for quality, bugs, and best practices.
2. **security-scanner agent**: Scan changed files for secrets, vulnerabilities, OWASP issues, dependency security
3. **code-cleanup agent**: Scan changed files for unused imports, debug statements, commented code, stale TODOs
4. **python-pro agent**: Review changed files for Python-specific patterns — async correctness, type hints, modern idioms, performance anti-patterns.
5. **refactor-pro agent**: Analyze changed files for code structure, duplication, design patterns, and separation of concerns.
6. **fastapi-pro agent** (if any API/route files changed) OR **streamlit-pro agent** (if any UI files changed) OR **debugger agent** (default — hunt for potential runtime bugs, edge cases, error handling gaps).
7. Run lint and format check (identify only, don't fix yet):
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   ```

### Large changes (30+ files changed OR 500+ lines modified)

Launch ALL in parallel (10+ agents + lint). Split reviews into focused, non-overlapping scopes so each agent produces targeted findings:

1. **code-reviewer agent** (scope: logic & correctness): Review business logic, control flow, edge cases, error handling. Additional scope instruction: "Focus on logic correctness and edge cases."
2. **code-reviewer agent** (scope: API contracts & data flow): Review function signatures, return types, data transformations, API boundaries. Additional scope instruction: "Focus on API contracts, data flow, and interface consistency."
3. **security-scanner agent**: Scan for secrets, vulnerabilities, OWASP issues, dependency security
4. **code-cleanup agent**: Scan for unused imports, debug statements, commented code, stale TODOs
5. **python-pro agent** (scope: async & performance): Review async patterns, potential deadlocks, performance anti-patterns, N+1 queries, inefficient loops. Additional scope instruction: "Focus on async correctness and performance."
6. **python-pro agent** (scope: types & idioms): Review type hints, modern Python idioms, Pydantic model usage, dataclass patterns. Additional scope instruction: "Focus on type safety and Pythonic patterns."
7. **refactor-pro agent**: Analyze code structure, duplication, design patterns, and separation of concerns.
8. **fastapi-pro agent** (if any API/route files changed): Review endpoint design, dependency injection, middleware, response models.
9. **streamlit-pro agent** (if any UI files changed): Review UI patterns, state management, layout, caching.
10. **debugger agent**: Hunt for potential runtime bugs, race conditions, resource leaks, error handling gaps.
11. Run lint and format check (identify only, don't fix yet):
    ```bash
    uv run ruff check .
    uv run ruff format --check .
    ```

Note: For large changes, agents 8 and 9 are conditional on file types changed. If neither API nor UI files are modified, launch additional focused code-reviewer agents scoped to specific subdirectories instead.

## Phase 2.5: Deduplicate & Triage

Before fixing anything, process all findings from Phase 2:

### Deduplication

Multiple agents will often flag the same issue (e.g., python-pro and code-reviewer both catch a missing type hint, or security-scanner and debugger both flag the same unvalidated input). Merge duplicate findings:

1. Group all findings by **file + line range** (findings within 5 lines of each other on the same file are likely duplicates)
2. For each group, keep the most detailed description and the highest severity tag
3. Combine any unique context from different agents into the merged finding

### Severity Triage

Sort the deduplicated findings by severity and plan the fix order:

1. **CRITICAL** — fix first, always. These block the PR.
2. **HIGH** — fix in the same iteration as CRITICAL if possible
3. **MEDIUM** — fix in second iteration if time allows
4. **LOW** — fix only if there are few other issues; otherwise note them in the summary but skip fixing

If there are more than 15 deduplicated findings, drop LOW-severity items from the fix plan entirely and focus on CRITICAL + HIGH + MEDIUM.

### Output

Produce a structured fix plan listing each finding with: severity, file(s), line(s), description, and which agent type should fix it. Use this plan to drive Phase 3.

## Phase 3: Fix Issues (max 3 iterations)

Execute the fix plan from Phase 2.5. The fix strategy depends on how many independent issue groups there are.

### Choosing the right agent per issue type

- Security vulnerabilities → **python-pro agent** (with security context from scanner)
- Python code quality → **python-pro agent**
- API issues → **fastapi-pro agent**
- UI issues → **streamlit-pro agent**
- Code structure → **refactor-pro agent**
- Cleanup (dead code, imports) → **code-cleanup agent**

### Small fix set (1-4 independent issue groups)

Fix **sequentially** — one agent at a time. Sequential writes are simpler and avoid merge overhead when there are only a few things to fix.

1. Group fixes that touch the same files into one agent call
2. Run each agent in order

### Large fix set (5+ independent issue groups)

Use **parallel worktree coordination** — launch multiple write agents simultaneously, each in its own isolated worktree, then merge results. This is significantly faster for large PRs with many scattered issues.

1. **Group issues** into independent fix units — each unit touches a distinct set of files. Issues touching the same files must be in the same group.

2. **Launch all fix agents in parallel** with `isolation: "worktree"`:
   - Each agent gets its own branch and copy of the repo
   - Include in each agent's prompt: the specific issues to fix, which files to modify, and the expected outcome
   - Agents cannot conflict because worktree isolation gives each one an independent copy

3. **Merge results** one-by-one into the current branch, in priority order (most critical fixes first):
   ```bash
   git merge <agent-branch> --no-edit
   ```
   If a merge conflicts, resolve it yourself for trivial cases or launch a **debugger agent** for complex ones.

### After all fixes (both strategies)

Run lint and format:
```bash
uv run ruff check --fix .
uv run ruff format .
```

## Phase 4: Verify (read-only parallel, scaled to match Phase 2 tier)

Verification should be proportional to the review depth. Use the same change-size tier from Phase 2.

Include `$CHANGED_FILES` in every verification agent's prompt, same as Phase 2. Instruct agents to focus specifically on verifying that the Phase 3 fixes are correct and haven't introduced new issues.

### Small changes — launch 2 agents:
1. **code-reviewer agent**: Verify the fixes are correct and complete.
2. **security-scanner agent**: Re-scan for remaining issues

### Medium changes — launch 4 agents:
1. **code-reviewer agent**: Verify the fixes are correct and complete.
2. **security-scanner agent**: Re-scan for remaining issues
3. **python-pro agent**: Verify Python-specific fixes (async, types, idioms).
4. **refactor-pro agent**: Verify structural changes didn't degrade design.

### Large changes — launch 6+ agents:
1. **code-reviewer agent** (scope: logic & correctness): Verify logic fixes.
2. **code-reviewer agent** (scope: API contracts): Verify interface fixes.
3. **security-scanner agent**: Re-scan for remaining issues.
4. **python-pro agent**: Verify Python-specific fixes.
5. **refactor-pro agent**: Verify structural changes.
6. **debugger agent**: Verify no new runtime bugs introduced by fixes.

Do NOT run tests here — tests are run once in `/manage` Phase 5 before merge. `/polish` focuses on code quality, not test verification.

**If any agent reports CRITICAL or HIGH issues**: loop back to Phase 3 (max 3 total iterations). MEDIUM and LOW findings from verification are noted in the summary but do not trigger another iteration.

## Phase 5: Commit & Push

1. **Stage specific files** — list them by name, not `git add -A`. This avoids accidentally committing secrets (.env), credentials, or large binaries.
   ```bash
   git add <list of changed files by name>
   ```

2. **Commit** with a conventional commit message that matches the nature of the fixes:
   - Security fixes → `fix: ...`
   - Code restructuring → `refactor: ...`
   - Mixed quality improvements → `chore: ...`
   - Test fixes → `test: ...`
   Choose the type that best represents the dominant change, not always `chore:`.

3. **Push**: `git push origin HEAD`

4. **Monitor CI**:
   ```bash
   gh pr checks 2>/dev/null || gh run list --limit 3
   ```

5. **If CI fails**: use **debugger agent** to analyze logs, fix, and loop back to Phase 4.

## Phase 6: CodeRabbit Review (if PR exists and CodeRabbit is configured)

Only run this phase if the repo uses CodeRabbit. Check by looking for prior CodeRabbit comments on the PR:
```bash
gh api repos/{owner}/{repo}/pulls/{pr}/comments --jq '.[].user.login' 2>/dev/null | grep -q coderabbitai
```

If CodeRabbit is active:
1. Use **coderabbit-monitor agent** to check review status
2. If CodeRabbit has comments:
   - Fix issues sequentially (one agent at a time)
   - Push fixes
   - Re-check review status (max 3 iterations)

## Phase 7: Summary Report

After all phases complete, output a structured summary to the user:

```
## /polish Summary

**Branch**: <branch name>
**Change size**: <Small/Medium/Large> (<N> files, <M> lines)
**Review agents launched**: <count>
**Iterations**: <N> of 3

### Findings
| Severity | Found | Fixed | Skipped |
|----------|-------|-------|---------|
| CRITICAL | X     | X     | 0       |
| HIGH     | X     | X     | 0       |
| MEDIUM   | X     | X     | X       |
| LOW      | X     | X     | X       |

### Key fixes applied
- <one-line description of each significant fix>

### Remaining items (not fixed)
- <any LOW/MEDIUM items that were intentionally skipped, with reason>

### CI Status
- <passing/failing/pending>
```

This summary helps the user quickly understand what /polish did without having to read through all the agent outputs.

---

Usage:
- `/polish` — Polish current branch
- `/polish 123` — Polish pull request #123

Current task context: $ARGUMENTS
