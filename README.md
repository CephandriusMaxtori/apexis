# Apexis

> **Status: design draft.** Nothing here is installable yet. There is no ISO, no
> installer, and no working system. The repository currently holds a design
> specification and a design token system.

A Linux distribution built around one idea: it should feel **smooth and clean**.
Fast to boot, quiet by default, visually consistent, and free of the clutter and
rough edges most distributions accumulate.

The full specification is [`plan.md`](plan.md).

## Where things stand

We are at the start of **M0 (Spec)**. The open questions from the design doc
have been researched and closed:

| Question | Answer |
|---|---|
| Base system | Fedora Atomic (rpm-ostree) |
| Desktop | KDE Plasma now; niri + Quickshell for a future custom shell |
| Update model | Atomic, image-based — all-or-nothing, rollback is one reboot |
| Primary audience | Developers and power users |
| Day-one hardware | x86_64, UEFI, Secure Boot, NVMe, AMD/Intel Mesa graphics. NVIDIA best-effort, off the 1.0 tested list |
| Release cadence | ISO per Fedora Atomic release, plus a rolling `apexis-edge` channel |

Design Doc §6.4 and §7.1 were in direct conflict — §6.4 assumed a curated
desktop, §7.1 described a custom shell. That is resolved by shipping a Plasma
image configured toward the §7.1 visual direction, while keeping the design
tokens renderer-agnostic so the custom shell can adopt them later.

**Not yet started:** image build, installer, update pipeline, hardware
enablement, branding.

## Layout

```
plan.md              the specification and implementation plan
design/
  README.md          how the design token system works
  tokens/apexis.json canonical source of truth — edit this
  src/               OKLCH colour maths + the generator
  dist/              generated output for every renderer (committed)
.github/workflows/   CI gate for the token system
```

## Design system

Design Doc principle 5 says fast is a feature and metrics are tracked, not
afterthoughts. The same applies here: **contrast is enforced by the build, not
documented.**

```sh
python design/src/generate.py --check    # validate only
python design/src/generate.py            # rebuild dist/
```

No dependencies beyond the standard library. Colours are authored in OKLCH
rather than hex, and a token change that breaks readability fails the build
instead of shipping. See [`design/README.md`](design/README.md).

Current worst case across all 12 checked pairs is 4.61:1 against a WCAG AA floor
of 4.5:1.

## Trademark and licensing

Apexis is a fully independent project. It is **not** Fedora, not a Fedora Spin,
and is not affiliated with, endorsed by, or sponsored by the Fedora Project or
Red Hat. It is a derivative that uses Fedora packages, code and repositories —
that is the extent of the relationship.

Fedora is a registered trademark of Red Hat, Inc. All Fedora trademark imagery
is removed from Apexis builds. Full obligations, and the marks belonging to GNOME
Foundation (GNOME, GTK, Flatpak, Flathub) and KDE e.V., are documented in
[`plan.md` §3.1](plan.md).

Bundled typefaces: **Geist**, SIL Open Font License 1.1 (© 2023 Vercel, in
collaboration with basement.studio). Upstream declares no Reserved Font Name.

## Contributing

Not yet open for outside contributions — there is no contributor guide or code
of conduct, and the foundations are still moving. If you want to follow along,
watch the repository.

## Licence

To be decided. Governance and licensing are recorded as in-scope work in
[`plan.md` §1](plan.md), but no specific licence has been chosen yet — the
question carried over from the design doc. The design tokens, the generator and
everything in `design/dist/` are covered by whichever licence is adopted.