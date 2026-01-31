# Claude Code Configuration

My personal [Claude Code](https://claude.ai/claude-code) configuration with custom agents, commands, and settings.

## Setup

Clone to your home directory:

```bash
git clone https://github.com/boriscardano/claude-config.git ~/.claude
```

Or if you already have a `~/.claude` directory, clone elsewhere and copy what you need.

## What's Included

### Custom Agents (`agents/`)

| Agent | Purpose |
|-------|---------|
| `python-pro` | Python 3.12+ development, async, modern patterns |
| `fastapi-pro` | FastAPI, SQLAlchemy 2.0, Pydantic V2 |
| `streamlit-pro` | Streamlit apps, state management, caching |
| `code-reviewer` | Code quality, security, best practices |
| `security-scanner` | Vulnerability scanning, secrets detection |
| `debugger` | Systematic debugging, error analysis, log parsing |
| `test-runner` | Run tests, analyze failures, coverage |
| `git-manager` | Git operations, conventional commits |
| `pr-manager` | GitHub PR creation and management |
| `code-cleanup` | Remove debug code, unused imports |
| `refactor-pro` | Code restructuring, technical debt |
| `docs-architect` | Technical documentation generation |
| `deployment-monitor` | CI/CD and deployment monitoring |
| `coderabbit-monitor` | CodeRabbit review status tracking |

### Custom Commands (`commands/`)

| Command | Purpose |
|---------|---------|
| `/polish` | Review all changes, fix issues, commit and push |
| `/implement-issue <n>` | Full GitHub issue implementation with worktrees |
| `/batch-implement <n n n>` | Multiple related issues in single branch |
| `/ship` | Feature branch to production workflow |
| `/fix-issue <n>` | Quick single-issue fix (no worktrees) |
| `/catchup` | Resume work by loading uncommitted changes |

### Settings

- **Auto-formatting**: Python files auto-formatted with `ruff` after every edit
- **MCP Servers**: Supabase (database), Chrome DevTools (browser automation)
- **Task tracking**: All commands create tasks with dependencies

## Machine-Specific Config

Create `settings.local.json` for machine-specific settings (not tracked):

```json
{
  "permissions": {
    "allow": [
      "Bash(uv:*)",
      "Bash(ruff:*)",
      "Bash(pytest:*)",
      "Bash(gh pr:*)",
      "Bash(gh issue:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Edit(*)"
    ]
  }
}
```

## Environment Variables

Set these for MCP servers:

```bash
export SUPABASE_ACCESS_TOKEN="your-token"
```

## License

MIT - feel free to use and modify.
