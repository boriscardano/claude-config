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

## Phase 2: Parallel Review (read-only, single message)

Launch ALL in parallel:

1. **code-reviewer agent**: Review all changed files for quality, bugs, and best practices. IMPORTANT: Include in the agent prompt: "Do NOT run any tests or pytest commands. Only read and analyze code." (Code-reviewer agents running tests causes timeout loops.)
2. **security-scanner agent**: Scan for secrets, vulnerabilities, OWASP issues, dependency security
3. **code-cleanup agent**: Scan for unused imports, debug statements, commented code, stale TODOs
4. **test-runner agent**: Run `uv run pytest` (no `-x` — show ALL failures). Set bash timeout to 600000 (10 min) since test suites can be slow. Do NOT pass `--timeout` flag to pytest — it is not supported.
5. Run lint and format check (identify only, don't fix yet):
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   ```

## Phase 3: Fix Issues (max 3 iterations)

Collect all findings from Phase 2 and categorize them. The fix strategy depends on how many independent issue groups there are.

### Choosing the right agent per issue type

- Security vulnerabilities → **python-pro agent** (with security context from scanner)
- Python code quality → **python-pro agent**
- API issues → **fastapi-pro agent**
- UI issues → **streamlit-pro agent**
- Code structure → **refactor-pro agent**
- Cleanup (dead code, imports) → **code-cleanup agent**
- Test failures → **debugger agent**

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

## Phase 4: Verify (read-only parallel, then loop if needed)

Launch in parallel:
1. **test-runner agent**: Run full test suite (bash timeout: 600000). Do NOT pass `--timeout` to pytest.
2. **code-reviewer agent**: Quick review of the fixes. Include: "Do NOT run any tests or pytest commands. Only read and analyze code."
3. **security-scanner agent**: Re-scan for remaining issues

**If any agent reports failures**: loop back to Phase 3 (max 3 total iterations). Do NOT proceed with failing tests — the point is to ship clean code.

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

---

Usage:
- `/polish` — Polish current branch
- `/polish 123` — Polish pull request #123

Current task context: $ARGUMENTS
