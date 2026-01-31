---
name: catchup
description: Load all uncommitted changes into context to resume work
---

Show me all uncommitted changes so I can understand the current state:

1. Run `git status` to see modified/untracked files
2. Run `git diff` to see unstaged changes
3. Run `git diff --cached` to see staged changes
4. Run `git log origin/main..HEAD --oneline` to see unpushed commits

Summarize what work is in progress and ask what I'd like to continue with.
