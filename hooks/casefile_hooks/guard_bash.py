"""PreToolUse on Bash and PowerShell: the command rules for every session alike, and the reviewer's own.

No agent but the reviewer has rules of its own (GUARD-009, D-074).

Commands are split into statements (on ; & | && || ( ) { } and newlines) after quoted text is
blanked out, so a commit message mentioning `git push` never counts. Each statement is judged by
its program and arguments. Claude Code's `if` filter is best-effort, so this hook registers
without one and checks every command itself.
"""

import os
import re

from casefile_hooks import lib

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


# --- the reviewer (GUARD-001 to 005) --------------------------------------------------

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
        return f"`git {sub}` changes the repository"
    if s.name in _FILE_CHANGERS:
        return f"`{s.name}` changes files"
    if s.name == "sed" and any(a.startswith("-i") for a in s.args):
        return "`sed -i` changes files"
    return None


_RESTORE_FLAGS = {"-p", "--patch", "-q", "--quiet"}
_PLAIN = r"[A-Za-z0-9._/@+-]+"
_QUOTED_PATH = r"\"[A-Za-z0-9._/@+ -]+\"|'[A-Za-z0-9._/@+ -]+'"
_WORD = rf"(?:{_QUOTED_PATH}|{_PLAIN})"
_RESTORE_COMMAND = re.compile(rf"git restore(?:[ \t]+{_WORD})+")


def _restores_paths(command: str) -> bool:
    """`git restore <path>…` that only discards edits in the working tree (GUARD-003). An allow-list
    over the raw command text: the whole command is `git restore` plus words made of plain
    characters (a quoted path may also hold spaces), so no chain, redirect, git option, glob, brace
    or other expansion can reach git as a flag. Flags are only those in `_RESTORE_FLAGS` and `--`;
    quoted words are paths; at least one path is required."""
    command = command.strip()
    if not _RESTORE_COMMAND.fullmatch(command):
        return False
    paths = 0
    options_ended = False
    for word in re.findall(_WORD, command[len("git restore"):]):
        if word[0] in "\"'":
            if word[1:2] == "-":
                return False
            paths += 1
        elif options_ended or not word.startswith("-"):
            paths += 1
        elif word == "--":
            options_ended = True
        elif word not in _RESTORE_FLAGS:
            return False
    return paths > 0


def _writes_by_redirect(command: str) -> bool:
    for m in _REDIRECT.finditer(_QUOTED.sub(" Q ", command)):
        target = m.group(2)
        if target.startswith("&") or target.lower() in _NULL_TARGETS:
            continue
        return True
    return False


def main(event: dict) -> None:
    command = (event.get("tool_input") or {}).get("command") or ""
    shown = command.strip()[:200]
    parsed = statements(command)

    for s in parsed:
        if _removes_compose_volumes(s):
            lib.deny("`docker compose down -v` deletes the compose volumes, the shared database "
                     f"included. Use plain `down`, or a throwaway container for a fresh database. (`{shown}`)")
        if _skips_git_hooks(s):
            lib.deny(f"skipping git hooks (`--no-verify`) is not allowed; fix what the hook reports. (`{shown}`)")

    if any(s.git()[0] == "push" for s in parsed):
        lib.ask(f"this pushes to a remote: `{shown}`. Push?")

    # Every other agent gets the main session's rules (GUARD-009); only the reviewer has its own.
    if lib.casefile_agent(event) != "reviewer":
        lib.allow()

    for s in parsed:
        why = _read_only_violation(s)
        if why and _restores_paths(command):
            if lib.git_root(event.get("cwd") or os.getcwd()) is None:
                lib.deny("the reviewer restores files only inside the repository it reviews, and this "
                         f"folder is not in one. (`{shown}`)")
            why = None
        if why:
            lib.deny(f"the reviewer only reads: {why}. (`{shown}`)")
    if _writes_by_redirect(command):
        lib.deny(f"the reviewer only reads: redirecting output into a file writes it. (`{shown}`)")

    lib.allow()
