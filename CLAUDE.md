- never push to main branch, always create feature branch and pull request
- CRITICAL: never merge PRs without explicit user confirmation - always ask first
- NOTE: both rules are mechanically enforced by a PreToolUse hook (~/.claude/hooks/git-guard.py): pushes to main/master are denied, and `gh pr merge` is always denied — Claude never merges. When a PR is ready, hand Boris the exact command to run himself: `! gh pr merge <PR#> --squash --delete-branch`. Denials are intentional; never attempt workarounds
- CRITICAL: before asking to merge, run thorough local tests (uv run pytest, start app locally, verify key changes work)
- CRITICAL: after finishing ANY feature or bug fix, automatically run /polish before asking to merge — do NOT wait to be asked. One pass for a normal change; 3-5 passes for large PRs (50+ files)
- CRITICAL: test web applications with Chrome MCP to verify they actually work in a browser
- CRITICAL: always create detailed tasks with dependencies using TaskCreate before starting work
- use `uv` for all Python package management
- use `ruff` for linting and formatting
- prefer async patterns for I/O operations
- run tests with `uv run pytest` before committing

## Self-Improvement
- After any correction from the user, add a rule to this file to prevent recurrence
- Keep rules specific and actionable (not vague)
- Before stating that an action did or did NOT happen, verify against the authoritative record (logs, DB, the actual system) — never infer an outcome from a single derived or possibly-empty field (e.g. a `drive_folder_url` left blank by one code path), and never just confirm a user's assumption without checking the source of truth first.

## Code Quality
- Before creating new utility functions, search the codebase for existing ones
- Check for code duplication when adding new functionality
- Run `/techdebt` at end of major sessions to find issues
- Favor simplicity; do not over-engineer. For agent/bot projects (e.g. slack-claude-bot), keep app code thin — push behavior, formatting, and policy into the managed agent's prompt/config rather than the application layer. Avoid adding locks/caches/queues/TTL machinery to the app unless clearly needed.