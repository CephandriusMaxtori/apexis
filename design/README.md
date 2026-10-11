# Apexis design system

The renderer-agnostic design tokens behind Design Doc §7.1.

## Why this shape

Design Doc §6.4 and §7.1 were in conflict: §6.4 assumed a curated desktop,
§7.1 described a custom shell. The plan resolves this by shipping Plasma first
and a custom shell later — but only if both can consume **the same design
decisions**. That is what this directory is: one token file, several renderers,
no fork required when the shell arrives.

Plasma's *layout* is reachable via configuration (floating panels, KWin blur,
Kvantum radii). The material depth — boosted saturation behind the blur, bright
inner edges, consistent 34px radii — is not, and is where the custom shell
eventually takes over. Tokens are shared; the renderer is not.

## Layout

```
design/
├── tokens/apexis.json      canonical source of truth — edit this
├── src/color.py            OKLCH / OKLab / sRGB maths, gamut mapping, WCAG contrast
├── src/generate.py         resolves the token graph, emits every format, validates
└── dist/                   generated — committed, do not edit
```

## Colours are authored in OKLCH

Perceptual lightness is the axis worth reasoning about; hex codes are an output
format, not a source of truth. Two consequences:

- **A ramp is one number.** Give `color.py` a hue and a peak chroma and it
  produces the whole tonal scale.
- **Out-of-gamut colours lose chroma, never lightness or hue.** Clipping those
  instead is what makes a system drift between themes — a colour ends up
  meaning something slightly different from the token that named it.

sRGB hex values pinned by the design doc (`#2c3fe0` light accent, `#a3afff`
dark) are used verbatim and are not regenerated.

## Contrast is enforced, not documented

Design Doc principle 5 says fast is a feature and metrics are tracked, not
afterthoughts. A design system is the same: `design/tokens/apexis.json` carries
a `contrast.pairs` list, and every build asserts it. A token change that breaks
readability **fails the build** instead of shipping.

```
$ python design/src/generate.py --check
```

Current worst case is `fg-subtle` on the light canvas at 4.61:1. Light-mode
`fg-muted` and `fg-subtle` are set as explicit OKLCH values rather than ramp
steps: `slate.600` fails AA at 3.62:1, and placeholder text is content.

CI runs this on every push (`.github/workflows/tokens.yml`).

## Output formats

| File | Consumer |
|---|---|
| `dist/apexis.tokens.json` | Anything. Fully resolved and flat — no expressions. |
| `dist/apexis-light.colors`, `dist/apexis-dark.colors` | Plasma 6 colour schemes (kcfg), 35 roles each |
| `dist/apexis-kvantum/apexis-kvantum.config` | Kvantum — Qt widget layer, radii per theme |
| `dist/apexis-qml/Tokens.qml` | The future niri/Quickshell shell |
| `dist/apexis.css` | Docs site, first-party web surfaces, mockups |
| `dist/palette.md` | Human reference |

Generated output is committed deliberately. The image build should not need
Python installed to produce a theme, and reviewing a diff of resolved values is
more useful than reviewing a diff of templates.

## The glass material

§7.1 specifies "translucent panels with heavy background blur, boosted
saturation, bright inner top edges and large rounded corners". That is the
system's one material, so it is specified once under `glass` and referenced by
every surface that uses it. Variants differ only in blur radius, corner radius
and edge opacity — `panel`, `dock`, `launcher`, `popover`, `status-pill`.

Compositor-facing values (blur, saturation) are emitted for the future shell;
KWin applies its own blur for the M1 Plasma theme.

## Rules

1. Edit `tokens/apexis.json`. Never `dist/`.
2. Reference semantic tokens from components, never raw ramp steps — that is
   what keeps light and dark in step.
3. Space is a 4px grid. Nothing should introduce a non-multiple of 4.
4. Accent belongs on small interactive surfaces, not large fills.
5. New colour tokens ship with a contrast pair, or they don't ship.

## Still open

- Icon set is undecided (§7). Until then, KDE Breeze is the fallback.
- Motion curves are proposed here (`quick-out`, `standard`, `emphasized`,
  `spring`) and have not been reviewed against real interaction timings. The
  16ms frame budget in plan.md §2 is what they should be tuned against.
- Wallpaper generation is not in this directory. The palette is derived from
  §7.1's description, but producing the periwinkle-to-teal gradient itself is
  a separate piece of work.