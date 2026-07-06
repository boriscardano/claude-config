#!/bin/bash
# PostToolUse hook (Edit|Write): auto-fix + format edited Python files with ruff.
# Prefers the project's pinned ruff (uv run), falls back to global ruff, then uvx.
# Non-blocking by design — never fails the edit.
f=$(jq -r '.tool_input.file_path // empty')
[[ "$f" == *.py && -f "$f" ]] || exit 0
d=$(dirname "$f")
cd "$d" 2>/dev/null || exit 0
if uv run --no-sync ruff --version >/dev/null 2>&1; then
  RUFF=(uv run --no-sync ruff)
elif command -v ruff >/dev/null 2>&1; then
  RUFF=(ruff)
elif command -v uvx >/dev/null 2>&1; then
  RUFF=(uvx ruff)
else
  exit 0
fi
"${RUFF[@]}" check --fix "$f" >/dev/null 2>&1
"${RUFF[@]}" format "$f" >/dev/null 2>&1
exit 0
