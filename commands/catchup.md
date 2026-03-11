---
name: catchup
description: Load all uncommitted changes into context to resume work
---

Sync with remote and show all in-progress work so I can resume.

1. **Fetch remote**: `git fetch origin`

2. **Detect current branch**:
   ```bash
   CURRENT=$(git branch --show-current) && echo "On branch: $CURRENT"
   ```

3. **Sync with remote** (branch-aware):
   - If on `main`/`master`: `git pull origin main --rebase`
   - If on a feature branch: do NOT rebase — just show how far ahead/behind:
     ```bash
     git log --oneline origin/main..HEAD
     git log --oneline HEAD..origin/main
     ```

4. **Show working state** (run all in parallel):
   - `git status` — modified/untracked files
   - `git diff` — unstaged changes
   - `git diff --cached` — staged changes
   - `git log origin/main..HEAD --oneline` — unpushed commits

5. **Check for active worktrees**:
   ```bash
   git worktree list
   ```

6. Summarize what work is in progress and ask what I'd like to continue with.
