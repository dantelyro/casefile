: << 'CMDBLOCK'
@echo off
REM Polyglot launcher for devflow's hooks: run-hook.cmd <hook-name>, event JSON on stdin.
REM cmd.exe runs this half; bash and sh read it as a heredoc and skip it (D-005).
REM Do not reorder this file or add anything above the first line.
REM
REM Finds Python 3.10 or newer and runs run.py with it. With none found, a guard blocks
REM (exit 2, reason on stderr) and session_start asks Claude to tell the developer.
setlocal
set "HOOK_DIR=%~dp0"
set "CHECK=import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
where py >nul 2>nul && py -3 -c "%CHECK%" >nul 2>nul && goto :py
where python >nul 2>nul && python -c "%CHECK%" >nul 2>nul && goto :python
if "%~1"=="session_start" (
    echo {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "devflow needs Python 3.10 or newer, and none was found. At the start of your first response, tell the developer, give them the install command: winget install Python.Python.3.14 -- and wait for their yes before running it. Until Python is installed, every devflow guard refuses commands and file edits."}}
    exit /b 0
)
echo devflow: this hook needs Python 3.10 or newer, and none was found, so the call is refused. Ask the developer to install it: winget install Python.Python.3.14 1>&2
exit /b 2
:py
py -3 "%HOOK_DIR%run.py" %*
exit /b %ERRORLEVEL%
:python
python "%HOOK_DIR%run.py" %*
exit /b %ERRORLEVEL%
CMDBLOCK

# bash / sh half. Only shell builtins are used before Python is found, so this works with an
# empty PATH. python3 on Windows can be the Microsoft Store stub, so py is tried first and every
# candidate must pass the version check.
case "$0" in
  */*) DIR="${0%/*}" ;;
  *\\*) DIR="${0%\\*}" ;;
  *) DIR=. ;;
esac
NAME="${1:-}"
CHECK='import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'
for PY in "py -3" python3 python; do
  set -- $PY
  if command -v "$1" >/dev/null 2>&1 && $PY -c "$CHECK" >/dev/null 2>&1; then
    exec $PY "$DIR/run.py" "$NAME"
  fi
done

INSTALL='Windows: winget install Python.Python.3.14 -- macOS: brew install python@3.14 -- Linux: the distribution package manager, for example sudo apt install python3'
if [ "$NAME" = "session_start" ]; then
  printf '{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "devflow needs Python 3.10 or newer, and none was found. At the start of your first response, tell the developer, give them the install command for their platform (%s), and wait for their yes before running it. Until Python is installed, every devflow guard refuses commands and file edits."}}\n' "$INSTALL"
  exit 0
fi
printf 'devflow: this hook needs Python 3.10 or newer, and none was found, so the call is refused. Ask the developer to install it (%s).\n' "$INSTALL" >&2
exit 2
