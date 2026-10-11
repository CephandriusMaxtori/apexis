# Apexis — Implementation Plan

Status: Draft · Derived from Design Doc v0.1 · Audience: developers and power users · Ambition: 1.0

## 1. Settled decisions (close Design Doc §12)

| Question | Answer |
|---|---|
| Primary audience | Developers and power users |
| Base system | Fedora Atomic (rpm-ostree / OSTree) |
| Desktop | KDE Plasma now; niri + Quickshell for a future custom shell |
| Update model | Atomic, image-based (settled, inherited from Fedora) |
| Day-one hardware | x86_64, UEFI, Secure Boot, NVMe, AMD/Intel Mesa graphics. NVIDIA best-effort, off the 1.0 tested list |
| Release cadence | ISO per Fedora Atomic release + rolling `apexis-edge` channel |
| Team / governance | Sustained team effort; licensing and trademark clearance now in scope |

## 2. Performance targets (§8) with methodology

- **Cold boot** — define as *firmware handoff → interactive shell*. UEFI alone varies 3.2s–12.5s in the wild; we do not control it. Target `systemd-analyze` `graphical.target` **< 2.5s** on reference NVMe hardware.
- **Input latency** — **no compositor frame over 16ms** (60fps) during normal interaction. This is the real "smooth" metric and was missing from the design doc.
- **Idle RAM** — **publish no number yet.** Define the measurement first: fresh boot, no autostarts, 8GB config, 2 min idle, report `MemAvailable`. Published figures span 0.9GB–2.6GB for the same desktop depending on autostarts alone.
- **Install time** — user input only: **≤ 5 clicks, ≤ 3 minutes**.
- **Update rollback** — one reboot (`rpm-ostree rollback`).

## 3. New items the research forced into the plan

1. **Fedora trademark clearance — an M0 blocker, absent from the design doc §10.** Reusing the Fedora name/images under a rebrand requires permission under Fedora's formal trademark policy; GNOME/KDE logo use must be clarified too. Legal work with real lead time.
2. **A supported layering story, shipped day one.** Atomic drops most `/etc` changes on update (SteamOS's keep-list model documents the failure mode). For developers this is the largest support burden atomic brings. Ship Toolbox + Flatpak + a documented `/etc` keep-list rather than letting users discover it. Land in **M2**.
3. **App curation is a pipeline problem.** "No duplicate apps for the same job" fights Flathub, which routinely ships GNOME and Plasma variants of the same app. Needs a curation process, not just a policy.
4. **Security response** belongs in the risk register now that 1.0 is real, with a stated target.

## 4. Design-system note (§7.1 vs §6.4 resolved)

Plasma's *layout* is reachable via configuration: floating panels (`position: floating`) give a detached vertical dock, the top bar can be removed or reduced to a wordmark + single status pill, KWin provides real background blur, and Kvantum handles radii and typography. So M1 is Plasma *configured toward* §7.1 — not generic themed Plasma.

Not cheaply reachable: material depth — boosted saturation behind blur, bright inner top edges on every panel, and consistent 34px radii across shell, dialogs, and apps. That is where a Kvantum derivative plus a libadapta / Kirigami pass earns its keep, and where the custom shell eventually takes over. M1 and the future shell share renderer-agnostic design tokens (type scale, palette, radii, motion curves, glass spec), so nothing is thrown away.

## 5. Milestones

- **M0 — Spec.** Close §8 and §12 as above. Start trademark clearance first; it gates everything. Define the design system as renderer-agnostic tokens.
- **M1 — Prototype ISO.** `coreos-assembler` manifest + `overlay.d/`. Plasma themed to tokens: floating dock, no top bar, centered launcher, KWin blur. Default app set via Flatpak. Publish a real measured boot profile.
- **M2 — Installer + updates.** Install experience (disk, user, timezone, optional FDE). Ship the layering story and keep-list docs here — that is where developer users hit it.
- **M3 — Alpha.** Enforced hardware list. App-curation pipeline for duplicate apps. CI + reproducible build verification.
- **M4 — Beta → 1.0.** Security response process, support channels, upgrade path from M1–M3 images.

## 6. Build tooling

- Image build: **coreos-assembler** (`manifest.yaml` for packages, `overlay.d/` for config and scripts) inside Podman.
- App delivery: **Flatpak** for GUI apps; native RPM only for base system and CLI tooling, layered via `rpm-ostree`.
- Dev tooling: **Toolbox** containers.
- Theme: **Kvantum** derivative + Plasma layout config + KWin effects.

## 7. Open items

- **Trademark approach** — approach Fedora Project directly, or research what an unaffiliated rebrand requires? Changes whether M0 blocks on an external dependency.
- **Geist font licensing** — verify the exact OFL license file ships with the typeface before bundling.
- **NVIDIA policy detail** — how to handle driver installation/secure boot for best-effort NVIDIA users in the first ISO.