"""PreToolUse on Bash and PowerShell: the command rules of the 0.13.0 guard table.

Commands are split into statements (on ; & | && || ( ) { } and newlines) after quoted text is
blanked out, so a commit message mentioning `git push` never counts. Each statement is judged by
its program and arguments. Claude Code's `if` filter is best-effort, so this hook registers
without one and checks every command itself.
"""

import re

from devflow_hooks import lib

_QUOTED = re.compile(r'"(?:\\.|[^"\\])*"|\'[^\']*\'')
_SPLIT = re.compile(r"\|\||&&|[;&|(){}\n]")
_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_PREFIXES = {"sudo", "exec", "command", "nohup", "time", "env", "&", "."}
# git's own options before the subcommand that take a separate value
_GIT_VALUE_OPTS = {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--config-env",
                   "--exec-path", "--super-prefix", "--attr-source"}


class Statement:
    def __init__(self, words: list[str], quoted: list[str]):
        self.name = re.sub(r"\.exe$", "", words[0].replace("\\", "/").rsplit("/", 1)[-1].lower())
        self.args = words[1:]
        self._quoted = quoted

    def value(self, word: str) -> str:
        """A word with its quoted text put back (rules never see it; a path after -C needs it)."""
        return re.sub(r"\x00(\d+)\x00", lambda m: self._quoted[int(m.group(1))], word)

    def git(self) -> tuple[str | None, list[str]]:
        """(subcommand, its arguments) when this is a git statement."""
        if self.name != "git":
            return None, []
        i = 0
        while i < len(self.args):
            a = self.args[i]
            if a in _GIT_VALUE_OPTS:
                i += 2
            elif a.startswith("-"):
                i += 1
            else:
                return a, self.args[i + 1:]
        return None, []


def statements(command: str) -> list[Statement]:
    quoted: list[str] = []

    def hide(m: re.Match) -> str:
        quoted.append(m.group(0)[1:-1])
        return f"\x00{len(quoted) - 1}\x00"

    blanked = _QUOTED.sub(hide, command)
    found = []
    for part in _SPLIT.split(blanked):
        words = part.split()
        while words and (_ASSIGN.match(words[0]) or words[0].lower() in _PREFIXES):
            words = words[1:]
        if words:
            found.append(Statement(words, quoted))
    return found


def _short_flags(args: list[str]) -> set[str]:
    """Letters given as short options (`-vt` → {'v', 't'})."""
    return {c for a in args if re.fullmatch(r"-[A-Za-z]+", a) for c in a[1:]}


# --- rules for everyone --------------------------------------------------------------------

def _removes_compose_volumes(s: Statement) -> bool:
    if s.name == "docker" and "compose" in s.args:
        args = s.args[s.args.index("compose") + 1:]
    elif s.name == "docker-compose":
        args = s.args
    else:
        return False
    if "down" not in args:
        return False
    after = args[args.index("down") + 1:]
    return "--volumes" in after or "v" in _short_flags(after)


def _skips_git_hooks(s: Statement) -> bool:
    sub, args = s.git()
    if sub is None:
        return False
    return "--no-verify" in args or (sub == "commit" and "n" in _short_flags(args))


# --- rules for agents ----------------------------------------------------------------------

def _kills_by_name(s: Statement) -> bool:
    lowered = [a.lower() for a in s.args]
    if s.name == "taskkill":
        return "/im" in lowered or "-im" in lowered
    if s.name in ("pkill", "killall"):
        return True
    if s.name == "stop-process":
        return not any(a in ("-id", "-inputobject") for a in lowered)
    return False


_SLEEP_LIMIT = 10  # seconds; an implementer once waited ~30 min in sleep/until loops on a hung check
_DURATION = re.compile(r"^(\d+(?:\.\d+)?)([smhd]?)$")


_CHAIN = re.compile(r"&&|\|\||;|\n|\|\s*tail\b")


def _chained(command: str) -> bool:
    """More than one command in one call, or output cut by `tail` (D-043). Quoted text never counts."""
    return bool(_CHAIN.search(_QUOTED.sub("", command.strip())))


def _waits_in_a_loop(s: Statement) -> bool:
    """A devflow agent polling a command instead of running it with a timeout (D-043)."""
    words = [s.name] + [a.lower() for a in s.args]
    if words[0] == "do":  # `while …; do sleep 100; done` splits into `do sleep 100`
        words = words[1:]
    if not words:
        return False
    if words[0] in ("until", "while"):
        return True
    if words[0] in ("sleep", "start-sleep"):
        for w in words[1:]:
            m = _DURATION.match(w)
            if m:
                seconds = float(m.group(1)) * {"": 1, "s": 1, "m": 60, "h": 3600, "d": 86400}[m.group(2)]
                return seconds >= _SLEEP_LIMIT
    return False


# --- read-only agents (reviewer, planner) --------------------------------------------------

_READ_GIT = {"log", "diff", "show", "status", "rev-parse", "ls-files", "blame", "grep", "describe",
             "merge-base", "cat-file", "shortlog", "show-ref", "for-each-ref", "rev-list"}
_FILE_CHANGERS = {"rm", "rmdir", "del", "erase", "mv", "cp", "touch", "mkdir", "tee", "truncate",
                  "remove-item", "move-item", "rename-item", "copy-item", "set-content",
                  "add-content", "out-file", "new-item", "clear-content"}
_REDIRECT = re.compile(r"(\d?)>>?\s*(&\d|[^\s;&|]*)")
_NULL_TARGETS = {"/dev/null", "$null", "nul"}


def _read_only_violation(s: Statement) -> str | None:
    sub, args = s.git()
    if s.name == "git":
        if sub in _READ_GIT:
            return None
        if sub == "branch" and not ({"d", "D", "m", "M", "c", "C"} & _short_flags(args)) \
                and not any(not a.startswith("-") for a in args):
            return None
        if sub == "switch" and "--detach" in args:
            return None
        return f"`git {sub}` changes the repository"
    if s.name in _FILE_CHANGERS:
        return f"`{s.name}` changes files"
    if s.name == "sed" and any(a.startswith("-i") for a in s.args):
        return "`sed -i` changes files"
    return None


_RESTORE_FLAGS = {"-W", "--worktree", "-p", "--patch", "-q", "--quiet"}
_SHELL_EXPANSION = re.compile(r"[\\$`]")


def _restores_worktree_paths(s: Statement, command: str) -> bool:
    """`git restore <path>…` that only discards edits in the working tree (GUARD-003), as an
    allow-list: no git option before `restore` (`-C` reaches other worktrees), only the flags in
    `_RESTORE_FLAGS` and `--`, at least one path, and nothing the shell would rewrite into another
    flag (backslash, `$`, backtick, parentheses), since git also takes options after paths."""
    if s.name != "git" or not s.args or s.args[0] != "restore":
        return False
    if "(" in command or ")" in command:
        return False
    paths = 0
    options_ended = False
    for word in s.args[1:]:
        a = s.value(word)  # the word git receives, quotes removed
        if _SHELL_EXPANSION.search(a) or _SHELL_EXPANSION.search(word):
            return False
        if options_ended or not a.startswith("-"):
            paths += 1
        elif a == "--":
            options_ended = True
        elif a not in _RESTORE_FLAGS:
            return False
    return paths > 0


def _writes_by_redirect(command: str) -> bool:
    for m in _REDIRECT.finditer(_QUOTED.sub(" Q ", command)):
        target = m.group(2)
        if target.startswith("&") or target.lower() in _NULL_TARGETS:
            continue
        return True
    return False


# --- implementer ---------------------------------------------------------------------------

def _implementer_violation(s: Statement, default_branch: str) -> str | None:
    sub, args = s.git()
    if sub in ("merge", "rebase", "cherry-pick"):
        return f"implementers may not `git {sub}`; the main session merges after the developer's yes"
    if sub == "reset" and "--hard" in args:
        return "implementers may not hard-reset"
    if sub in ("switch", "checkout") and default_branch in args:
        return f"implementers stay on their own branch, never `{default_branch}`"
    if sub == "branch" and "D" in _short_flags(args):
        return "implementers may not force-delete branches"
    return None


def main(event: dict) -> None:
    command = (event.get("tool_input") or {}).get("command") or ""
    agent = lib.agent_of(event)
    role = lib.devflow_agent(event)
    shown = command.strip()[:200]
    parsed = statements(command)

    for s in parsed:
        if _removes_compose_volumes(s):
            lib.deny("`docker compose down -v` deletes the compose volumes, the shared database "
                     f"included. Use plain `down`, or a throwaway container for a fresh database. (`{shown}`)")
        if _skips_git_hooks(s):
            lib.deny(f"skipping git hooks (`--no-verify`) is not allowed; fix what the hook reports. (`{shown}`)")

    if any(s.git()[0] == "push" for s in parsed):
        if agent:
            lib.deny("agents may not `git push`. Commit locally and report back; the developer "
                     f"reviews and pushes. (`{shown}`)")
        lib.ask(f"this pushes to a remote: `{shown}`. Push?")

    if not agent:
        lib.allow()

    for s in parsed:
        if _kills_by_name(s):
            lib.deny("agents may not kill processes by name: it kills the developer's processes too. "
                     f"Stop the one process you started, by its id. (`{shown}`)")

    if role:
        if _chained(command):
            lib.deny("devflow agents run one command per call: no `;`, `&&`, `||`, several lines or "
                     f"`| tail`. Split it, and give each check its own timeout. (`{shown}`)")
        for s in parsed:
            if _waits_in_a_loop(s):
                lib.deny(f"devflow agents run each check once, with a timeout, and never wait on one in a "
                         f"`sleep`/`until` loop. If it timed out, report it with its last output. (`{shown}`)")

    if role in ("reviewer", "planner"):
        for s in parsed:
            why = _read_only_violation(s)
            if why and role == "reviewer" and _restores_worktree_paths(s, command):
                why = None
            if why:
                lib.deny(f"the {role} only reads: {why}. (`{shown}`)")
        if _writes_by_redirect(command):
            lib.deny(f"the {role} only reads: redirecting output into a file writes it. (`{shown}`)")

    if role == "implementer":
        default_branch = lib.config(event)["default_branch"]
        for s in parsed:
            why = _implementer_violation(s, default_branch)
            if why:
                lib.deny(f"{why}. (`{shown}`)")

    lib.allow()
