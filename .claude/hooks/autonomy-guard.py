#!/usr/bin/env python3
"""PreToolUse guard for scheduled runs of the morning routine.

Reads the hook JSON on stdin. Exit 0 = no decision (the normal permission
rules apply). Exit 2 = block; the text on stderr is shown to Claude.

It blocks a Bash command when:
  - the command contains a NEVER word (money movement, deletion), at any level;
  - the command contains an ACT word (send, push, ...) and AUTONOMY.md is not
    at Level 3 (PAUSED, a missing file or an unreadable Level line all block).

The match is on whole words in the command text, so it fails closed: a search
query that contains the word "send" is blocked too. Edit the two lists to fit
the subcommands of your own tools.
"""
import json
import os
import re
import sys

ACT = r"send|send-draft|reply|forward|push|apply|publish"
NEVER = r"refund|charge|payout|pay|delete|cancel"


def word(pattern, text):
    return re.search(r"(?<![\w-])(" + pattern + r")(?![\w-])", text, re.IGNORECASE)


def level(project_dir):
    """Return 0-3, or None for PAUSED.

    AUTONOMY.md has exactly one line `Level: <value>`, value 0, 1, 2, 3 or
    PAUSED. A missing file, a missing line, more than one line or any other
    value counts as PAUSED.
    """
    try:
        with open(os.path.join(project_dir, "AUTONOMY.md"), encoding="utf-8") as fh:
            values = [m.group(1) for m in (re.match(r"Level:\s*(.*?)\s*$", line) for line in fh) if m]
    except (OSError, UnicodeDecodeError):
        return None
    if len(values) == 1 and values[0] in ("0", "1", "2", "3"):
        return int(values[0])
    return None


def block(reason):
    print("autonomy-guard: " + reason, file=sys.stderr)
    sys.exit(2)


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        block("could not read the hook input, so the call is blocked")
    if data.get("tool_name") != "Bash":
        sys.exit(0)
    command = str((data.get("tool_input") or {}).get("command", ""))
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or "."

    hit = word(NEVER, command)
    if hit:
        block("'%s' is never autonomous. Put it under 'Needs you'." % hit.group(1))
    hit = word(ACT, command)
    if hit:
        lvl = level(project_dir)
        if lvl != 3:
            state = "PAUSED (or missing or unreadable)" if lvl is None else "Level %d" % lvl
            block("'%s' needs Level 3 and AUTONOMY.md is %s. Put it under 'Needs you'." % (hit.group(1), state))
    sys.exit(0)


if __name__ == "__main__":
    main()
