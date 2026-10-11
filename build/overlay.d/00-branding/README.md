# 00-branding

Removes Fedora identity from the image. This directory exists to make the
trademark obligation explicit and locatable in the build rather than buried in
`manifest.yaml`.

## What is removed where

| What | Where |
|---|---|
| Fedora wordmark, boot splash, Anaconda branding | `exclude-packages: fedora-logos*` in `../manifest.yaml` |
| OS identity (`NAME`, `ID`, `VERSION`) | `ostree: osname/osid/version` in `../image.yaml` |

Fedora's EULA is explicit: *"If User modifies the Software, then User must
replace all images containing the 'Fedora' trademark."* Those images live in the
`fedora-logos` packages. Excluding them is a legal obligation, not a stylistic
choice — see `plan.md` §3.1.

Apexis is not a Fedora Spin, is not affiliated with the Fedora Project or Red
Hat, and does not use the Fedora or Fedora Remix marks. Where Apexis describes
itself as *derived from* Fedora, it says so plainly and states that it is not
Fedora.

## Still to do

- **Plymouth splash.** `image.yaml` currently uses the base image's. The splash
  is part of the first-boot impression and Design Doc §2 asks for a quiet,
  flicker-free boot, so it needs Apexis branding — but only once the logo
  exists, which it does not yet (Design Doc §7 is open on logo and wallpaper).
- **Anaconda installer branding.** Covered by the `fedora-logos-anaconda`
  exclusion above; will need its own assets for the M2 graphical installer.
- **First-boot release notes / what-s-new**, once there is a product to
  describe.