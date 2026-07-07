#!/usr/bin/env python3
"""PreToolUse guard for the Bash tool — enforces CLAUDE.md git rules.

- DENY any `git push` that targets main/master (never push to main).
- ASK on `gh pr merge` / `gh api ...merge...`. The hook cannot know whether the
  user asked for the merge, so it delegates that judgment to a confirmation
  prompt. The policy "only merge when the user explicitly asked" is enforced at
  the instruction layer (CLAUDE.md / pr-manager); this prompt is the human gate.

Fail-open on unexpected errors (a crashing guard must not block all Bash),
fail-closed when a push target cannot be determined.
"""

import json
import os
import re
import shlex
import subprocess
import sys

PROTECTED = {"main", "master"}
WRAPPERS = {"sudo", "command", "env", "nohup", "time", "timeout", "caffeinate", "xargs"}
SHELLS = {"bash", "sh", "zsh", "dash", "fish"}
GIT_VALUE_OPTS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}


def tokenize(command):
    lex = shlex.shlex(command, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    try:
        return list(lex)
    except ValueError:
        return command.split()


def split_segments(tokens):
    """Split a token stream into simple commands on shell operators."""
    segments, current = [], []
    for tok in tokens:
        if re.fullmatch(r"[|;&()]+", tok):
            if current:
                segments.append(current)
            current = []
        else:
            current.append(tok)
    if current:
        segments.append(current)
    return segments


def strip_redirects(seg):
    """Drop redirections: `> file`, `2>&1`, `< in` and fd digits before them."""
    is_redirect = lambda t: bool(re.fullmatch(r"[<>&]+", t)) and (">" in t or "<" in t)
    out, i = [], 0
    while i < len(seg):
        tok = seg[i]
        if is_redirect(tok):
            i += 2  # skip operator and its target
            continue
        if tok.isdigit() and i + 1 < len(seg) and is_redirect(seg[i + 1]):
            i += 1  # fd number in front of a redirect (2>&1)
            continue
        out.append(tok)
        i += 1
    return out


def strip_wrappers(seg):
    """Drop leading VAR=val assignments and wrapper commands (sudo, env, ...)."""
    seg = list(seg)
    while seg:
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", seg[0]):
            seg.pop(0)
            continue
        if seg[0] in WRAPPERS:
            wrapper = seg.pop(0)
            while seg and (seg[0].startswith("-") or seg[0] == "{}"):
                seg.pop(0)
            if (
                wrapper == "timeout"
                and seg
                and re.fullmatch(r"\d+(\.\d+)?[smhd]?", seg[0])
            ):
                seg.pop(0)
            continue
        break
    return seg


def resolve_path(path, base):
    path = os.path.expanduser(path)
    if os.path.isabs(path):
        return os.path.normpath(path)
    if not base:
        return ""
    return os.path.normpath(os.path.join(base, path))


def current_branch(workdir):
    if not workdir or not os.path.isdir(workdir):
        return ""
    try:
        r = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return r.stdout.strip()
    except Exception:
        return ""


def parse_git(seg, cwd):
    """Return (subcommand, args_after_subcommand, workdir) for a git segment."""
    workdir = cwd
    i = 1
    while i < len(seg):
        tok = seg[i]
        if tok == "-C" and i + 1 < len(seg):
            workdir = resolve_path(seg[i + 1], cwd)
            i += 2
            continue
        if tok in GIT_VALUE_OPTS and i + 1 < len(seg):
            i += 2
            continue
        if tok.startswith("-"):
            i += 1
            continue
        return tok, seg[i + 1 :], workdir
    return None, [], workdir


def resolve_dst(refspec, workdir):
    """Destination branch of a refspec, or None if it cannot be determined."""
    dst = refspec.split(":", 1)[1] if ":" in refspec else refspec
    dst = dst.lstrip("+")
    if dst.startswith("refs/heads/"):
        dst = dst[len("refs/heads/") :]
    if not dst:
        return None
    if "$" in dst or "`" in dst or dst == "HEAD":
        return current_branch(workdir) or None  # dynamic — best effort, else unknown
    return dst


DENY_TARGET = (
    "This push targets '%s'. CLAUDE.md forbids pushing to main/master "
    "— create a feature branch and open a PR instead."
)
DENY_CURRENT = (
    "This would push the current branch '%s' directly. CLAUDE.md forbids "
    "pushing to %s — create a feature branch and open a PR instead."
)
DENY_UNKNOWN = (
    "Could not determine which branch this push targets (main/master must "
    "never be pushed directly). Re-run with an explicit literal refspec, "
    "e.g. `git push origin <feature-branch>`."
)


def push_denial(seg, cwd):
    """Return a denial reason if this segment pushes to a protected branch."""
    if not seg or seg[0] != "git":
        return None
    sub, args, workdir = parse_git(seg, cwd)
    if sub != "push":
        return None
    if "--dry-run" in args or "-n" in args:
        return None
    positionals = [a for a in args if not a.startswith("-")]
    if "--tags" in args and len(positionals) <= 1:
        return None  # pushes tags only, not a branch
    if len(positionals) <= 1:
        # implicit refspec: pushes the current branch
        branch = current_branch(workdir)
        if branch in PROTECTED:
            return DENY_CURRENT % (branch, branch)
        if not branch:
            return DENY_UNKNOWN
        return None
    for refspec in positionals[1:]:
        dst = resolve_dst(refspec, workdir)
        if dst is None:
            return DENY_UNKNOWN
        if dst in PROTECTED:
            return DENY_TARGET % dst
    return None


def is_pr_merge(seg):
    if not seg or seg[0] != "gh":
        return False
    if "pr" in seg and "merge" in seg:
        return True
    if "api" in seg and any("/merge" in t for t in seg):
        return True
    return False


def analyze(command, cwd, depth=0):
    """Return (deny_reason_or_None, wants_merge)."""
    if depth > 3:
        return None, False
    wants_merge = False
    effective_cwd = cwd
    for seg in split_segments(tokenize(command)):
        seg = strip_wrappers(strip_redirects(seg))
        if not seg:
            continue
        if seg[0] == "cd":
            effective_cwd = (
                resolve_path(seg[1], effective_cwd)
                if len(seg) > 1
                else os.path.expanduser("~")
            )
            continue
        if seg[0] in SHELLS and "-c" in seg:
            i = seg.index("-c")
            if i + 1 < len(seg):
                reason, merge = analyze(seg[i + 1], effective_cwd, depth + 1)
                if reason:
                    return reason, False
                wants_merge = wants_merge or merge
            continue
        reason = push_denial(seg, effective_cwd)
        if reason:
            return reason, False
        if is_pr_merge(seg):
            wants_merge = True
    return None, wants_merge


def emit(decision, reason):
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def main():
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        return
    command = (data.get("tool_input") or {}).get("command") or ""
    if "git" not in command and "gh" not in command:
        return
    reason, wants_merge = analyze(command, data.get("cwd") or ".")
    if reason:
        emit("deny", reason)
    elif wants_merge:
        emit(
            "ask",
            "Confirm PR merge. Only proceed if Boris explicitly asked for this "
            "merge in his request — never autonomously, and never as a side effect "
            "of /polish, /manage, /implement-issue, or because CI/CodeRabbit passed. "
            "If it wasn't explicitly requested, decline and report the PR as ready instead.",
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)  # fail open: a broken guard must not block every Bash call
