---
name: implement-issue
description: Implement a GitHub issue comprehensively using parallel subagents
---

Implement GitHub issue #$ARGUMENTS comprehensively using parallel subagents.

## Phase 0: Create Task Plan (CRITICAL - DO THIS FIRST)

Before any work, create detailed tasks with dependencies:
1. Use TaskCreate for each phase of work
2. Set up blockedBy dependencies between tasks
3. Update task status as you progress (in_progress -> completed)

Example tasks for /implement-issue:
- Task 1: "Setup worktree for issue #$ARGUMENTS" (no dependencies)
- Task 2: "Fetch and analyze issue" (blockedBy: Task 1)
- Task 3: "Implement changes" (blockedBy: Task 2)
- Task 4: "Run QA checks" (blockedBy: Task 3)
- Task 5: "Create PR" (blockedBy: Task 4)
- Task 6: "Polish and cleanup" (blockedBy: Task 5)

## CRITICAL: Use Git Worktree for Isolation

**IMPORTANT**: This command may run in parallel with other implement-issue agents. To avoid conflicts, ALWAYS use a git worktree for isolated development.

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

## Workflow

### Phase 1: Setup Isolated Worktree

1. **Get project name**:
   ```bash
   PROJECT_NAME=$(basename $(git rev-parse --show-toplevel))
   ```

2. **Fetch latest main**:
   ```bash
   git fetch origin main
   ```

3. **Create isolated worktree** (REQUIRED for parallel execution):
   ```bash
   git worktree add ../$PROJECT_NAME-issue-$ARGUMENTS -b feature/issue-$ARGUMENTS origin/main
   ```

4. **Change to worktree directory**:
   ```bash
   cd ../$PROJECT_NAME-issue-$ARGUMENTS
   ```

5. **Verify isolation**:
   ```bash
   pwd  # Should show ../$PROJECT_NAME-issue-$ARGUMENTS
   git branch  # Should show feature/issue-$ARGUMENTS
   ```

**All subsequent work MUST happen in the worktree directory, NOT the main repo.**

### Phase 2: Fetch & Analyze Issue (PARALLEL)

1. **Fetch issue details**:
   ```bash
   gh issue view $ARGUMENTS --json title,body,labels,assignees
   ```

2. **Launch parallel analysis agents** (SINGLE message with multiple Task calls):
   - **Explore agent** (thoroughness: "very thorough"): Analyze codebase to understand context
   - **Plan agent**: Create detailed implementation plan based on issue description
   - **security-scanner agent**: Pre-scan affected areas for existing vulnerabilities

### Phase 3: Implementation (PARALLEL based on issue type)

Launch appropriate subagents IN PARALLEL (SINGLE message with multiple Task calls):

**For Frontend/UI Issues:**
- **streamlit-pro agent**: Implement Streamlit UI changes
- **python-pro agent**: Python logic and patterns
- **code-cleanup agent**: Ensure clean code

**For Backend/API Issues:**
- **python-pro agent**: Implement core logic
- **fastapi-pro agent**: API endpoints and async patterns
- **code-cleanup agent**: Ensure clean code

**For Security Issues:**
- **security-scanner agent**: Detailed security analysis
- **code-reviewer agent**: Security-focused review
- **python-pro agent**: Secure implementation

**For Refactoring Issues:**
- **refactor-pro agent**: Code restructuring
- **python-pro agent**: Modern Python patterns
- **code-cleanup agent**: Clean up after refactoring

### Phase 4: Quality Assurance (ALL IN PARALLEL - SINGLE message)

Launch ALL these agents IN PARALLEL:

1. **test-runner agent**: Run full test suite, analyze failures, check coverage
2. **code-reviewer agent**: Full code review of all changes
3. **security-scanner agent**: Scan for new vulnerabilities introduced
4. **code-cleanup agent**: Remove debug statements, unused imports
5. **debugger agent**: Verify no regressions, investigate any issues
6. Run `uv run ruff check --fix` for linting

### Phase 5: Commit & PR

1. **git-manager agent**: Create atomic commits with conventional commit messages

2. **Push branch from worktree**:
   ```bash
   git push -u origin feature/issue-$ARGUMENTS
   ```

3. **pr-manager agent**: Create PR with comprehensive description:
   ```bash
   gh pr create --base main --title "fix/feat: <title from issue>" --body "Closes #$ARGUMENTS

   ## Summary
   <bullet points of changes>

   ## Testing
   - [ ] Unit tests pass
   - [ ] Manual testing completed
   - [ ] Security scan passed

   Generated with Claude Code"
   ```

### Phase 6: Polish

1. Run `/polish` command to review, fix issues, and push
2. Use **coderabbit-monitor agent** to wait for CodeRabbit review
3. Address feedback using appropriate fix agents

### Phase 7: Cleanup Worktree

After PR is merged OR if abandoning work:

1. **Return to main repository**:
   ```bash
   cd $(git rev-parse --show-toplevel)  # Return to original repo
   ```

2. **Remove worktree**:
   ```bash
   git worktree remove ../$PROJECT_NAME-issue-$ARGUMENTS
   ```

3. **Clean up branch** (after merge):
   ```bash
   git fetch --prune
   git branch -d feature/issue-$ARGUMENTS
   ```

## Key Rules

- **ALWAYS use git worktree** - Never work in main repo when running parallel agents
- **Use subagents extensively in parallel** - Launch multiple agents in SINGLE message
- **Never work on main branch** - Always use feature branches
- **Atomic commits** - Each logical change in separate commit
- **Run tests** before and after changes
- **Security scan** all changes before PR
- **Clean up worktree** after PR is merged

## Parallel Execution Safety

When multiple `/implement-issue` commands run simultaneously:
- Each gets its own worktree: `../podcasts-chatbot-issue-97`, `../podcasts-chatbot-issue-98`, etc.
- Each works on isolated branch: `feature/issue-97`, `feature/issue-98`, etc.
- No file conflicts between agents
- Each creates separate PR

## Example Usage

```bash
# Single issue
/implement-issue 97

# Multiple issues in parallel (each in separate terminal/agent)
/implement-issue 97  # → worktree: ../podcasts-chatbot-issue-97
/implement-issue 98  # → worktree: ../podcasts-chatbot-issue-98
/implement-issue 99  # → worktree: ../podcasts-chatbot-issue-99
```

Current issue: $ARGUMENTS
