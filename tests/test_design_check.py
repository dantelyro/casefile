"""design_check: UI code may use only what the project's design system defines."""

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "hooks"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(HOOKS))

import run  # noqa: E402

CONFIG = {"design": {
    "ui_paths": ["web/"],
    "components_dir": "web/components/ui/",
    "classes": "tailwind",
    "raw_values_allowed": ["web/styles/tokens.css", "web/features/cv/template/"],
    "forbidden_imports": ["react-icons", "@heroicons/*", "@fortawesome/*"],
}}


class Base(unittest.TestCase):
    config = CONFIG
    with_design_system = True

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        if self.with_design_system:
            shutil.copytree(FIXTURES / "design", self.repo / "docs" / "product" / "design-system")
        if self.config is not None:
            (self.repo / ".claude").mkdir()
            (self.repo / ".claude" / "devflow.json").write_text(json.dumps(self.config), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def decide(self, tool_input, agent="devflow:implementer", tool="Write"):
        e = json.loads((FIXTURES / "write_main.json").read_text(encoding="utf-8"))
        e.update({"cwd": str(self.repo), "tool_name": tool, "tool_input": tool_input})
        e.pop("agent_type", None)
        if agent:
            e["agent_type"] = agent
        code, out = run.dispatch("design_check", json.dumps(e))
        self.assertEqual(code, 0)
        if not out:
            return "allow", ""
        hso = json.loads(out)["hookSpecificOutput"]
        return hso["permissionDecision"], hso["permissionDecisionReason"]

    def write(self, path, content, expected="allow", agent="devflow:implementer"):
        got, reason = self.decide({"file_path": str(self.repo / path), "content": content}, agent=agent)
        self.assertEqual(got, expected, f"{path}: {content!r}\n{reason}")
        return reason


class Tokens(Base):
    def test_token_classes_pass(self):
        self.write("web/features/jobs/JobList.tsx",
                   '<li className="bg-surface-raised text-ink border border-line rounded-md p-6 gap-4 '
                   'text-heading font-mono shadow-raised hover:bg-brand-strong text-on-brand/80 ring-2 ring-focus">'
                   'Jobs up-to-date</li>')

    def test_raw_colours_are_blocked(self):
        self.write("web/app/page.tsx", 'const c = "#0b6e52"', "deny")
        self.write("web/app/page.tsx", "style={{ color: 'rgb(11, 110, 82)' }}", "deny")
        self.write("web/app/page.tsx", "style={{ color: 'oklch(0.5 0.1 150)' }}", "deny")
        self.write("web/styles/app.css", ".x { background: white; color: #fff; }", "deny")

    def test_raw_lengths_and_fonts_are_blocked(self):
        self.write("web/app/page.tsx", "style={{ padding: '13px' }}", "deny")
        self.write("web/styles/app.css", ".x { font-family: Arial; }", "deny")
        self.write("web/styles/app.css", ".x { border-width: 1px; }")  # hairline allowed

    def test_tailwind_defaults_and_arbitrary_values_are_blocked(self):
        for cls in ("bg-blue-500", "text-gray-600", "p-5", "gap-7", "rounded-xl", "rounded", "shadow-lg",
                    "text-xl", "font-bold", "font-serif", "bg-[#fff]", "p-[13px]", "[mask:url(x)]", "bg-primary",
                    "text-muted-foreground"):
            self.write("web/components/primitives/Box.tsx", f'<div className="{cls}" />', "deny")

    def test_the_reason_names_the_fix(self):
        reason = self.write("web/app/page.tsx", '<div className="bg-blue-500" />', "deny")
        self.assertIn("brand", reason)
        self.assertIn("design system", reason)


class Edits(Base):
    def test_edit_checks_the_replacement_text(self):
        path = str(self.repo / "web/app/page.tsx")
        got, _ = self.decide({"file_path": path, "old_string": "x", "new_string": 'className="bg-red-500"'}, tool="Edit")
        self.assertEqual(got, "deny")
        got, _ = self.decide({"file_path": path, "old_string": "x", "new_string": 'className="bg-score-low"'}, tool="Edit")
        self.assertEqual(got, "allow")

    def test_multiple_edits(self):
        path = str(self.repo / "web/app/page.tsx")
        got, _ = self.decide({"file_path": path, "edits": [{"old_string": "a", "new_string": "bg-ink"},
                                                           {"old_string": "b", "new_string": '"p-[3px]"'}]},
                             tool="MultiEdit")
        self.assertEqual(got, "deny")


class Imports(Base):
    def test_forbidden_imports(self):
        self.write("web/app/page.tsx", "import { FaUser } from 'react-icons/fa'", "deny")
        self.write("web/app/page.tsx", 'import { X } from "@heroicons/react/24/solid"', "deny")
        self.write("web/app/page.tsx", "const i = require('@fortawesome/free-solid-svg-icons')", "deny")
        self.write("web/app/page.tsx", "import { Search } from 'lucide-react'")
        self.write("web/app/page.tsx", "import x from 'react-iconsx'")


class Components(Base):
    def test_only_design_system_components_live_in_the_components_folder(self):
        self.write("web/components/ui/JobCard.tsx", "export function JobCard() {}")
        self.write("web/components/ui/match-score.tsx", "export function MatchScore() {}")
        self.write("web/components/ui/index.ts", "export * from './JobCard'")
        self.write("web/components/ui/FancyCard.tsx", "export function FancyCard() {}", "deny")
        self.write("web/components/ui/Cover.tsx", "export function Cover() {}", "deny")
        self.write("web/components/primitives/Dialog.tsx", "export function Dialog() {}")


class Exceptions(Base):
    def test_raw_value_files_tests_and_other_folders(self):
        self.write("web/styles/tokens.css", ":root { --brand: #0b6e52; --space-4: 16px; }")
        self.write("web/features/cv/template/style.ts", "export const c = '#1F5C8B'")
        self.write("web/features/matching/score.test.ts", "expect(color).toBe('#0b6e52')")
        self.write("worker/app/x.py", "COLOR = '#ffffff'")
        self.write("docs/product/design-system/components/bundle.css", ".x { color: #fff; }", agent=None)

    def test_raw_value_files_still_follow_class_rules(self):
        self.write("web/styles/tokens.css", '@apply bg-blue-500;', "deny")

    def test_main_session_is_checked_too(self):
        self.write("web/app/page.tsx", '<div className="bg-blue-500" />', "deny", agent=None)

    def test_other_agents_too(self):
        self.write("web/app/page.tsx", '<div className="bg-blue-500" />', "deny", agent="general-purpose")


class WithoutTailwind(Base):
    config = {"design": dict(CONFIG["design"], classes=None)}

    def test_class_rules_are_off_raw_values_stay(self):
        self.write("web/app/page.tsx", '<div className="bg-blue-500 p-5 rounded-xl" />')
        self.write("web/app/page.tsx", 'const c = "#0b6e52"', "deny")


class NoDesignSystem(Base):
    with_design_system = False

    def test_nothing_is_checked(self):
        self.write("web/app/page.tsx", '<div className="bg-blue-500" style={{color: "#fff"}} />')


class NoConfig(Base):
    config = None

    def test_no_ui_paths_means_nothing_is_checked(self):
        self.write("web/app/page.tsx", '<div className="bg-blue-500" />')

    def test_a_broken_tokens_file_does_not_block_a_project_that_has_not_turned_it_on(self):
        (self.repo / "docs/product/design-system/tokens.json").write_text("{ nope", encoding="utf-8")
        self.write("web/app/page.tsx", "x")


class TokensPathFromConfig(Base):
    with_design_system = False
    config = {"design": dict(CONFIG["design"], tokens="docs/design/tokens.json")}

    def test_reads_the_configured_path(self):
        shutil.copytree(FIXTURES / "design", self.repo / "docs" / "design")
        self.write("web/app/page.tsx", '<div className="bg-blue-500" />', "deny")
        self.write("web/app/page.tsx", '<div className="bg-brand" />')


class BrokenTokens(Base):
    def test_unreadable_tokens_refuse_with_the_file_named(self):
        (self.repo / "docs/product/design-system/tokens.json").write_text("{ nope", encoding="utf-8")
        got, reason = self.decide({"file_path": str(self.repo / "web/a.tsx"), "content": "x"})
        self.assertEqual(got, "deny")
        self.assertIn("tokens.json", reason)


if __name__ == "__main__":
    unittest.main()
