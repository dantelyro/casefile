"""PreToolUse on Edit, Write, MultiEdit and NotebookEdit: UI code uses only the design system.

The vocabulary — colours, spacing,
radii, shadows, type styles, font families, components — is read from the project's `tokens.json`
(the claude.ai Design System format) and its `components/` folder, so adding a token to the design
system is the only way to make a new value usable in code. Applies to every session.

Off until the project has the tokens file and `design.ui_paths` in `.claude/devflow.json`.
pre_commit uses `Checker` on the added lines of a commit.
"""

import fnmatch
import json
import os
import re

from devflow_hooks import lib

UI_EXTENSIONS = (".tsx", ".ts", ".jsx", ".js", ".css", ".scss", ".mdx")
TEST_PATH = re.compile(r"(^|/)(tests?|e2e|__tests__)/|\.(test|spec)\.[jt]sx?$")
NOT_COMPONENTS = {"Cover"}  # the design-system artifact's cover card, never a code component

# --- raw values ----------------------------------------------------------------------------
RAW_HEX = re.compile(r"(?<![\w&/])#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
RAW_COLOR_FN = re.compile(r"\b(rgba?|hsla?|oklch|oklab|lab|lch|hwb|color)\(\s*[\d.]")
RAW_LENGTH = re.compile(r"(?<![\w.-])(?!1px\b)\d+(?:\.\d+)?(px|rem|em)\b")
RAW_FONT = re.compile(r"font-family\s*:|fontFamily\s*:")
NAMED_COLOR = re.compile(r"""(color|background|backgroundColor|borderColor|fill|stroke)\s*:\s*['"]?"""
                         r"""(white|black|red|blue|green|gray|grey|orange|yellow|purple|pink)\b""")
IMPORT = re.compile(r"""(?:\bfrom|\bimport|\brequire\()\s*['"]([^'"]+)['"]""")

# --- Tailwind classes ----------------------------------------------------------------------
TW_ARBITRARY = re.compile(r"(?<![\w-])[\w:-]*-\[[^\]\s]+\]")          # p-[13px], bg-[#fff]
TW_ARBITRARY_PROP = re.compile(r"(?<![\w-])\[[a-z-]+:[^\]\s]+\]")     # [mask:...]
COLOR_PREFIXES = ("bg", "text", "border", "ring", "fill", "stroke", "outline", "decoration",
                  "divide", "placeholder", "caret", "accent", "from", "via", "to", "shadow", "ring-offset")
TW_COLOR = re.compile(r"(?<![\w-])(?:[\w-]+:)*(" + "|".join(sorted(COLOR_PREFIXES, key=len, reverse=True))
                      + r")-([a-z][\w-]*?)(?:/\d+)?(?![\w-])")
NON_COLOR_SUFFIX = re.compile(
    r"^(\d+|x|y|[trblse]|[xy]-\d+|[trblse]-\d+|solid|dashed|dotted|double|hidden|none|collapse|separate|inset|"
    r"transparent|current|inherit|left|center|right|justify|start|end|wrap|nowrap|balance|pretty|ellipsis|clip|"
    r"cover|contain|fixed|local|scroll|repeat(-[xy]|-round|-space)?|no-repeat|top|bottom|auto|offset-\d+|"
    r"clip-\w+|origin-\w+|gradient-to-[trbl]{1,2}|opacity-\d+|thin|thick|wavy|underline-offset-\d+|"
    r"[trbl]{1,2})$"
)
TW_SPACING = re.compile(r"(?<![\w-])(?:[\w-]+:)*-?(p|px|py|pt|pr|pb|pl|ps|pe|m|mx|my|mt|mr|mb|ml|ms|me|gap|gap-x|gap-y|"
                        r"space-x|space-y|inset|inset-x|inset-y|top|right|bottom|left|start|end|scroll-m|scroll-p)-"
                        r"(\d+(?:\.\d+)?|px)(?![\w.-])")
TW_RADIUS = re.compile(r"(?<![\w-])(?:[\w-]+:)*rounded(?:-(?:t|r|b|l|s|e|tl|tr|br|bl|ss|se|es|ee))?(?:-([\w]+))?(?![\w-])")
TW_SHADOW = re.compile(r"(?<![\w-])(?:[\w-]+:)*shadow(?:-([a-z][\w-]*))?(?![\w-])")
TW_TEXT_SIZE = re.compile(r"(?<![\w-])(?:[\w-]+:)*text-(xs|sm|base|lg|[2-9]?xl)(?![\w-])")
TW_FONT_WEIGHT = re.compile(r"(?<![\w-])(?:[\w-]+:)*font-(thin|extralight|light|normal|medium|semibold|bold|extrabold|black)(?![\w-])")
TW_FONT_FAMILY = re.compile(r"(?<![\w-])(?:[\w-]+:)*font-(serif|sans|mono|display)(?![\w-])")
QUOTED = re.compile(r"""(["'`])((?:\\.|(?!\1).)*)\1""")


class DesignSystemError(Exception):
    pass


class Checker:
    def __init__(self, cfg: dict, root: str):
        d = cfg["design"]
        self.ui_paths = [p.strip("/") + "/" for p in d["ui_paths"]]
        self.components_dir = (d["components_dir"] or "").strip("/")
        self.tailwind = d["classes"] == "tailwind"
        self.raw_allowed = tuple(d["raw_values_allowed"])
        self.forbidden = list(d["forbidden_imports"])
        self.tokens_path = d["tokens"]
        self.vocab = self._load(os.path.join(root, *d["tokens"].split("/")))

    def _load(self, path: str) -> dict:
        try:
            with open(path, encoding="utf-8") as f:
                tokens = json.load(f)
            names = lambda family, prefix="": {  # noqa: E731
                t["name"].removeprefix(prefix) for t in tokens.get(family, {}).get("tokens", [])}
            vocab = {
                "colors": names("color"),
                "spacing": names("spacing", "space-") | {"0", "px"},
                "radii": names("radius", "radius-") | {"none"},
                "shadows": names("shadow", "shadow-") | {"none"},
                "type_styles": {s["name"] for g in tokens["type"]["groups"] for s in g["styles"]},
                "families": set(tokens["type"]["families"]),
            }
        except (OSError, ValueError, KeyError, TypeError) as e:
            raise DesignSystemError(f"the design system's `{self.tokens_path}` cannot be read ({e})") from e
        comp_dir = os.path.join(os.path.dirname(path), "components")
        vocab["components"] = {c for c in (os.listdir(comp_dir) if os.path.isdir(comp_dir) else [])
                               if os.path.isdir(os.path.join(comp_dir, c)) and c not in NOT_COMPONENTS}
        return vocab

    @classmethod
    def for_event(cls, event: dict) -> "Checker | None":
        """The checker for this project, or None when the design check is off."""
        cfg = lib.config(event)
        root = lib.git_root(event.get("cwd") or os.getcwd())
        if not root or not cfg["design"]["ui_paths"]:
            return None
        if not os.path.isfile(os.path.join(root, *cfg["design"]["tokens"].split("/"))):
            return None
        return cls(cfg, root)

    def is_ui_file(self, rel: str) -> bool:
        return (rel.startswith(tuple(self.ui_paths)) and rel.endswith(UI_EXTENSIONS)
                and not TEST_PATH.search(rel))

    def check_path(self, rel: str) -> list[str]:
        if not self.components_dir:
            return []
        m = re.match(re.escape(self.components_dir) + r"/([^/]+)\.(tsx|ts|jsx|js)$", rel)
        if not m or m.group(1) == "index":
            return []
        stem = m.group(1)
        name = "".join(p[:1].upper() + p[1:] for p in re.split(r"[-_]", stem)) if re.search(r"[-_]", stem) else stem
        if name in self.vocab["components"]:
            return []
        return [f"`{rel}`: `{self.components_dir}/` only holds design-system components "
                f"({', '.join(sorted(self.vocab['components']))}); `{name}` is not one. Put generic building "
                f"blocks elsewhere, or have the component added to the design system first."]

    def check_text(self, rel: str, text: str) -> list[str]:
        if not self.is_ui_file(rel):
            return []
        raw_allowed = rel.startswith(self.raw_allowed)
        problems: list[str] = []

        def add(rule, found, fix):
            p = f"`{rel}`: {rule} `{found}` → {fix}"
            if p not in problems:
                problems.append(p)

        v = self.vocab
        for line in text.splitlines():
            if not raw_allowed:
                for m in RAW_HEX.finditer(line):
                    if not m.group(0)[1:].isdigit():
                        add("raw colour", m.group(0), f"use a colour token: {', '.join(sorted(v['colors']))}")
                for m in RAW_COLOR_FN.finditer(line):
                    add("raw colour", m.group(0) + "…", "use a colour token")
                for m in NAMED_COLOR.finditer(line):
                    add("named colour", m.group(0), "use a colour token")
                for m in RAW_LENGTH.finditer(line):
                    add("raw length", m.group(0), "use spacing, radius or type tokens (only `1px` hairlines are allowed)")
                for m in RAW_FONT.finditer(line):
                    add("font family", m.group(0), f"use `font-{'`/`font-'.join(sorted(v['families']))}`")
            for m in IMPORT.finditer(line):
                if self._forbidden(m.group(1)):
                    add("import from", m.group(1), "this library is not allowed in this project")
            if self.tailwind:
                segments = [q.group(2) for q in QUOTED.finditer(line)]
                if rel.endswith((".css", ".scss")) and "@apply" in line:
                    segments.append(line)
                for segment in segments:
                    self._check_classes(segment, add)
        return problems

    def _forbidden(self, spec: str) -> bool:
        return any(spec == p or spec.startswith(p.rstrip("*").rstrip("/") + "/") and p.endswith("*")
                   or spec.startswith(p + "/") or fnmatch.fnmatchcase(spec, p) for p in self.forbidden)

    def _check_classes(self, line: str, add) -> None:
        v = self.vocab
        for m in TW_ARBITRARY.finditer(line):
            add("arbitrary Tailwind value", m.group(0), "use a token class; arbitrary values are not allowed")
        for m in TW_ARBITRARY_PROP.finditer(line):
            add("arbitrary Tailwind property", m.group(0), "use a token class")
        for m in TW_TEXT_SIZE.finditer(line):
            add("Tailwind text size", m.group(0),
                f"use a type style: {', '.join('text-' + s for s in sorted(v['type_styles']))}")
        for m in TW_FONT_WEIGHT.finditer(line):
            add("font weight", m.group(0), "weights come with the type style")
        for m in TW_FONT_FAMILY.finditer(line):
            if m.group(1) not in v["families"]:
                add("font family", m.group(0), f"use `font-{'`/`font-'.join(sorted(v['families']))}`")
        for m in TW_SPACING.finditer(line):
            if m.group(2) not in v["spacing"]:
                steps = sorted(v["spacing"] - {"px"}, key=lambda s: float(s) if s.replace(".", "").isdigit() else 0)
                add("spacing off the scale", m.group(0), f"spacing steps are {', '.join(steps)}")
        for m in TW_RADIUS.finditer(line):
            if m.group(1) not in v["radii"]:
                add("radius off the scale", m.group(0), f"use rounded-{'/rounded-'.join(sorted(v['radii']))}")
        for m in TW_SHADOW.finditer(line):
            if (m.group(1) or "") not in v["shadows"] and not (m.group(1) or "").startswith(tuple(v["colors"])):
                add("shadow off the scale", m.group(0), f"use shadow-{'/shadow-'.join(sorted(v['shadows']))}")
        for m in TW_COLOR.finditer(line):
            prefix, suffix = m.group(1), m.group(2)
            if prefix == "shadow":
                continue
            if prefix == "text" and (suffix in v["type_styles"] or re.fullmatch(r"xs|sm|base|lg|[2-9]?xl", suffix)):
                continue
            if prefix == "ring-offset" or NON_COLOR_SUFFIX.match(suffix):
                continue
            if suffix not in v["colors"]:
                add("colour off the palette", m.group(0), f"colours are: {', '.join(sorted(v['colors']))}")


def written_text(tool_input: dict) -> str:
    """What the tool call writes: Write's content, Edit's replacement, MultiEdit's replacements."""
    parts = [tool_input.get(k) for k in ("content", "new_string", "new_source")]
    parts += [e.get("new_string") for e in tool_input.get("edits") or [] if isinstance(e, dict)]
    return "\n".join(p for p in parts if isinstance(p, str))


def main(event: dict) -> None:
    tool_input = event.get("tool_input") or {}
    rel = lib.repo_relative(event, tool_input.get("file_path") or tool_input.get("notebook_path"))
    if rel is None:
        lib.allow()
    try:
        checker = Checker.for_event(event)
    except DesignSystemError as e:
        lib.deny(f"{e}. Fix the design system file; UI files cannot be checked until then.")
    if checker is None:
        lib.allow()
    problems = checker.check_path(rel) + checker.check_text(rel, written_text(tool_input))
    if problems:
        shown = "\n  ".join(problems[:15]) + ("\n  …and more." if len(problems) > 15 else "")
        lib.deny("this would invent styles outside the design system "
                 f"(`{checker.tokens_path}`):\n  {shown}\n"
                 "If the design system is missing something you need, don't work around it: report it "
                 "(agents: STATUS: blocked) so the design system is extended first.")
    lib.allow()
