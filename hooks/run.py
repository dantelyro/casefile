"""Entry point for every casefile hook: `run.py <hook-name>`, event JSON on stdin.

Guards fail closed: if the hook cannot be found, the event cannot be read, or the hook crashes,
the call is denied with the reason. session_start only adds context, so it never blocks.
"""

import importlib
import io
import json
import os
import re
import sys
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

NEVER_BLOCKS = {"session_start"}
_NAME = re.compile(r"^[a-z_]+$")


def _deny(reason: str) -> str:
    return json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "casefile: " + reason,
    }})


def dispatch(name: str, raw: str, importer=importlib.import_module) -> tuple[int, str]:
    """Run hook `name` on the raw event text. Returns (exit code, stdout)."""
    out = io.StringIO()
    try:
        if not _NAME.match(name):
            raise ValueError(f"not a hook name: {name!r}")
        module = importer(f"casefile_hooks.{name}")
        event = json.loads(raw) if raw.strip() else {} if name in NEVER_BLOCKS else None
        if not isinstance(event, dict):
            raise TypeError("hook input is not a JSON object")
        with redirect_stdout(out):
            try:
                module.main(event)
            except SystemExit as e:
                return (e.code or 0), out.getvalue()
        return 0, out.getvalue()
    except Exception as e:  # noqa: BLE001 — any failure must not let the call through
        if name in NEVER_BLOCKS:
            return 0, ""
        return 0, _deny(f"hook `{name}` failed, so the call is refused: {type(e).__name__}: {e}. "
                        "Tell the developer; this is a casefile bug, not something to work around.")


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    code, out = dispatch(name, raw)
    sys.stdout.write(out)
    sys.stdout.flush()
    sys.exit(code)


if __name__ == "__main__":
    main()
