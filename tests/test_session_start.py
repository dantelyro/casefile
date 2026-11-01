"""session_start: the project context for every session and agent, and the evidence pointer for the
main session, in exactly one field."""

import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
from contextlib import redirect_stdout
from unittest import mock

import pytest

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "hooks"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(HOOKS))

from casefile_hooks import session_start  # needs HOOKS on sys.path first


def output(env: dict, event: dict | None = None) -> dict:
    out = io.StringIO()
    with mock.patch.dict(os.environ, env, clear=True), redirect_stdout(out):
        session_start.main(event or {"hook_event_name": "SessionStart", "source": "startup"})
    return json.loads(out.getvalue())


def agent_context(agent_type: str) -> dict:
    return output({"CLAUDE_PLUGIN_ROOT": "/x"},
                  {"hook_event_name": "SubagentStart", "agent_id": "a1", "agent_type": agent_type})["hookSpecificOutput"]


@pytest.mark.parametrize("agent_type", ["Explore", "general-purpose", "casefile:reviewer", "other-plugin:helper"])
def test_CTX_001_every_agent_starts_with_the_project_context(agent_type):
    out = agent_context(agent_type)
    assert out["hookEventName"] == "SubagentStart", out
    assert "docs/decisions/README.md" in out["additionalContext"], out
    assert "in full" in out["additionalContext"], out


@pytest.mark.parametrize("agent_type", ["Explore", "casefile:implementer"])
def test_CTX_001_an_agent_never_gets_the_main_sessions_behaviour(agent_type):
    text = agent_context(agent_type)["additionalContext"]
    assert "casefile:evidence" not in text, text
    assert "watermark" not in text, text


def test_CTX_002_the_main_session_gets_the_project_context_then_the_evidence_pointer():
    text = output({"CLAUDE_PLUGIN_ROOT": "/x"})["hookSpecificOutput"]["additionalContext"]
    agent = agent_context("Explore")["additionalContext"]
    assert text.startswith(agent), text
    assert "casefile:evidence" in text[len(agent):], text


@pytest.mark.parametrize("env", [{"CLAUDE_PLUGIN_ROOT": "/x"}, {}])
def test_exactly_one_context_field(env):
    out = output(env)
    assert "additionalContext" not in out, out
    assert "additionalContext" in out["hookSpecificOutput"], out


def test_wrapper_runs_it():
    sh = shutil.which("sh")
    assert sh, "casefile requires sh (Git Bash on Windows)"
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=str(HOOKS.parent))
    proc = subprocess.run(
        [sh, str(HOOKS / "run-hook"), "session_start"],
        input=(FIXTURES / "session_start_startup.json").read_text(encoding="utf-8"),
        capture_output=True, text=True, encoding="utf-8", env=env, timeout=60, check=False,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)["hookSpecificOutput"]
    assert out["hookEventName"] == "SessionStart", out
    assert "casefile:evidence" in out["additionalContext"], out
