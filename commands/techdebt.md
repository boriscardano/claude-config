---
name: techdebt
description: Audit the codebase (or a focus area) for technical debt — duplication, dead code, complexity hotspots, risky patterns, outdated dependencies, and test-coverage gaps — and produce a prioritized report. Report-only; changes nothing.
argument-hint: "[path or focus area]"
---

Audit technical debt in this repository and produce a prioritized, actionable report.

**This command is READ-ONLY.** Do not modify, create, or delete any files. Do not run tests. Report findings; fixing is a separate decision for the user.

Focus area: $ARGUMENTS (if empty, audit the whole repo)

## Phase 1: Scope & churn analysis

1. Establish the repo root and main source tree:
   ```bash
   git rev-parse --show-toplevel
   ```
2. Determine scope: the `$ARGUMENTS` path if given, otherwise the primary source tree. Exclude vendored, generated, and migration files.
3. Find churn hotspots — debt hurts most in files that change often:
   ```bash
   git log --since="3 months ago" --pretty=format: --name-only | grep -v '^$' | sort | uniq -c | sort -rn | head -15
   ```
4. Note repo size (`git ls-files | wc -l`) to calibrate how many findings to expect.

## Phase 2: Parallel audit (read-only, single message)

Launch these agents **in parallel** (one message, multiple Agent calls). Every prompt MUST include: the scope from Phase 1, the churn hotspot list, and this block:

```
This is a READ-ONLY audit. Do NOT modify any files. Do NOT run any tests or pytest commands.
Tag every finding with severity (CRITICAL/HIGH/MEDIUM/LOW) and file:line references.
```

1. **code-reviewer agent** — correctness debt: fragile logic, missing error handling, race conditions, swallowed exceptions in the scoped files (prioritize churn hotspots).
2. **refactor-pro agent** — structural debt: duplication across modules, god functions/classes, deep nesting, tangled dependencies, copy-paste drift. REPORT ONLY, no refactoring.
3. **code-cleanup agent** — dead code, unused imports, debug statements, stale TODO/FIXME markers, leftover temp files. REPORT ONLY, no cleanup.
4. **security-scanner agent** — hardcoded secrets, injection risks, unsafe deserialization, debug flags, permissive CORS.

While agents run, do these in the main session:

5. **Dependency health**:
   ```bash
   uv pip list --outdated
   pip-audit 2>/dev/null || echo "pip-audit not installed"
   ```
6. **Test-coverage gaps** (heuristic — do NOT run pytest): map source modules to test files by name (`src/foo.py` ↔ `tests/**/test_foo*.py` or similar convention). List source modules with no corresponding test file, prioritizing the churn hotspots from Phase 1.

## Phase 3: Synthesize

1. **Deduplicate**: merge findings from different agents that point at the same file + line range (within ~5 lines); keep the most detailed description and highest severity.
2. **Score** each item:
   - **Impact**: High (bugs waiting to happen, blocks changes, security) / Medium (slows development) / Low (cosmetic)
   - **Effort**: S (< 1 hour) / M (half a day) / L (multi-day, needs planning)
3. **Prioritize**: High impact + S/M effort first. Weight items in churn hotspots higher — debt in hot files compounds fastest.

## Phase 4: Report

```
## Tech Debt Report — <repo> (<scope>)

**Files audited**: <N> | **Churn hotspots**: <top 3-5 files>

### Top quick wins (high impact, low effort)
| # | Issue | Files | Impact | Effort |
|---|-------|-------|--------|--------|
| 1 | ...   | ...   | High   | S      |

### Bigger refactors worth planning
- <item — why it matters, what it would take>

### Dependency & security
- <outdated packages with known issues, audit findings>

### Test-coverage gaps
- <untested modules, hotspots first>

### Noted but not worth fixing
- <low-value items, with a one-line reason each>
```

## Phase 5: Follow-up (offer, don't do)

Ask the user which (if any) they want:
- **Create GitHub issues** for the top items (`gh issue create` with a clear body per item; label `tech-debt`)
- **Fix the quick wins now** — on a feature branch, then run `/polish`
- **Nothing** — report stands as documentation

Do not create issues or fix anything without the user choosing to.
