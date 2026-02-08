- never push to main branch, always create feature branch and pull request
- CRITICAL: never merge PRs without explicit user confirmation - always ask first
- CRITICAL: before asking to merge, run thorough local tests (uv run pytest, start app locally, verify key changes work)
- CRITICAL: for large PRs (50+ files), run /polish at least 3-5 times before requesting merge
- CRITICAL: test web applications with Chrome MCP to verify they actually work in a browser
- CRITICAL: always create detailed tasks with dependencies using TaskCreate before starting work
- use `uv` for all Python package management
- use `ruff` for linting and formatting
- prefer async patterns for I/O operations
- run tests with `uv run pytest` before committing

## Self-Improvement
- After any correction from the user, add a rule to this file to prevent recurrence
- Keep rules specific and actionable (not vague)

## Code Quality
- Before creating new utility functions, search the codebase for existing ones
- Check for code duplication when adding new functionality
- Run `/techdebt` at end of major sessions to find issues