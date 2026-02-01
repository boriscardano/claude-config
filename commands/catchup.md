---
name: catchup
description: Load all uncommitted changes into context to resume work
---

First, sync with the remote repository:

1. Run `git fetch origin` to get latest remote changes
2. Run `git pull origin main --rebase` to pull latest changes from main (if on main branch) or rebase current branch on latest main

Then show me all uncommitted changes so I can understand the current state:

3. Run `git status` to see modified/untracked files
4. Run `git diff` to see unstaged changes
5. Run `git diff --cached` to see staged changes
6. Run `git log origin/main..HEAD --oneline` to see unpushed commits

Summarize what work is in progress and ask what I'd like to continue with.
