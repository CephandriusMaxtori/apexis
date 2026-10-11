# SPDX-FileCopyrightText: 2026 Nolan Bragan
# SPDX-License-Identifier: MPL-2.0

"""Colour maths for the Apexis design system.

Everything is authored in OKLCH because perceptual lightness is the axis we
actually reason about — "is this dark or light" is a far better question than
"which of these two hex codes looks darker". sRGB hex is only ever an output
format, never the source of truth.

Colour space conversions follow Björn Ottosson's OKLab derivation. Chroma is
reduced (never lightness or hue) when a colour falls outside the sRGB gamut, so
that a colour keeps its identity as it moves between light and dark ramps.
"""

from __future__ import annotations

import math
from typing import Iterable

# ---------------------------------------------------------------------------
# sRGB transfer function
# ---------------------------------------------------------------------------


def srgb_to_linear(c: float) -> float:
    """Decode an sRGB channel (0..1) to linear light."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    """Encode a linear-light channel to sRGB (0..1)."""
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


# ---------------------------------------------------------------------------
# OKLab / OKLCH
# ---------------------------------------------------------------------------


def linear_srgb_to_oklab(r: float, g: float, b: float) -> tuple[float, float, float]:
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

    l_, m_, s_ = math.cbrt(l), math.cbrt(m), math.cbrt(s)

    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_linear_srgb(L: float, a: float, b: float) -> tuple[float, float, float]:
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l, m, s = l_ * l_ * l_, m_ * m_ * m_, s_ * s_ * s_

    return (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def oklch_to_oklab(L: float, C: float, h: float) -> tuple[float, float, float]:
    rad = math.radians(h)
    return L, C * math.cos(rad), C * math.sin(rad)


def oklab_to_oklch(L: float, a: float, b: float) -> tuple[float, float, float]:
    C = math.hypot(a, b)
    if C < 1e-7:
        return L, 0.0, 0.0
    h = math.degrees(math.atan2(b, a)) % 360.0
    return L, C, h


# ---------------------------------------------------------------------------
# Gamut handling
# ---------------------------------------------------------------------------


def _in_gamut(rgb: tuple[float, float, float], eps: float = 1e-4) -> bool:
    return all(-eps <= c <= 1.0 + eps for c in rgb)


def gamut_map(L: float, C: float, h: float) -> tuple[float, float, float]:
    """Return sRGB (0..1 per channel) for an OKLCH colour, in gamut.

    Reduces chroma by bisection until the colour fits. Lightness and hue are
    held fixed — clipping those instead is what makes a system drift between
    themes, because a colour ends up meaning something slightly different from
    the token that named it.
    """
    if L <= 0:
        return (0.0, 0.0, 0.0)
    if L >= 1:
        return (1.0, 1.0, 1.0)

    direct = oklab_to_linear_srgb(*oklch_to_oklab(L, C, h))
    if _in_gamut(direct):
        return tuple(min(1.0, max(0.0, c)) for c in direct)

    lo, hi = 0.0, C
    for _ in range(40):
        mid = (lo + hi) / 2
        if _in_gamut(oklab_to_linear_srgb(*oklch_to_oklab(L, mid, h))):
            lo = mid
        else:
            hi = mid

    rgb = oklab_to_linear_srgb(*oklch_to_oklab(L, lo, h))
    return tuple(min(1.0, max(0.0, c)) for c in rgb)


def to_hex(rgb: tuple[float, float, float]) -> str:
    """Format *linear* RGB as hex, applying the sRGB encoding transfer.

    Use this after `gamut_map` / `oklab_to_linear_srgb`. If you already hold
    sRGB values (e.g. from `from_hex`), use `hex_from_srgb` instead — running
    the transfer twice washes colours out and quietly destroys contrast.
    """
    return "#" + "".join(f"{round(linear_to_srgb(c) * 255):02x}" for c in rgb)


def hex_from_srgb(rgb: tuple[float, float, float]) -> str:
    """Format sRGB (0..1) channels as hex. No transfer applied."""
    return "#" + "".join(f"{round(c * 255):02x}" for c in rgb)


def from_hex(value: str) -> tuple[float, float, float]:
    v = value.lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6:
        raise ValueError(f"bad hex colour: {value!r}")
    return tuple(int(v[i : i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def hex_to_oklch(value: str) -> tuple[float, float, float]:
    r, g, b = (srgb_to_linear(c) for c in from_hex(value))
    return oklab_to_oklch(*linear_srgb_to_oklab(r, g, b))


def oklch_to_hex(L: float, C: float, h: float) -> str:
    return to_hex(gamut_map(L, C, h))


def oklch_to_srgb(L: float, C: float, h: float) -> tuple[float, float, float]:
    """Gamut-mapped OKLCH to *sRGB* (0..1) — the form every consumer wants.

    `gamut_map` returns linear light; this is the explicit step to sRGB, so
    callers never have to remember which space they are holding.
    """
    return tuple(linear_to_srgb(c) for c in gamut_map(L, C, h))  # type: ignore[return-value]


def with_alpha(rgb: tuple[float, float, float], alpha: float) -> str:
    """Format *sRGB* (0..1) channels as `rgba()`. See `to_hex` for the caveat."""
    r, g, b = (round(c * 255) for c in rgb)
    return f"rgba({r}, {g}, {b}, {round(alpha, 4)})"


# ---------------------------------------------------------------------------
# Relative luminance and contrast (WCAG 2.1)
# ---------------------------------------------------------------------------


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = (srgb_to_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    la, lb = relative_luminance(a), relative_luminance(b)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def mix(a: tuple[float, float, float], b: tuple[float, float, float], t: float) -> tuple[float, float, float]:
    """Blend two sRGB colours in linear light (matches what compositors do)."""
    return (
        srgb_to_linear(a[0]) * (1 - t) + srgb_to_linear(b[0]) * t,
        srgb_to_linear(a[1]) * (1 - t) + srgb_to_linear(b[1]) * t,
        srgb_to_linear(a[2]) * (1 - t) + srgb_to_linear(b[2]) * t,
    )


# ---------------------------------------------------------------------------
# Ramp generation
# ---------------------------------------------------------------------------

# Target perceptual lightness per step. Chosen so consecutive steps stay
# distinguishable by eye without the ends looking washed out.
STEP_LIGHTNESS: dict[int, float] = {
    50: 0.977,
    100: 0.954,
    200: 0.912,
    300: 0.854,
    400: 0.775,
    500: 0.681,
    600: 0.588,
    700: 0.505,
    800: 0.428,
    900: 0.359,
    950: 0.259,
}

# Chroma is strongest mid-ramp. Pure hue is reserved for the steps people
# actually use as accents; the pale tints stay near-neutral so surfaces built
# from them do not read as coloured.
STEP_CHROMA_SCALE: dict[int, float] = {
    50: 0.08,
    100: 0.16,
    200: 0.32,
    300: 0.52,
    400: 0.76,
    500: 1.00,
    600: 0.92,
    700: 0.74,
    800: 0.54,
    900: 0.38,
    950: 0.20,
}

RAMP_STEPS: Iterable[int] = STEP_LIGHTNESS.keys()


def build_ramp(hue: float, chroma: float) -> dict[int, str]:
    """Generate a full tonal ramp for a hue at a given peak chroma."""
    return {
        step: oklch_to_hex(STEP_LIGHTNESS[step], chroma * STEP_CHROMA_SCALE[step], hue)
        for step in RAMP_STEPS
    }