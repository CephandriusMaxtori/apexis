#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Nolan Bragan
# SPDX-License-Identifier: MPL-2.0

"""Resolve the Apexis token graph and emit every renderer format.

The token file is the single source of truth. This script is the only thing
that reads it, and everything under `design/dist/` is committed output — the
image build must not need Python to produce a theme, and reviewing a diff of
generated files is more useful than reviewing a diff of a template.

Usage:
    python design/src/generate.py           # build and validate
    python design/src/generate.py --check   # validate only, write nothing
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import color as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TOKENS_PATH = ROOT / "tokens" / "apexis.json"
DIST = ROOT / "dist"

COMMENT_KEYS = {"$comment"}


def write(path: Path, text: str) -> None:
    """Write UTF-8 text with LF endings, on every platform.

    Python's text mode translates \n to os.linesep, which on Windows would emit
    CRLF and make generated output differ by platform. CI validates on
    ubuntu-latest while development happens on Windows, so the committed
    artifacts must not depend on which one produced them.
    """
    path.write_text(text, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


class Resolver:
    def __init__(self, tokens: dict) -> None:
        self.tokens = tokens
        self.ramps: dict[str, dict[int, str]] = {}
        for name, spec in tokens["families"].items():
            if name in COMMENT_KEYS:
                continue
            self.ramps[name] = C.build_ramp(spec["hue"], spec["chroma"])

        self.resolved: dict[str, dict[str, str]] = {"light": {}, "dark": {}}
        for theme, palette in tokens["palette"].items():
            if theme in COMMENT_KEYS:
                continue
            for key, spec in palette.items():
                if key in COMMENT_KEYS:
                    continue
                self.resolved[theme][key] = self._resolve(spec)

    def _resolve(self, spec: dict) -> str:
        """Resolve one colour expression to a CSS-usable string.

        Normalises to sRGB on the way out so every branch formats identically.
        """
        if "oklch" in spec:
            rgb = C.oklch_to_srgb(*spec["oklch"])
        elif "ref" in spec:
            family, _, step = spec["ref"].partition(".")
            if family not in self.ramps:
                raise KeyError(f"unknown colour family: {family}")
            rgb = C.from_hex(self.ramps[family][int(step)])
        elif "hex" in spec:
            rgb = C.from_hex(spec["hex"])
        else:
            raise ValueError(f"unrecognised colour spec: {spec}")

        alpha = spec.get("alpha")
        if alpha is None:
            return C.hex_from_srgb(rgb)
        return C.with_alpha(rgb, alpha)

    def rgb(self, theme: str, key: str) -> tuple[float, float, float]:
        return C.from_hex(self.resolved[theme][key])

    def css(self, theme: str, key: str) -> str:
        return self.resolved[theme][key]


def camel(name: str) -> str:
    head, *rest = name.split("-")
    return head + "".join(part.capitalize() for part in rest)


def qml_color(css: str) -> str:
    """CSS colour string -> QML literal. QML has no `rgba()`, only `Qt.rgba()`."""
    if css.startswith("rgba("):
        r, g, b, a = (p.strip() for p in css[5:-1].split(","))
        return f"Qt.rgba({r}, {g}, {b}, {a})"
    return css


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def check_contrast(tokens: dict, r: Resolver) -> list[str]:
    spec = tokens["contrast"]
    floor = spec.get("minimum", 4.5)
    failures: list[str] = []

    for pair in spec["pairs"]:
        theme = next(t for t in pair if t in ("light", "dark"))
        fg, bg = pair[theme]
        required = pair.get("min", floor)
        ratio = C.contrast_ratio(r.rgb(theme, fg), r.rgb(theme, bg))
        status = "ok " if ratio >= required else "FAIL"
        print(f"  [{status}] {theme:5} {fg:22} on {bg:18} {ratio:5.2f}:1 (min {required})")
        if ratio < required:
            failures.append(f"{theme}/{fg} on {bg}: {ratio:.2f}:1 < {required}")

    return failures


# ---------------------------------------------------------------------------
# Emitters
# ---------------------------------------------------------------------------

# Plasma 6 ColorScheme role -> semantic token. The theme is chosen by the
# emitter, not baked in here: "Background" means bg-canvas, which resolves
# light or dark as appropriate.
PLASMA_ROLES: dict[str, str] = {
    "Background": "bg-canvas",
    "BackgroundAlternate": "bg-surface",
    "BackgroundFaint": "bg-sunken",
    "Foreground": "fg-default",
    "ForegroundAlternate": "fg-muted",
    "ForegroundFaint": "fg-subtle",
    "Decoration": "border-default",
    "DecorationHover": "accent-hover",
    "DecorationFocus": "focus-ring",
    "DecorationText": "fg-default",
    "SelectionBackground": "accent-default",
    "SelectionForeground": "fg-on-accent",
    "SelectionDecoration": "accent-default",
    "PlaceholderText": "fg-subtle",
    "ButtonBackground": "bg-surface",
    "ButtonForeground": "fg-default",
    "ButtonHover": "border-default",
    "ButtonDecoration": "accent-default",
    "ButtonText": "fg-default",
    "ViewBackground": "bg-surface",
    "ViewForeground": "fg-default",
    "ViewDecoration": "border-subtle",
    "FieldBackground": "bg-sunken",
    "FieldForeground": "fg-default",
    "FieldPlaceholderText": "fg-subtle",
    "WindowBackground": "bg-surface",
    "WindowForeground": "fg-default",
    "WindowDecoration": "border-default",
    "LinkColor": "accent-default",
    "VisitedLink": "accent-muted",
    "Positive": "success",
    "Negative": "destructive",
    "Neutral": "warning",
    "Warning": "warning",
    "PlaceholderBackground": "bg-sunken",
}

KVANTUM_KEYS: dict[str, str] = {
    "window.color": "bg-surface",
    "window.text.color": "fg-default",
    "base.color": "bg-surface",
    "base.text.color": "fg-default",
    "base.hover.color": "bg-sunken",
    "base.hover.text.color": "fg-default",
    "base.active.color": "accent-default",
    "base.active.text.color": "fg-on-accent",
    "base.highlight.color": "accent-default",
    "base.highlight.text.color": "fg-on-accent",
    "base.selected.color": "accent-default",
    "tooltip.base.color": "bg-overlay",
    "tooltip.text.color": "fg-default",
    "tooltip.base.border.color": "border-default",
    "Button.flat.color": "fg-default",
    "Button.flat.hover.color": "fg-default",
    "Button.flat.pressed.color": "fg-muted",
    "Button.flat.border.color": "border-default",
    "Button.flat.border.hover.color": "border-strong",
    "icon.color": "fg-muted",
    "icon.color.disabled": "fg-subtle",
    "icon.color.hover": "fg-default",
    "icon.color.active": "accent-default",
    "icon.color.normal": "fg-default",
    "icon.color.selected": "accent-default",
    "widget.line.color": "border-subtle",
    "widget.divider.color": "border-subtle",
    "widget.text.color": "fg-muted",
    "focus.color": "focus-ring",
    "focus.border.color": "focus-ring",
}


def emit_css(tokens: dict, r: Resolver) -> str:
    """CSS custom properties — for the docs site and first-party web surfaces."""
    t = tokens["typography"]
    out = [
        "/* Apexis design tokens — GENERATED, do not edit.",
        f" * Source: design/tokens/apexis.json (v{tokens['version']})",
        " * Regenerate: python design/src/generate.py",
        " */",
        ":root {",
    ]
    out.append(f"  --font-sans: {t['sans']}, {t['fallbackSans']};")
    out.append(f"  --font-mono: {t['mono']}, {t['fallbackMono']};")

    for theme in ("light", "dark"):
        sel = ":root" if theme == "light" else f'[data-theme="{theme}"]'
        out.append(f"  /* {theme} */")
        out.append(f"  {sel} {{")
        for key, value in r.resolved[theme].items():
            out.append(f"    --color-{key}: {value};")
        for key, v in r.resolved[theme].items():
            if key.startswith("bg-glass"):
                out.append(f"    --{key}-blur: 40px;")
                out.append(f"    --{key}-saturation: {tokens['glass']['saturation']};")
        out.append("  }")

    for key, spec in tokens["radii"].items():
        out.append(f"  --radius-{key}: {spec}px;")
    for key, value in tokens["space"].items():
        out.append(f"  --space-{key}: {value}px;")
    for key, spec in tokens["typography"]["scale"].items():
        out.append(
            f"  --text-{key}: {spec['weight']} {spec['size']}px/{spec['line']}px "
            f"var(--font-{'mono' if spec.get('mono') else 'sans'});"
        )
        out.append(f"  --tracking-{key}: {spec['tracking']}em;")
    for key, curve in tokens["motion"]["curve"].items():
        out.append(f"  --ease-{key}: cubic-bezier({', '.join(str(c) for c in curve)});")
    for key, ms in tokens["motion"]["duration"].items():
        out.append(f"  --duration-{key}: {ms}ms;")

    for name, spec in tokens["glass"]["variants"].items():
        out.append(f"  --glass-{name}-blur: {spec['blur']}px;")
        out.append(f"  --glass-{name}-radius: {spec['radius']}px;")
        out.append(f"  --glass-{name}-saturation: {tokens['glass']['saturation']};")

    out.append("}")
    return "\n".join(out) + "\n"


def emit_kcfg(tokens: dict, r: Resolver, theme: str) -> str:
    """A standalone Plasma 6 colour scheme (kcfg) for one theme.

    Plasma loads one file per scheme, so light and dark are separate files
    rather than two entries in one — Plasma names them `<name>.colors`.
    """
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kcfg xmlns="http://www.kde.org/standards/kcfg/1.0"',
        '       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        '       xsi:schemaLocation="http://www.kde.org/standards/kcfg/1.0'
        ' http://www.kde.org/standards/kcfg/1.0/kcfg.xsd">',
        '  <kcfgfile name=""/>',
        '  <group name="">',
        '    <entry name="Colors" type="Color">',
        f"      <label>Apexis {theme} colour scheme</label>",
        "      <defaults>",
    ]
    for role, key in PLASMA_ROLES.items():
        lines.append(f'        <color name="{role}" rgb="{r.css(theme, key)}"/>')
    lines += [
        "      </defaults>",
        "    </entry>",
        "  </group>",
        "</kcfg>",
    ]
    return "\n".join(lines) + "\n"


def emit_kvantum(tokens: dict, r: Resolver) -> str:
    """Kvantum theme config — handles radii and the Qt widget layer."""
    lines = [
        "; Apexis — Kvantum theme — GENERATED, do not edit.",
        f"; Source: design/tokens/apexis.json (v{tokens['version']})",
        "",
        "[General]",
        "name=Apexis",
        "author=Apexis Project",
        "version=%s" % tokens["version"],
        "qt4support=false",
        "qt5ctsupport=false",
        "qt6ctsupport=true",
        "svgdisabled=true",
        "",
        "[%General]",
        "alldefault=true",
        "menushade=1",
    ]
    for theme in ("light", "dark"):
        lines.append(f"[%{theme.title()}]")
        lines.append(f"wm_border_active_color={r.css(theme, 'border-default')}")
        lines.append(f"wm_border_inactive_color={r.css(theme, 'border-subtle')}")
        for key, spec in tokens["radii"].items():
            if key == "none":
                continue
            lines.append(f"wm_{key}_radius={spec}")
            lines.append(f"tooltip_{key}_radius={spec}")
            lines.append(f"menu_{key}_radius={spec}")
            lines.append(f"tab_{key}_radius={spec}")
        lines.append("")

    for theme in ("light", "dark"):
        lines.append(f"[{theme.title()}]")
        for key, token in KVANTUM_KEYS.items():
            lines.append(f"{key}={r.css(theme, token)}")
        lines.append("")

    return "\n".join(lines) + "\n"


def emit_qml(tokens: dict, r: Resolver) -> tuple[str, str]:
    """QML token object for the future niri/Quickshell shell."""
    palette = ["pragma Singleton", "", "import QtQuick", "", "QtObject {", "    id: root", ""]
    for theme in ("light", "dark"):
        palette.append(f"    readonly property QtObject {theme}: QtObject {{")
        for key, value in r.resolved[theme].items():
            palette.append(f"        readonly property color {camel(key)}: {qml_color(value)}")
        palette.append("    }")
        palette.append("")

    radii = ["    readonly property QtObject radius: QtObject {"]
    for key, value in tokens["radii"].items():
        radii.append(f"        readonly property int {camel(key)}: {value}")
    radii.append("    }")

    space = ["    readonly property QtObject space: QtObject {"]
    for key, value in tokens["space"].items():
        space.append(f"        readonly property int {camel(key)}: {value}")
    space.append("    }")

    duration = ["    readonly property QtObject duration: QtObject {"]
    for key, value in tokens["motion"]["duration"].items():
        duration.append(f"        readonly property int {camel(key)}: {value}")
    duration.append("    }")

    glass = ["    readonly property QtObject glass: QtObject {"]
    glass.append(f"        readonly property int saturation: "
                 f"{int(tokens['glass']['saturation'] * 100)}")
    glass.append("        readonly property QtObject variants: QtObject {")
    for key, spec in tokens["glass"]["variants"].items():
        glass.append(f"            readonly property QtObject {camel(key)}: QtObject {{")
        glass.append(f"                readonly property int blur: {spec['blur']}")
        glass.append(f"                readonly property int radius: {spec['radius']}")
        glass.append(f"                readonly property int edgeWidth: {spec['edgeWidth']}")
        glass.append("            }")
    glass.append("        }")
    glass.append("    }")

    typography = ["    readonly property QtObject typography: QtObject {"]
    for key, spec in tokens["typography"]["scale"].items():
        name = camel(key)
        typography.append(f"        readonly property QtObject {name}: QtObject {{")
        typography.append(f"            readonly property int pixelSize: {spec['size']}")
        typography.append(f"            readonly property int lineHeight: {spec['line']}")
        typography.append(f"            readonly property int weight: {spec['weight']}")
        typography.append(f"            readonly property real tracking: {spec['tracking']}")
        typography.append("        }")
    typography.append("    }")

    body = "\n".join(
        palette + radii + space + duration + glass + typography + ["}", ""]
    )
    qmldir = (
        "module Apexis\n"
        "singleton Tokens 1.0 Tokens.qml\n"
    )
    return body, qmldir


def emit_tokens_json(tokens: dict, r: Resolver) -> dict:
    """Fully resolved, flat tokens — what other languages consume."""
    return {
        "name": tokens["name"],
        "version": tokens["version"],
        "generatedFrom": "design/tokens/apexis.json",
        "families": {k: v for k, v in r.ramps.items()},
        "palette": r.resolved,
        "typography": tokens["typography"],
        "space": tokens["space"],
        "radii": tokens["radii"],
        "motion": tokens["motion"],
        "glass": tokens["glass"],
        "elevation": tokens["elevation"],
    }


def emit_markdown(tokens: dict, r: Resolver) -> str:
    out = [
        "# Apexis palette reference",
        "",
        f"Generated from `design/tokens/apexis.json` v{tokens['version']}. "
        "Do not edit — regenerate instead.",
        "",
        "## Accents (pinned by Design Doc §7.1)",
        "",
        "| Token | Light | Dark |",
        "|---|---|---|",
        f"| `accent-default` | `{r.css('light', 'accent-default')}` | "
        f"`{r.css('dark', 'accent-default')}` |",
        "",
        "## Semantic surface",
        "",
        "| Token | Light | Dark |",
        "|---|---|---|",
    ]
    for key in r.resolved["light"]:
        out.append(
            f"| `{key}` | `{r.css('light', key)}` | `{r.css('dark', key)}` |"
        )

    out += ["", "## Ramps", ""]
    for family, ramp in r.ramps.items():
        out.append(f"### {family}")
        out.append("")
        out.append("| " + " | ".join(str(s) for s in ramp) + " |")
        out.append("|" + "---|" * len(ramp))
        out.append("| " + " | ".join(f"`{v}`" for v in ramp.values()) + " |")
        out.append("")

    return "\n".join(out) + "\n"


def emit_dist_readme() -> str:
    return (
        "# dist/ — generated output\n\n"
        "Everything in this directory is produced by "
        "`python design/src/generate.py` from `design/tokens/apexis.json`.\n"
        "Do not edit these files; edit the token source and rebuild.\n\n"
        "Generated output is committed deliberately: the image build should not\n"
        "need Python installed to produce a theme, and reviewing a diff of\n"
        "resolved values is more useful than reviewing a diff of templates.\n\n"
        "| File | Consumer |\n|---|---|\n"
        "| `apexis.tokens.json` | Anything. Fully resolved, flat, no expressions. |\n"
        "| `apexis.css` | Docs site, first-party web surfaces, mockups |\n"
        "| `apexis-light.colors` / `apexis-dark.colors` | Plasma 6 colour schemes (kcfg) |\n"
        "| `apexis-kvantum/apexis-kvantum.config` | Kvantum — Qt widget layer and radii |\n"
        "| `apexis-qml/Tokens.qml` | Future niri/Quickshell shell |\n"
        "| `palette.md` | Human reference |\n"
    )


# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="validate only, write nothing")
    args = ap.parse_args()

    tokens = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
    resolver = Resolver(tokens)

    print(f"Apexis tokens v{tokens['version']} — contrast validation")
    failures = check_contrast(tokens, resolver)

    if failures:
        print("\nContrast validation FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("\nAll contrast pairs pass.\n")

    if args.check:
        return 0

    DIST.mkdir(parents=True, exist_ok=True)
    write(DIST / "apexis.css", emit_css(tokens, resolver))
    for theme in ("light", "dark"):
        write(DIST / f"apexis-{theme}.colors", emit_kcfg(tokens, resolver, theme))

    kv = DIST / "apexis-kvantum"
    kv.mkdir(exist_ok=True)
    write(kv / "apexis-kvantum.config", emit_kvantum(tokens, resolver))

    qml = DIST / "apexis-qml"
    qml.mkdir(exist_ok=True)
    body, qmldir = emit_qml(tokens, resolver)
    write(qml / "Tokens.qml", body)
    write(qml / "qmldir", qmldir)

    write(DIST / "apexis.tokens.json", json.dumps(emit_tokens_json(tokens, resolver), indent=2) + "\n")
    write(DIST / "palette.md", emit_markdown(tokens, resolver))
    write(DIST / "README.md", emit_dist_readme())

    print(f"Wrote {len(list(DIST.rglob('*')))} entries to {DIST.relative_to(ROOT.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())