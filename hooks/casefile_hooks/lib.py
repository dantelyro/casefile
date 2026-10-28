"""Shared helpers for casefile's hooks.

A hook reads one JSON event from stdin and ends with a decision printed as JSON on stdout (exit 0):
deny or ask. Printing nothing allows. Exit codes are not used for decisions: `ask` has no
exit-code form, and one output style is one thing to test.
"""

import json
import os
import re
import subprocess
import sys

PREFIX = "casefile:"


def read_event() -> dict:
    """The event Claude Code sends on stdin. Raises ValueError on empty or malformed input
    and TypeError when it is not a JSON object, so the launcher can fail closed."""
    raw = sys.stdin.buffer.read().decode("utf-8").strip()
    if not raw:
        raise ValueError("empty hook input")
    event = json.loads(raw)
    if not isinstance(event, dict):
        raise TypeError("hook input is not a JSON object")
    return event


def _decide(decision: str, reason: str) -> None:
    sys.stdout.write(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": "casefile: " + reason,
    }}))
    sys.stdout.flush()
    sys.exit(0)


def deny(reason: str) -> None:
    _decide("deny", reason)


def ask(reason: str) -> None:
    _decide("ask", reason)


def allow() -> None:
    sys.exit(0)


def agent_of(event: dict) -> str | None:
    """Which agent is acting (`casefile:reviewer`, `Explore`, …). None means the developer's own
    session: the probe showed `agent_type` is absent there and set in every agent."""
    return event.get("agent_type") or None


def casefile_agent(event: dict) -> str | None:
    """The casefile agent's short name (`reviewer`), or None for anyone else."""
    agent = agent_of(event)
    if agent and agent.startswith(PREFIX):
        return agent[len(PREFIX):]
    return None


def git_root(cwd: str | None) -> str | None:
    """Root of the checkout or worktree that `cwd` belongs to."""
    if not cwd:
        return None
    try:
        out = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"],
                             check=False, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip() or None


def _linked_worktree_dir(directory: str) -> str | None:
    """The git dir of the linked worktree that `directory` is in (unique per worktree); None when it is the
    main checkout, outside any repository, or git cannot tell (fail closed)."""
    def ask(flag: str) -> str | None:
        try:
            out = subprocess.run(["git", "-C", directory, "rev-parse", "--path-format=absolute", flag],
                                 check=False, capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if out.returncode != 0 or not out.stdout.strip():
            return None
        return os.path.realpath(out.stdout.strip())

    git_dir, common_dir = ask("--git-dir"), ask("--git-common-dir")
    if git_dir is None or common_dir is None or git_dir == common_dir:
        return None
    return git_dir


def in_own_worktree(path: str, cwd: str | None = None) -> bool:
    """True when `path` (relative ones resolved against `cwd`) lies in the same linked git worktree as
    `cwd`. The file is asked through its nearest existing parent directory. Anything git cannot tell
    → False (fail closed)."""
    cwd = cwd or os.getcwd()
    directory = os.path.dirname(os.path.realpath(os.path.join(cwd, path)))
    while directory and not os.path.isdir(directory):
        parent = os.path.dirname(directory)
        if parent == directory:
            return False
        directory = parent
    file_tree = _linked_worktree_dir(directory)
    return file_tree is not None and file_tree == _linked_worktree_dir(cwd)


_WORKTREE_PREFIX = re.compile(r"^\.claude/worktrees/[^/]+/")


def repo_relative(event: dict, path: str | None) -> str | None:
    """`path` relative to the repository being worked in, with forward slashes; a path into an
    agent's worktree folder maps to the same repo path. None when outside the repository."""
    if not path:
        return None
    cwd = event.get("cwd") or os.getcwd()
    absolute = os.path.realpath(os.path.join(cwd, path))
    roots = [r for r in (git_root(cwd), os.environ.get("CLAUDE_PROJECT_DIR")) if r]
    for root in roots:
        try:
            rel = os.path.relpath(absolute, os.path.realpath(root))
        except ValueError:  # another drive on Windows
            continue
        rel = rel.replace("\\", "/")
        if not rel.startswith(".."):
            return _WORKTREE_PREFIX.sub("", rel)
    return None


class ConfigError(Exception):
    pass


CONFIG_PATH = ".claude/casefile.json"
OLD_CONFIG_PATH = ".claude/devflow.json"  # the plugin's name before 0.25.0 (D-060)

_DEFAULTS = {
    "default_branch": "main",
    "protected_paths": [],
    "apps": {},
    "allow_skip_markers_in": [],
    "rule_id_pattern": r"[A-Z]+-\d{3}",
    "specs_dir": "docs/specs",
    "plans_dir": "docs/plans",
    "build_order": "docs/product/blueprint.html",
    "repo": None,
    "siblings": {},
    "claim_docs": ["CLAUDE.md", "AGENTS.md", "docs/architecture/overview.md", "README.md"],
    "design": {
        "tokens": "docs/product/design-system/tokens.json",
        "ui_paths": [],
        "components_dir": None,
        "classes": None,
        "raw_values_allowed": [],
        "forbidden_imports": [],
    },
}

_TYPES = {
    "default_branch": str, "protected_paths": list, "apps": dict, "allow_skip_markers_in": list, "rule_id_pattern": str,
    "specs_dir": str, "plans_dir": str, "build_order": str, "repo": (str, type(None)), "siblings": dict,
    "claim_docs": list, "design": dict,
    "design.tokens": str, "design.ui_paths": list, "design.components_dir": (str, type(None)),
    "design.classes": (str, type(None)), "design.raw_values_allowed": list,
    "design.forbidden_imports": list,
}


def config(event: dict) -> dict:
    """The project's `.claude/casefile.json` over the defaults. Missing file → defaults.
    Raises ConfigError, naming the file or key, when it cannot be used."""
    cfg = json.loads(json.dumps(_DEFAULTS))
    root = git_root(event.get("cwd") or os.getcwd())
    if not root:
        return cfg
    path = os.path.join(root, *CONFIG_PATH.split("/"))
    if not os.path.isfile(path):
        # Defaults would quietly loosen every guard the old file configured, so refuse instead.
        if os.path.isfile(os.path.join(root, *OLD_CONFIG_PATH.split("/"))):
            raise ConfigError(f"{OLD_CONFIG_PATH} is from before devflow became casefile: rename it to {CONFIG_PATH}")
        return cfg
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise ConfigError(f"{CONFIG_PATH} cannot be read: {e}") from e
    if not isinstance(data, dict):
        raise ConfigError(f"{CONFIG_PATH} must hold a JSON object")
    for key, value in data.items():
        if key == "design" and isinstance(value, dict):
            for sub, subvalue in value.items():
                _check_type(f"design.{sub}", subvalue)
                cfg["design"][sub] = subvalue
        else:
            _check_type(key, value)
            cfg[key] = value
    return cfg


def _check_type(key: str, value) -> None:
    expected = _TYPES.get(key)
    if expected and not isinstance(value, expected):
        raise ConfigError(f"{CONFIG_PATH}: `{key}` has the wrong type ({type(value).__name__})")
