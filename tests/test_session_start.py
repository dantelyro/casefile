"""session_start: the same context the bash hook gave, in exactly one field."""

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

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "plugins" / "devflow" / "hooks"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(HOOKS))

from devflow_hooks import session_start  # needs HOOKS on sys.path first


def expected(name: str) -> dict:
    return json.loads((FIXTURES / "outputs" / f"session_start_{name}.json").read_text(encoding="utf-8"))


def output(env: dict, cwd=None) -> dict:
    out = io.StringIO()
    with mock.patch.dict(os.environ, env, clear=True), redirect_stdout(out):
        event = {"hook_event_name": "SessionStart", "source": "startup"}
        if cwd is not None:
            event["cwd"] = str(cwd)
        session_start.main(event)
    return json.loads(out.getvalue())


def test_under_claude_code_nested_form(tmp_path):
    assert output({"CLAUDE_PLUGIN_ROOT": "/x"}, tmp_path) == expected("nested")


def test_elsewhere_top_level_form(tmp_path):
    assert output({}, tmp_path) == expected("top")


def test_copilot_gets_top_level_form(tmp_path):
    assert output({"CLAUDE_PLUGIN_ROOT": "/x", "COPILOT_CLI": "1"}, tmp_path) == expected("top")


@pytest.mark.parametrize("env", [
    {"EVAL_DEVFLOW_SKIP_SESSION_START": "1"},
    {"EVAL_DEVFLOW_SKIP_SESSION_START": "1", "CLAUDE_PLUGIN_ROOT": "/x"},
])
def test_EVID_006_eval_opt_out_emits_no_context(env, tmp_path):
    out = io.StringIO()
    with mock.patch.dict(os.environ, env, clear=True), redirect_stdout(out):
        session_start.main({"cwd": str(tmp_path)})
    assert out.getvalue() == ""


@pytest.mark.parametrize("value", [None, "0", "true", "", " 1"])
def test_EVID_006_only_explicit_one_opts_out(value, tmp_path):
    env = {} if value is None else {"EVAL_DEVFLOW_SKIP_SESSION_START": value}
    assert output(env, tmp_path) == expected("top")


@pytest.mark.parametrize("env", [{"CLAUDE_PLUGIN_ROOT": "/x"}, {}])
def test_exactly_one_context_field(env, tmp_path):
    out = output(env, tmp_path)
    fields = [k for k in ("additionalContext",) if k in out]
    fields += [k for k in ("additionalContext",) if k in out.get("hookSpecificOutput", {})]
    assert len(fields) == 1, out


def test_wrapper_runs_it():
    sh = shutil.which("sh")
    assert sh, "devflow requires sh (Git Bash on Windows)"
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=str(HOOKS.parent))
    env.pop("COPILOT_CLI", None)
    proc = subprocess.run(
        [sh, str(HOOKS / "run-hook"), "session_start"],
        input=(FIXTURES / "session_start_startup.json").read_text(encoding="utf-8"),
        capture_output=True, text=True, encoding="utf-8", env=env, timeout=60, check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout) == expected("nested")


CURRENT = "# Product decisions\n\n✅ decided by Ana Souza · ❌ rejected by Ana Souza\n\n- ✅ Keep jobs\n"


def write_decisions(root, text=CURRENT):
    path = root / "docs/product/product-decisions.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def context(root):
    return output({}, root)["additionalContext"]


def test_EVID_004_a_mental_model_is_named(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/mental-model.md").write_text("Private contents", encoding="utf-8")
    text = context(tmp_path)
    assert "docs/mental-model.md: the architecture document is now docs/architecture/overview.md" in text
    assert "Private contents" not in text
    assert text.index("Out of date") < text.index("</devflow>")


def test_EVID_004_product_decisions_without_the_legend_is_named(tmp_path):
    write_decisions(tmp_path, "# Product decisions\n\n- ✅ Keep jobs\n")
    assert "docs/product/product-decisions.md: no legend line" in context(tmp_path)


def test_EVID_004_a_decision_line_without_an_icon_is_named_with_its_line(tmp_path):
    write_decisions(tmp_path, CURRENT + "- Missing icon\n  continuation\n- Another missing icon\n")
    text = context(tmp_path)
    assert "lines 6, 8 have no ✅ or ❌" in text
    assert "no legend" not in text
    assert "Missing icon" not in text


def test_EVID_004_both_files_are_named_together(tmp_path):
    write_decisions(tmp_path, "# Product decisions\n\n- Missing icon\n")
    (tmp_path / "docs/mental-model.md").touch()
    text = context(tmp_path)
    assert "docs/mental-model.md:" in text
    assert "docs/product/product-decisions.md: no legend line; lines 3 have no ✅ or ❌" in text


def test_EVID_004_current_documents_inject_only_the_pointer(tmp_path):
    write_decisions(tmp_path)
    assert output({}, tmp_path) == expected("top")


def test_EVID_004_no_documents_inject_only_the_pointer(tmp_path):
    assert output({}, tmp_path) == expected("top")


def test_EVID_004_a_session_in_a_subfolder_reads_the_repository_root(tmp_path):
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    write_decisions(tmp_path, "# Product decisions\n")
    subfolder = tmp_path / "src"
    subfolder.mkdir()
    result = output({"PATH": os.environ["PATH"]}, subfolder)
    assert "docs/product/product-decisions.md: no legend line" in result["additionalContext"]


def test_EVID_004_an_unreadable_file_still_injects_the_pointer(tmp_path):
    (tmp_path / "docs/product/product-decisions.md").mkdir(parents=True)
    (tmp_path / "docs/mental-model.md").touch()
    assert output({}, tmp_path) == expected("top")


def test_EVID_004_invalid_encoding_still_injects_the_pointer(tmp_path):
    write_decisions(tmp_path).write_bytes(b"\xff")
    assert output({}, tmp_path) == expected("top")


def test_EVID_004_outdated_documents_still_emit_exactly_one_context_field(tmp_path):
    write_decisions(tmp_path, "# Product decisions\n")
    result = output({"CLAUDE_PLUGIN_ROOT": "/x"}, tmp_path)
    assert set(result) == {"hookSpecificOutput"}
    assert "no legend line" in result["hookSpecificOutput"]["additionalContext"]
