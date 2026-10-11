#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Nolan Bragan
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Build an Apexis image.
#
# Stages the generated design tokens into the overlay before invoking
# coreos-assembler, so the image and the tokens can never drift apart. CI
# regenerates tokens and fails on staleness; this script copies them in.
#
# Requires a Linux host with Podman and /dev/kvm. See build/README.md.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$REPO_ROOT/build"
CONFIG_DIR="$BUILD_DIR"
WORK_DIR="$REPO_ROOT/.build"
STAGE_DIR="$CONFIG_DIR/overlay.d/30-apexis"

COSA_IMAGE="quay.io/coreos-assembler/coreos-assembler:latest"
COSA_CONTAINER="${COSA_CONTAINER:-apexis-cosa}"

die() { printf '\033[31merror:\033[0m %s\n' "$*" >&2; exit 1; }
step() { printf '\033[1m==>\033[0m %s\n' "$*"; }

# --- Preflight ------------------------------------------------------------

command -v podman >/dev/null 2>&1 || die "podman not found. See build/README.md."
[[ -w /dev/kvm && -e /dev/kvm ]] || die "/dev/kvm not available. coreos-assembler needs hardware virtualisation."
[[ "$(uname -s)" == "Linux" ]] || die "coreos-assembler runs on Linux only."

# --- Design tokens --------------------------------------------------------

step "Regenerating design tokens"
python3 "$REPO_ROOT/design/src/generate.py" || die "token generation failed — see contrast validation output above."

[[ -f "$REPO_ROOT/design/dist/apexis-light.colors" ]] || die "token output missing; generator produced nothing"

# --- Stage tokens into the overlay ---------------------------------------

step "Staging design tokens into overlay.d/30-apexis"
rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR/usr/share/color-schemes"

# Plasma colour schemes. These are the generated kcfg files, installed
# verbatim; Plasma picks them up from this path by filename.
install -m 0644 "$REPO_ROOT/design/dist/apexis-light.colors" \
  "$STAGE_DIR/usr/share/color-schemes/apexis-light.colors"
install -m 0644 "$REPO_ROOT/design/dist/apexis-dark.colors" \
  "$STAGE_DIR/usr/share/color-schemes/apexis-dark.colors"

step "Tokens staged:"
find "$STAGE_DIR" -type f -printf '    %P\n' | sort

# --- Build ----------------------------------------------------------------

mkdir -p "$WORK_DIR"

if podman image exists "$COSA_IMAGE" >/dev/null 2>&1; then
  podman pull --quiet "$COSA_IMAGE" >/dev/null || die "failed to pull $COSA_IMAGE"
fi

step "Building with coreos-assembler (this takes a while)"

podman run --rm -it --privileged \
  -v "${WORK_DIR}:/srv/ctx:Z" \
  -v "${CONFIG_DIR}:/srv/src/config:Z" \
  --name "${COSA_CONTAINER}-run" \
  --entrypoint /usr/bin/cosa \
  "$COSA_IMAGE" \
  build --config /srv/src/config || {
    die "cosa build failed. If this is the first run, expect the unverified
       values called out in build/README.md to need correcting."
  }

step "Done. Artifacts are in .build/builds/latest"
printf '    cosautil info --disk / run the image\n'