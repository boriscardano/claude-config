#!/usr/bin/env python3
"""Stop/Notification hook: macOS notification when Claude needs input, or when
a long turn finishes. Silent no-op on any error — never blocks the session.

- Notification event: always notify (fires only when attention is needed).
- Stop event: notify only if the turn ran >= MIN_SECONDS (skips quick replies)
  and <= MAX_SECONDS (skips stale timestamps from idle sessions / clears).
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

MIN_SECONDS = 90
MAX_SECONDS = 3 * 3600
MAX_TRANSCRIPT_BYTES = 50 * 1024 * 1024


def notify(message, title="Claude Code", sound=None):
    msg = message.replace("\\", "\\\\").replace('"', '\\"')
    ttl = title.replace("\\", "\\\\").replace('"', '\\"')
    script = 'display notification "%s" with title "%s"' % (msg, ttl)
    if sound:
        script += ' sound name "%s"' % sound
    subprocess.run(["osascript", "-e", script], capture_output=True, timeout=10)


def is_user_prompt(entry):
    """A real user message — not a tool result, meta entry, or subagent line."""
    if entry.get("type") != "user" or entry.get("isMeta") or entry.get("isSidechain"):
        return False
    if "toolUseResult" in entry:
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list):
        return not any(
            c.get("type") == "tool_result" for c in content if isinstance(c, dict)
        )
    return isinstance(content, str)


def turn_seconds(transcript_path):
    if os.path.getsize(transcript_path) > MAX_TRANSCRIPT_BYTES:
        return None
    last_ts = None
    with open(transcript_path) as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if is_user_prompt(entry) and entry.get("timestamp"):
                last_ts = entry["timestamp"]
    if not last_ts:
        return None
    ts = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - ts).total_seconds()


def main():
    data = json.load(sys.stdin)
    event = data.get("hook_event_name")
    if event == "Notification":
        notify(data.get("message") or "Claude needs your attention", sound="Glass")
        return
    if event == "Stop":
        if data.get("stop_hook_active"):
            return
        path = data.get("transcript_path") or ""
        if not os.path.isfile(path):
            return
        secs = turn_seconds(path)
        if secs is not None and MIN_SECONDS <= secs <= MAX_SECONDS:
            where = os.path.basename(data.get("cwd") or "") or "session"
            notify("Finished after %d min in %s" % (round(secs / 60), where))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
