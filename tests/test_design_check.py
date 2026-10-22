"""design_check: UI code may use only what the project's design system defines."""

import json
import pathlib
import shutil
import subprocess
import sys

import pytest

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "plugins" / "devflow" / "hooks"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(HOOKS))

import run

CONFIG = {"design": {
    "ui_paths": ["web/"],
    "components_dir": "web/components/ui/",
    "classes": "tailwind",
    "raw_values_allowed": ["web/styles/tokens.css", "web/features/cv/template/"],
    "forbidden_imports": ["react-icons", "@heroicons/*", "@fortawesome/*"],
}}


class Project:
    """A throwaway git repository with a design system and a config, as the case needs."""

    def __init__(self, path, config, with_design_system=True):
        self.repo = path
        subprocess.run(["git", "init", "-q"], cwd=path, check=True)
        if with_design_system:
            shutil.copytree(FIXTURES / "design", path / "docs" / "product" / "design-system")
        if config is not None:
            (path / ".claude").mkdir()
            (path / ".claude" / "devflow.json").write_text(json.dumps(config), encoding="utf-8")

    def decide(self, tool_input, agent="devflow:implementer", tool="Write"):
        e = json.loads((FIXTURES / "write_main.json").read_text(encoding="utf-8"))
        e.update({"cwd": str(self.repo), "tool_name": tool, "tool_input": tool_input})
        e.pop("agent_type", None)
        if agent:
            e["agent_type"] = agent
        code, out = run.dispatch("design_check", json.dumps(e))
        assert code == 0
        if not out:
            return "allow", ""
        hso = json.loads(out)["hookSpecificOutput"]
        return hso["permissionDecision"], hso["permissionDecisionReason"]

    def write(self, path, content, expected="allow", agent="devflow:implementer"):
        got, reason = self.decide({"file_path": str(self.repo / path), "content": content}, agent=agent)
        assert got == expected, f"{path}: {content!r}\n{reason}"
        return reason


@pytest.fixture
def project(tmp_path):
    return Project(tmp_path, CONFIG)


@pytest.fixture
def project_without_tailwind(tmp_path):
    return Project(tmp_path, {"design": dict(CONFIG["design"], classes=None)})


@pytest.fixture
def project_without_design_system(tmp_path):
    return Project(tmp_path, CONFIG, with_design_system=False)


@pytest.fixture
def project_without_config(tmp_path):
    return Project(tmp_path, None)


@pytest.fixture
def project_with_tokens_path_in_config(tmp_path):
    return Project(tmp_path, {"design": dict(CONFIG["design"], tokens="docs/design/tokens.json")},
                   with_design_system=False)


# tokens

def test_tokens_token_classes_pass(project):
    project.write("web/features/jobs/JobList.tsx",
                  '<li className="bg-surface-raised text-ink border border-line rounded-md p-6 gap-4 '
                  'text-heading font-mono shadow-raised hover:bg-brand-strong text-on-brand/80 ring-2 ring-focus">'
                  'Jobs up-to-date</li>')


def test_tokens_raw_colours_are_blocked(project):
    project.write("web/app/page.tsx", 'const c = "#0b6e52"', "deny")
    project.write("web/app/page.tsx", "style={{ color: 'rgb(11, 110, 82)' }}", "deny")
    project.write("web/app/page.tsx", "style={{ color: 'oklch(0.5 0.1 150)' }}", "deny")
    project.write("web/styles/app.css", ".x { background: white; color: #fff; }", "deny")


def test_tokens_raw_lengths_and_fonts_are_blocked(project):
    project.write("web/app/page.tsx", "style={{ padding: '13px' }}", "deny")
    project.write("web/styles/app.css", ".x { font-family: Arial; }", "deny")
    project.write("web/styles/app.css", ".x { border-width: 1px; }")  # hairline allowed


@pytest.mark.parametrize("cls", [
    "bg-blue-500", "text-gray-600", "p-5", "gap-7", "rounded-xl", "rounded", "shadow-lg", "text-xl",
    "font-bold", "font-serif", "bg-[#fff]", "p-[13px]", "[mask:url(x)]", "bg-primary", "text-muted-foreground"])
def test_tokens_tailwind_defaults_and_arbitrary_values_are_blocked(project, cls):
    project.write("web/components/primitives/Box.tsx", f'<div className="{cls}" />', "deny")


def test_tokens_the_reason_names_the_fix(project):
    reason = project.write("web/app/page.tsx", '<div className="bg-blue-500" />', "deny")
    assert "brand" in reason
    assert "design system" in reason


# edits

def test_edits_edit_checks_the_replacement_text(project):
    path = str(project.repo / "web/app/page.tsx")
    got, _ = project.decide({"file_path": path, "old_string": "x", "new_string": 'className="bg-red-500"'},
                            tool="Edit")
    assert got == "deny"
    got, _ = project.decide({"file_path": path, "old_string": "x", "new_string": 'className="bg-score-low"'},
                            tool="Edit")
    assert got == "allow"


def test_edits_multiple_edits(project):
    path = str(project.repo / "web/app/page.tsx")
    got, _ = project.decide({"file_path": path, "edits": [{"old_string": "a", "new_string": "bg-ink"},
                                                          {"old_string": "b", "new_string": '"p-[3px]"'}]},
                            tool="MultiEdit")
    assert got == "deny"


# imports

def test_imports_forbidden_imports(project):
    project.write("web/app/page.tsx", "import { FaUser } from 'react-icons/fa'", "deny")
    project.write("web/app/page.tsx", 'import { X } from "@heroicons/react/24/solid"', "deny")
    project.write("web/app/page.tsx", "const i = require('@fortawesome/free-solid-svg-icons')", "deny")
    project.write("web/app/page.tsx", "import { Search } from 'lucide-react'")
    project.write("web/app/page.tsx", "import x from 'react-iconsx'")


# components

def test_components_only_design_system_components_live_in_the_components_folder(project):
    project.write("web/components/ui/JobCard.tsx", "export function JobCard() {}")
    project.write("web/components/ui/match-score.tsx", "export function MatchScore() {}")
    project.write("web/components/ui/index.ts", "export * from './JobCard'")
    project.write("web/components/ui/FancyCard.tsx", "export function FancyCard() {}", "deny")
    project.write("web/components/ui/Cover.tsx", "export function Cover() {}", "deny")
    project.write("web/components/primitives/Dialog.tsx", "export function Dialog() {}")


# exceptions

def test_exceptions_raw_value_files_tests_and_other_folders(project):
    project.write("web/styles/tokens.css", ":root { --brand: #0b6e52; --space-4: 16px; }")
    project.write("web/features/cv/template/style.ts", "export const c = '#1F5C8B'")
    project.write("web/features/matching/score.test.ts", "expect(color).toBe('#0b6e52')")
    project.write("worker/app/x.py", "COLOR = '#ffffff'")
    project.write("docs/product/design-system/components/bundle.css", ".x { color: #fff; }", agent=None)


def test_exceptions_raw_value_files_still_follow_class_rules(project):
    project.write("web/styles/tokens.css", "@apply bg-blue-500;", "deny")


def test_exceptions_main_session_is_checked_too(project):
    project.write("web/app/page.tsx", '<div className="bg-blue-500" />', "deny", agent=None)


def test_exceptions_other_agents_too(project):
    project.write("web/app/page.tsx", '<div className="bg-blue-500" />', "deny", agent="general-purpose")


# without tailwind

def test_without_tailwind_class_rules_are_off_raw_values_stay(project_without_tailwind):
    project_without_tailwind.write("web/app/page.tsx", '<div className="bg-blue-500 p-5 rounded-xl" />')
    project_without_tailwind.write("web/app/page.tsx", 'const c = "#0b6e52"', "deny")


# no design system

def test_no_design_system_nothing_is_checked(project_without_design_system):
    project_without_design_system.write(
        "web/app/page.tsx", '<div className="bg-blue-500" style={{color: "#fff"}} />')


# no config

def test_no_config_no_ui_paths_means_nothing_is_checked(project_without_config):
    project_without_config.write("web/app/page.tsx", '<div className="bg-blue-500" />')


def test_no_config_a_broken_tokens_file_does_not_block_a_project_that_has_not_turned_it_on(
        project_without_config):
    (project_without_config.repo / "docs/product/design-system/tokens.json").write_text(
        "{ nope", encoding="utf-8")
    project_without_config.write("web/app/page.tsx", "x")


# tokens path from config

def test_tokens_path_from_config_reads_the_configured_path(project_with_tokens_path_in_config):
    p = project_with_tokens_path_in_config
    shutil.copytree(FIXTURES / "design", p.repo / "docs" / "design")
    p.write("web/app/page.tsx", '<div className="bg-blue-500" />', "deny")
    p.write("web/app/page.tsx", '<div className="bg-brand" />')


# broken tokens

def test_broken_tokens_unreadable_tokens_refuse_with_the_file_named(project):
    (project.repo / "docs/product/design-system/tokens.json").write_text("{ nope", encoding="utf-8")
    got, reason = project.decide({"file_path": str(project.repo / "web/a.tsx"), "content": "x"})
    assert got == "deny"
    assert "tokens.json" in reason
