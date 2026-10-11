# dist/ — generated output

Everything in this directory is produced by `python design/src/generate.py` from `design/tokens/apexis.json`.
Do not edit these files; edit the token source and rebuild.

Generated output is committed deliberately: the image build should not
need Python installed to produce a theme, and reviewing a diff of
resolved values is more useful than reviewing a diff of templates.

| File | Consumer |
|---|---|
| `apexis.tokens.json` | Anything. Fully resolved, flat, no expressions. |
| `apexis.css` | Docs site, first-party web surfaces, mockups |
| `apexis-light.colors` / `apexis-dark.colors` | Plasma 6 colour schemes (kcfg) |
| `apexis-kvantum/apexis-kvantum.config` | Kvantum — Qt widget layer and radii |
| `apexis-qml/Tokens.qml` | Future niri/Quickshell shell |
| `palette.md` | Human reference |
