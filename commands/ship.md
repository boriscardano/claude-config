---
name: ship
description: Complete workflow from feature branch to production deployment
---

Execute the complete shipping workflow from feature branch to production.

## Phase 0: Create Task Plan (CRITICAL - DO THIS FIRST)

Before any work, create detailed tasks with dependencies:
1. Use TaskCreate for each phase of work
2. Set up blockedBy dependencies between tasks
3. Update task status as you progress (in_progress -> completed)

Example tasks for /ship:
- Task 1: "Run pre-flight checks" (no dependencies)
- Task 2: "Commit and prepare" (blockedBy: Task 1)
- Task 3: "Create/update PR" (blockedBy: Task 2)
- Task 4: "Wait for CodeRabbit review" (blockedBy: Task 3)
- Task 5: "Address feedback" (blockedBy: Task 4)
- Task 6: "Merge and deploy" (blockedBy: Task 5)

## Available Agents

Use these specialized agents throughout the workflow:
- **code-reviewer**: Final code quality and security review
- **code-cleanup**: Remove debug code before shipping
- **test-runner**: Run tests and verify coverage
- **security-scanner**: Final security audit before deployment
- **debugger**: Analyze CI failures, production logs, and debug any issues
- **git-manager**: Git operations and commits
- **pr-manager**: PR creation and management
- **coderabbit-monitor**: Monitor CodeRabbit reviews
- **deployment-monitor**: Monitor CI/CD and deployments
- **python-pro**: Fix Python code issues
- **fastapi-pro**: Fix API issues
- **streamlit-pro**: Fix Streamlit issues

## Phase 1: Pre-Flight Checks (SINGLE message with multiple Task calls - ALL IN PARALLEL)

Launch ALL these checks IN PARALLEL:

1. **Verify branch status**:
   - `git status` - Ensure clean working directory
   - `git log origin/main..HEAD --oneline` - Show commits to ship

2. **test-runner agent**:
   - Run full test suite: `uv run pytest`
   - All tests must pass
   - Check coverage levels

3. **Run linting**:
   - `uv run ruff check .` - No lint errors allowed

4. **code-reviewer agent**:
   - Final security and quality review of all changes

5. **security-scanner agent**:
   - Final security audit
   - Check for secrets, vulnerabilities
   - Verify no security regressions

6. **code-cleanup agent**:
   - Remove unused code, debug statements, commented code
   - Verify no temporary files remain

If ANY check fails, stop and fix issues before proceeding.

## Phase 2: Commit & Prepare

Use **git-manager agent** to:
- Stage all changes
- Generate conventional commit messages
- Create atomic commits (one per logical change)
- Ensure commits are clean and well-described

## Phase 3: Create/Update PR

Use **pr-manager agent** to:

1. Check if PR exists:
   - `gh pr view --json number,state 2>/dev/null || echo "NO_PR"`

2. If no PR exists:
   - Push branch: `git push -u origin HEAD`
   - Create PR: `gh pr create --base main --fill`
   - Add relevant labels

3. If PR exists but draft:
   - `gh pr ready` to mark ready for review

## Phase 4: Wait for CodeRabbit Review

Use **coderabbit-monitor agent** to:
- Wait for CodeRabbit to complete initial review
- Check status every 30 seconds via `gh pr checks`
- Timeout after 30 minutes
- Report review status and findings

## Phase 5: Address CodeRabbit Feedback

If CodeRabbit has suggestions:

1. Analyze all comments and categorize by severity

2. Launch fix agents IN PARALLEL based on issue types:
   - **security-scanner agent**: Security issues
   - **python-pro agent**: Code quality, Python issues
   - **streamlit-pro agent**: Streamlit UI issues
   - **fastapi-pro agent**: API issues
   - **debugger agent**: Bug fixes, logic issues
   - **code-cleanup agent**: Style, cleanup issues

3. Use **git-manager agent** to commit fixes with clear messages referencing CodeRabbit comments

4. Push changes: `git push origin HEAD`

5. Return to Phase 4 (max 5 iterations)

## Phase 6: Merge PR

Once CodeRabbit approves:

1. Verify all CI checks pass:
   - `gh pr checks --watch`

2. Use **pr-manager agent** to merge:
   - `gh pr merge --squash --delete-branch`

3. Update local main:
   - `git checkout main`
   - `git pull origin main`

## Phase 7: Monitor Deployment

Use **deployment-monitor agent** to:

1. Watch GitHub Actions deploy workflow:
   - `gh run list --workflow=deploy.yaml --limit 3`
   - `gh run watch`

2. Check Cloud Run deployment status:
   - `gcloud run services describe podcasts-chatbot --region=europe-west3 --format="value(status.url)"`

3. Report deployment success or failure with logs

4. If deployment fails:
   - Use **debugger agent** to analyze logs
   - Investigate and fix before proceeding

## Phase 8: Post-Deployment Verification

1. **Health check**:
   ```bash
   curl -s -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
     https://podcasts-chatbot-348848615584.europe-west3.run.app/health
   ```

2. **Quick smoke test** (if applicable):
   - Test critical endpoints
   - Verify no errors in logs

3. **If issues found**:
   - Use **debugger agent** to analyze production logs:
     ```bash
     gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=podcasts-chatbot" --limit=20
     ```
   - Investigate and fix issues

## Phase 9: Cleanup

1. Prune old branches:
   - `git fetch --prune`
   - `git branch -d <merged-branch>` (if not auto-deleted)

2. Verify clean state:
   - `git status`
   - Confirm on main branch

## Rollback Procedure (if needed)

If deployment fails or critical issues found:

1. Find previous revision:
   ```bash
   gcloud run revisions list --service=podcasts-chatbot --region=europe-west3
   ```

2. Route traffic to previous revision:
   ```bash
   gcloud run services update-traffic podcasts-chatbot \
     --to-revisions=<previous-revision>=100 \
     --region=europe-west3
   ```

3. Use **error-detective agent** to investigate
4. Fix issues before re-shipping

## Summary

After each major phase, provide a summary and wait for confirmation before proceeding to the next phase.

Current task: $ARGUMENTS
