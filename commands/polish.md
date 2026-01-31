---
name: polish
description: Review all changes, fix issues, commit and push to origin. Optionally pass a PR number to polish a specific pull request.
---

Execute the complete code polishing workflow.

## Phase 0: Create Task Plan (CRITICAL - DO THIS FIRST)

Before any work, create detailed tasks with dependencies:
1. Use TaskCreate for each phase of work
2. Set up blockedBy dependencies between tasks
3. Update task status as you progress (in_progress -> completed)

Example tasks for /polish:
- Task 1: "Run code review and security scan" (no dependencies)
- Task 2: "Fix identified issues" (blockedBy: Task 1)
- Task 3: "Verify fixes with tests" (blockedBy: Task 2)
- Task 4: "Commit and push" (blockedBy: Task 3)

## Available Agents

Use these specialized agents throughout the workflow:
- **code-reviewer**: Code quality, security, and best practices review
- **code-cleanup**: Remove debug code, unused imports, commented code
- **test-runner**: Run tests, analyze failures, check coverage
- **security-scanner**: Security audits and vulnerability detection
- **refactor-pro**: Code restructuring suggestions
- **python-pro**: Python code fixes and modern patterns
- **fastapi-pro**: API-related fixes
- **streamlit-pro**: Streamlit UI fixes
- **debugger**: Debug issues, test failures, analyze error patterns and logs
- **git-manager**: Git operations and commits
- **deployment-monitor**: CI/CD monitoring
- **coderabbit-monitor**: Monitor CodeRabbit reviews

## Phase 1: Setup (after creating tasks)

If a PR number is provided in $ARGUMENTS:
- Run `gh pr checkout $ARGUMENTS` to checkout the pull request branch
- Run `gh pr diff $ARGUMENTS` to see what changes are in the PR
- If no PR number is provided, work on the current branch

## Phase 2: Parallel Review & Analysis (SINGLE message with multiple Task calls)

Launch ALL these agents IN PARALLEL:

1. **code-reviewer agent** (launch multiple for large PRs):
   - Each reviewer focuses on specific files or directories
   - Check for: security vulnerabilities, performance issues, code quality

2. **security-scanner agent**:
   - Scan for secrets, vulnerabilities, OWASP issues
   - Check dependency security

3. **code-cleanup agent**:
   - Scan for unused imports, debug statements, commented code
   - Identify TODO/FIXME comments that should be addressed

4. **test-runner agent**:
   - Run `uv run pytest -x` to verify tests pass
   - Check coverage levels
   - Identify untested code paths

5. **Run linting**:
   - `uv run ruff check .` to identify lint issues

## Phase 3: Analyze & Categorize Issues

Collect results from all parallel agents and:
- Group issues by type: security, performance, bugs, style, tests
- Group issues by affected files/modules
- Determine which specialized agent type is best for each category:
  * **security-scanner**: Security vulnerabilities, secrets exposure
  * **python-pro**: Python code issues, async problems, type hints, modern Python
  * **fastapi-pro**: FastAPI endpoints, SQLAlchemy, Pydantic, API design
  * **streamlit-pro**: Streamlit UI issues, state management, caching
  * **debugger**: Bugs, test failures, runtime errors, logic issues
  * **refactor-pro**: Code smell fixes, structural improvements
  * **debugger**: Complex error patterns, stack traces, production issues, test failures

## Phase 4: Fix Issues (SINGLE message with multiple Task calls)

Launch multiple fix agents IN PARALLEL based on issue categories:

1. **security-scanner agent**: Fix security vulnerabilities
2. **python-pro agent**: Fix Python code quality issues
3. **streamlit-pro agent**: Fix Streamlit UI issues (if applicable)
4. **fastapi-pro agent**: Fix API issues (if applicable)
5. **refactor-pro agent**: Apply refactoring improvements
6. **code-cleanup agent**: Remove debug code, fix style issues

Provide clear context and file references to each agent.

## Phase 5: Verify Fixes (SINGLE message with multiple Task calls)

Launch ALL IN PARALLEL:

1. **test-runner agent**: Run full test suite, verify coverage
2. **security-scanner agent**: Re-scan for any remaining vulnerabilities
3. **code-reviewer agent**: Quick review of all fixes
4. **debugger agent**: Verify no regressions introduced
5. `uv run ruff check --fix .` - Fix any remaining lint issues

## Phase 6: Commit Changes

Use **git-manager agent** to:
- Stage all changes: `git add -A`
- Create comprehensive commit message describing all fixes
- Follow conventional commit format
- Reference issues if applicable
- Commit all changes

## Phase 7: Push & Monitor

1. **Push to origin**:
   - `git push origin HEAD`
   - If working on a PR, note changes have been pushed

2. **Monitor CI** (use **deployment-monitor agent**):
   - `gh run list --limit 3`
   - `gh pr checks` (if PR exists)
   - Report CI status

3. **If CI fails**:
   - Use **debugger agent** to analyze failure logs and investigate issues
   - Fix issues and repeat from Phase 4

## Phase 8: CodeRabbit Review (if PR)

If working on a PR:

1. Use **coderabbit-monitor agent** to check review status
2. If CodeRabbit has comments, categorize and address using appropriate agents
3. Push fixes and wait for re-review

## Summary

After each major phase, provide a brief summary of what was accomplished.

Usage examples:
- `/polish` - Polish current branch
- `/polish 123` - Polish pull request #123

Current task context: $ARGUMENTS
