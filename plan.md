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

1. **Fedora trademark compliance — a checklist, not a blocker.** Fedora's own redistribution policy explicitly sanctions the plan: *"you may not modify the Fedora installation and maintain the Fedora name. The nearest you may do is completely rebrand the distribution... and distribute the product under a different name."* No permission or clearance from Fedora or Red Hat is required. See §3.1 for the concrete obligations. (An earlier draft of this plan wrongly called this an M0 blocker.)
2. **A supported layering story, shipped day one.** Atomic drops most `/etc` changes on update (SteamOS's keep-list model documents the failure mode). For developers this is the largest support burden atomic brings. Ship Toolbox + Flatpak + a documented `/etc` keep-list rather than letting users discover it. Land in **M2**.
3. **App curation is a pipeline problem.** "No duplicate apps for the same job" fights Flathub, which routinely ships GNOME and Plasma variants of the same app. Needs a curation process, not just a policy.
4. **Security response** belongs in the risk register now that 1.0 is real, with a stated target.

### 3.1 Trademark and licensing compliance

Fedora is FOSS: *"Anyone may download, use, modify, and redistribute it without charge."* Only the **trademark** is restricted, and the restriction is satisfied by doing exactly what Apexis already plans to do — shipping under its own name. Required:

- **Remove all Fedora trademark imagery.** Drop `fedora-logos` from the image manifest and replace boot/splash/about assets. The Fedora EULA is explicit: *"If User modifies the Software, then User must replace all images containing the 'Fedora' trademark."*
- **Never present Apexis as Fedora.** Not "Fedora Apexis", not an "edition of Fedora", not "contains Fedora". You may say **"a derivative of Fedora"** or **"built upon Fedora"**, provided you make clear Apexis *is not* Fedora and is not endorsed by Fedora or Red Hat.
- **Carry the attribution.** State that *Fedora is a registered trademark of Red Hat, Inc.*
- **Optional:** use the "Fedora Remix" secondary mark to signal derivation. Usable **without permission**, but you must follow its usage guidelines — never recolour, rearrange, stretch or distort it, and pick a palette variant appropriate to the background.

**Not required:** any permission, licence, or "approved derivatives" agreement from Fedora or Red Hat. Nobara and Asahi Remix are precedent — Nobara states outright that it is *"NOT... a 'Fedora Spin'... completely independent project from Fedora"*, and Fedora staff publicly confirm it as a legitimate downstream remix.

**Other marks in the stack:**

| Mark | Owner | Practical rule for Apexis |
|---|---|---|
| GNOME, GTK, **Flatpak**, **Flathub** | GNOME Foundation | Use descriptively ("built on Flatpak", "apps from Flathub"). Never brand the Apexis app store with the Flathub logo — Flathub is a *source*, not the storefront identity. This aligns with the "one app store" goal anyway. |
| KDE®, K Desktop Environment® | KDE e.V. | Use "KDE Plasma" descriptively. Do not use their logo as Apexis brand. |
| Linux® | Linus Torvalds | Fine in descriptive text; never inside the Apexis logo or wordmark. |
| **Geist** | Vercel / basement.studio | **Cleared.** SIL OFL 1.1, and upstream declares **no Reserved Font Name** — so bundling, embedding, subsetting and conversion (e.g. TTF→WOFF2) are all permitted while keeping the "Geist" family name. Obligations: don't sell the font standalone, ship the copyright notice + OFL text with each copy, and don't relicense derivatives. |

One bonus of the Fedora base: because Red Hat is a US company bound by US patent law, everything in the Fedora repositories is patent-clean by construction — a real advantage for a redistributor.

## 4. Design-system note (§7.1 vs §6.4 resolved)

Plasma's *layout* is reachable via configuration: floating panels (`position: floating`) give a detached vertical dock, the top bar can be removed or reduced to a wordmark + single status pill, KWin provides real background blur, and Kvantum handles radii and typography. So M1 is Plasma *configured toward* §7.1 — not generic themed Plasma.

Not cheaply reachable: material depth — boosted saturation behind blur, bright inner top edges on every panel, and consistent 34px radii across shell, dialogs, and apps. That is where a Kvantum derivative plus a libadapta / Kirigami pass earns its keep, and where the custom shell eventually takes over. M1 and the future shell share renderer-agnostic design tokens (type scale, palette, radii, motion curves, glass spec), so nothing is thrown away.

## 5. Milestones

- **M0 — Spec.** Close §8 and §12 as above. Drop `fedora-logos` from the image and add trademark attribution (see §3.1) — housekeeping, not a gate. Define the design system as renderer-agnostic tokens.
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

- **NVIDIA policy detail** — how to handle driver installation/secure boot for best-effort NVIDIA users in the first ISO.
- **App store branding** — confirm the storefront ships as "Apexis Software" with Flathub listed as an upstream source, per §3.1.

### Resolved

- ~~Trademark approach~~ — closed. No permission needed; see §3.1.
- ~~Geist font licensing~~ — closed. OFL-1.1, no Reserved Font Name, bundling cleared; see §3.1.