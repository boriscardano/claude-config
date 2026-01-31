---
name: batch-implement
description: Implement multiple related GitHub issues in a single feature branch
---

Implement multiple related GitHub issues in a single feature branch.

Arguments: $ARGUMENTS (space-separated issue numbers, e.g., "97 98 99")

## Phase 0: Create Task Plan (CRITICAL - DO THIS FIRST)

Before any work, create detailed tasks with dependencies:
1. Use TaskCreate for each phase of work
2. Set up blockedBy dependencies between tasks
3. Update task status as you progress (in_progress -> completed)

Example tasks for /batch-implement:
- Task 1: "Setup worktree for batch issues" (no dependencies)
- Task 2: "Fetch and plan all issues" (blockedBy: Task 1)
- Task 3: "Analyze codebase for affected areas" (blockedBy: Task 2)
- Task 4: "Implement UI/frontend issues" (blockedBy: Task 3)
- Task 5: "Implement backend/API issues" (blockedBy: Task 3)
- Task 6: "Run QA checks" (blockedBy: Task 4, Task 5)
- Task 7: "Create PR" (blockedBy: Task 6)
- Task 8: "Polish and cleanup" (blockedBy: Task 7)

## CRITICAL: Use Git Worktree for Isolation

**IMPORTANT**: This command may run in parallel with other batch-implement commands. To avoid conflicts, ALWAYS use a git worktree for isolated development.

## Available Agents

Use these specialized agents throughout the workflow:
- **Explore**: Codebase exploration and understanding
- **Plan**: Implementation planning and architecture
- **python-pro**: Python development and modern patterns
- **fastapi-pro**: FastAPI/API development
- **streamlit-pro**: Streamlit UI development
- **code-reviewer**: Code quality and security review
- **code-cleanup**: Remove debug code, unused imports
- **debugger**: Debug issues and test failures
- **test-runner**: Run tests and analyze coverage
- **security-scanner**: Security audits and vulnerability checks
- **refactor-pro**: Code restructuring and improvements
- **git-manager**: Git operations and commits
- **pr-manager**: PR creation and management
- **coderabbit-monitor**: Monitor CodeRabbit reviews

## Workflow

### Phase 1: Setup Isolated Worktree

1. **Parse issue numbers** from `$ARGUMENTS`
   - Extract first and last issue numbers for naming

2. **Get project name**:
   ```bash
   PROJECT_NAME=$(basename $(git rev-parse --show-toplevel))
   ```

3. **Fetch latest main**:
   ```bash
   git fetch origin main
   ```

4. **Create isolated worktree** (REQUIRED for parallel execution):
   ```bash
   git worktree add ../$PROJECT_NAME-batch-<first>-<last> -b feature/issues-<first>-to-<last> origin/main
   ```

   Example: For `$ARGUMENTS = "97 98 99 100 101"`:
   ```bash
   git worktree add ../$PROJECT_NAME-batch-97-101 -b feature/issues-97-to-101 origin/main
   ```

5. **Change to worktree directory**:
   ```bash
   cd ../$PROJECT_NAME-batch-<first>-<last>
   ```

6. **Verify isolation**:
   ```bash
   pwd  # Should show ../$PROJECT_NAME-batch-<first>-<last>
   git branch  # Should show feature/issues-<first>-to-<last>
   ```

**All subsequent work MUST happen in the worktree directory, NOT the main repo.**

### Phase 2: Fetch & Plan Issues (PARALLEL)

1. **Fetch all issues IN PARALLEL** (SINGLE message with multiple Task calls):
   - Launch one **general-purpose agent** per issue to fetch: `gh issue view <number> --json title,body,labels`

2. **Plan agent**: Analyze all issues together:
   - Identify common files affected
   - Determine implementation order (dependencies)
   - Group related changes

### Phase 3: Parallel Analysis (SINGLE message with multiple Task calls)

Launch ALL IN PARALLEL:

1. **Explore agent** (thoroughness: "very thorough"):
   - Understand all files that will be modified
   - Map dependencies between issues

2. **code-reviewer agent** (for each unique file):
   - Pre-review existing code
   - Identify potential conflicts

3. **security-scanner agent**:
   - Pre-scan affected areas for existing vulnerabilities
   - Identify security-sensitive code paths

### Phase 4: Implementation (Grouped by Category)

Group issues by type and launch appropriate agents IN PARALLEL:

**Group 1: UI/Frontend issues**
- **streamlit-pro agent**: Streamlit-specific patterns and optimizations
- **python-pro agent**: Python logic and state management
- Single commit for related frontend changes

**Group 2: Backend/API issues**
- **python-pro agent**: Core logic implementation
- **fastapi-pro agent**: API endpoints, async patterns
- Commit per logical change

**Group 3: Refactoring issues**
- **refactor-pro agent**: Code restructuring
- **python-pro agent**: Modern Python patterns
- **code-cleanup agent**: Clean up after refactoring

**Group 4: Security issues**
- **security-scanner agent**: Vulnerability analysis
- **python-pro agent**: Secure implementation

### Phase 5: Quality Assurance (ALL IN PARALLEL - SINGLE message)

Launch ALL these agents IN PARALLEL:

1. **test-runner agent**: Run full test suite, check coverage, analyze failures
2. **code-reviewer agent**: Review all changes holistically
3. **security-scanner agent**: Final security scan of all changes
4. **code-cleanup agent**: Clean up across all modified files
5. **debugger agent**: Verify no regressions
6. Run `uv run ruff check --fix .` - Lint all files

### Phase 6: Commit Strategy

Use **git-manager agent** with atomic commits per issue:
```
fix(ui): add type hints to streamlit components (#97)
fix(ui): implement proper error boundaries (#98)
fix(backend): add rate limiting to API (#99)
```

Or grouped commits if changes are tightly coupled:
```
fix(frontend): address UI issues #97, #98, #100
fix(backend): address API issues #99, #101
```

### Phase 7: Push & Create PR

1. **Push branch from worktree**:
   ```bash
   git push -u origin feature/issues-<first>-to-<last>
   ```

2. Use **pr-manager agent** to create PR:
   ```bash
   gh pr create --base main --title "fix: implement issues #<first>-#<last>" --body "## Summary

   This PR implements multiple related issues:

   ### Issues Addressed
   - Closes #<issue1> - <title1>
   - Closes #<issue2> - <title2>
   ...

   ## Changes by Category

   ### Frontend
   - <change1>

   ### Backend
   - <change2>

   ## Security
   - Security scan: PASSED
   - No new vulnerabilities introduced

   ## Testing
   - [ ] All unit tests pass
   - [ ] Coverage maintained/improved
   - [ ] No regressions

   Generated with Claude Code"
   ```

### Phase 8: Polish & Ship

1. Run `/polish` command
2. Use **coderabbit-monitor agent** to wait for CodeRabbit review
3. Address feedback using appropriate agents:
   - **python-pro agent**: Code quality fixes
   - **debugger agent**: Bug fixes
   - **code-cleanup agent**: Style fixes
   - **security-scanner agent**: Security fixes
4. Run `/ship` when ready

### Phase 9: Cleanup Worktree

After PR is merged OR if abandoning work:

1. **Return to main repository**:
   ```bash
   cd $(git rev-parse --show-toplevel)  # Return to original repo
   ```

2. **Remove worktree**:
   ```bash
   git worktree remove ../$PROJECT_NAME-batch-<first>-<last>
   ```

3. **Clean up branch** (after merge):
   ```bash
   git fetch --prune
   git branch -d feature/issues-<first>-to-<last>
   ```

## Key Rules

- **ALWAYS use git worktree** - Never work in main repo when running parallel batches
- **Use subagents extensively in parallel** - Launch multiple agents in SINGLE message
- **Never work on main branch** - Always use feature branches
- **Atomic commits** - One commit per issue when possible
- **Security scan** - Always run before creating PR
- **Clean up worktree** after PR is merged

## Parallel Execution Safety

When multiple `/batch-implement` commands run simultaneously:
- Each gets its own worktree: `../$PROJECT_NAME-batch-97-101`, `../$PROJECT_NAME-batch-102-105`, etc.
- Each works on isolated branch: `feature/issues-97-to-101`, `feature/issues-102-to-105`, etc.
- No file conflicts between agents
- Each creates separate PR

## Best Practices

- **Group related issues** - Don't batch unrelated changes
- **Limit batch size** - 3-5 issues maximum
- **Same category** - Batch frontend OR backend, not mixed
- **Atomic commits** - One commit per issue when possible
- **Security scan** - Always run before creating PR
- **Parallel agents** - Maximize efficiency with parallel execution

## Example Usage

```bash
# Terminal 1: Frontend HIGH priority
/batch-implement 97 98 99 100 101
# → worktree: ../$PROJECT_NAME-batch-97-101
# → branch: feature/issues-97-to-101

# Terminal 2: Frontend MEDIUM priority
/batch-implement 102 103 104 105
# → worktree: ../$PROJECT_NAME-batch-102-105
# → branch: feature/issues-102-to-105

# Terminal 3: Backend HIGH priority
/batch-implement 106 107 108 109
# → worktree: ../$PROJECT_NAME-batch-106-109
# → branch: feature/issues-106-to-109

# Terminal 4: Backend MEDIUM priority
/batch-implement 110 111 112
# → worktree: ../$PROJECT_NAME-batch-110-112
# → branch: feature/issues-110-to-112
```

Current issues: $ARGUMENTS
