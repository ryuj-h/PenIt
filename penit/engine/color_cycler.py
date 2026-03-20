"""Premium color cycling using curated palette interpolation with organic noise."""

import math
import time
import colorsys
from typing import Tuple

from PyQt6.QtGui import QColor


class ColorCycler:
    """Premium color cycling using curated palette interpolation with organic noise.

    Instead of raw HSV sine cycling (cheap neon look), this uses:
    - Hand-picked luxury color stops (aurora / bioluminescence palette)
    - Smooth cubic Hermite interpolation between stops
    - Multi-octave organic noise for natural, non-repetitive movement
    - Controlled saturation (60-80%) and lightness for depth, not screaming neon
    """

    # Curated palette: deep ocean -> arctic teal -> soft violet -> warm cyan -> emerald
    # Each tuple is (H, S, L) in 0-1 range, designed for dark backgrounds
    PALETTES = {
        "aurora": [
            (185, 0.72, 0.62),  # arctic teal
            (210, 0.65, 0.58),  # steel blue
            (260, 0.50, 0.65),  # soft lavender
            (290, 0.45, 0.60),  # muted orchid
            (220, 0.60, 0.55),  # twilight blue
            (175, 0.68, 0.55),  # deep aqua
            (160, 0.55, 0.58),  # sage emerald
            (195, 0.75, 0.60),  # ocean cyan
        ],
        "ember": [
            (15,  0.75, 0.60),  # warm coral
            (35,  0.80, 0.62),  # amber gold
            (350, 0.55, 0.58),  # dusty rose
            (25,  0.70, 0.55),  # burnt sienna
            (45,  0.65, 0.65),  # champagne
            (5,   0.60, 0.52),  # deep terracotta
            (330, 0.45, 0.60),  # mauve
            (20,  0.72, 0.58),  # copper
        ],
        "neon_ink": [
            (190, 0.90, 0.65),  # electric cyan
            (270, 0.80, 0.68),  # vivid purple
            (320, 0.75, 0.65),  # hot magenta
            (210, 0.85, 0.60),  # neon blue
            (170, 0.82, 0.58),  # mint shock
            (250, 0.78, 0.62),  # ultraviolet
            (300, 0.70, 0.60),  # fuchsia
            (195, 0.88, 0.62),  # bright teal
        ],
        "sakura": [
            (340, 0.65, 0.72),  # cherry blossom
            (350, 0.50, 0.68),  # soft pink
            (320, 0.40, 0.65),  # plum mist
            (10,  0.55, 0.70),  # peach
            (335, 0.60, 0.60),  # rose
            (300, 0.35, 0.72),  # lilac
            (345, 0.55, 0.75),  # baby pink
            (15,  0.45, 0.68),  # apricot
        ],
        "ocean": [
            (200, 0.80, 0.50),  # deep ocean
            (190, 0.70, 0.55),  # tidal blue
            (215, 0.75, 0.45),  # midnight wave
            (180, 0.65, 0.58),  # seafoam
            (205, 0.60, 0.52),  # steel sea
            (170, 0.72, 0.50),  # dark aqua
            (195, 0.85, 0.48),  # abyss blue
            (185, 0.68, 0.55),  # marine
        ],
        "forest": [
            (120, 0.55, 0.45),  # deep forest
            (140, 0.50, 0.50),  # pine
            (100, 0.45, 0.52),  # moss
            (160, 0.60, 0.48),  # evergreen
            (80,  0.40, 0.55),  # olive
            (150, 0.55, 0.42),  # dark jade
            (130, 0.48, 0.50),  # fern
            (110, 0.52, 0.48),  # woodland
        ],
        "sunset": [
            (30,  0.85, 0.60),  # golden hour
            (15,  0.80, 0.55),  # tangerine
            (45,  0.75, 0.65),  # warm yellow
            (350, 0.70, 0.55),  # crimson dusk
            (0,   0.65, 0.50),  # blood red
            (20,  0.78, 0.58),  # burnt orange
            (40,  0.70, 0.60),  # amber
            (10,  0.72, 0.52),  # rust
        ],
        "galaxy": [
            (270, 0.70, 0.45),  # deep violet
            (250, 0.60, 0.50),  # nebula blue
            (290, 0.55, 0.42),  # dark purple
            (230, 0.65, 0.48),  # cosmic blue
            (310, 0.50, 0.45),  # dark magenta
            (260, 0.58, 0.40),  # void indigo
            (280, 0.62, 0.48),  # amethyst
            (240, 0.55, 0.45),  # starfield
        ],
        "pastel": [
            (200, 0.50, 0.78),  # baby blue
            (150, 0.45, 0.75),  # mint cream
            (280, 0.40, 0.78),  # lavender
            (30,  0.50, 0.80),  # peach cream
            (340, 0.45, 0.78),  # rose quartz
            (60,  0.40, 0.78),  # butter
            (180, 0.42, 0.76),  # aqua mist
            (220, 0.48, 0.77),  # periwinkle
        ],
        "ice": [
            (200, 0.40, 0.82),  # frost
            (210, 0.50, 0.78),  # glacier
            (190, 0.35, 0.85),  # white ice
            (220, 0.45, 0.75),  # frozen blue
            (195, 0.38, 0.80),  # silver frost
            (205, 0.42, 0.72),  # cold steel
            (185, 0.30, 0.88),  # diamond dust
            (215, 0.48, 0.76),  # polar
        ],
        "toxic": [
            (120, 0.90, 0.55),  # radioactive green
            (90,  0.85, 0.50),  # acid lime
            (150, 0.80, 0.48),  # toxic teal
            (75,  0.88, 0.52),  # venom
            (100, 0.82, 0.45),  # slime
            (140, 0.75, 0.50),  # biohazard
            (110, 0.92, 0.48),  # neon green
            (80,  0.78, 0.55),  # chartreuse
        ],
        "blood": [
            (0,   0.80, 0.40),  # deep crimson
            (350, 0.70, 0.35),  # dark blood
            (10,  0.75, 0.45),  # arterial red
            (340, 0.60, 0.38),  # wine
            (355, 0.72, 0.42),  # scarlet
            (5,   0.65, 0.35),  # maroon
            (345, 0.68, 0.40),  # garnet
            (15,  0.70, 0.48),  # vermilion
        ],
        "rainbow": [
            (0,   0.80, 0.58),  # red
            (30,  0.80, 0.58),  # orange
            (55,  0.80, 0.55),  # yellow
            (120, 0.70, 0.48),  # green
            (190, 0.75, 0.55),  # cyan
            (230, 0.70, 0.55),  # blue
            (270, 0.65, 0.55),  # indigo
            (310, 0.70, 0.55),  # violet
        ],
    }

    def __init__(self, palette_name: str = "aurora"):
        self.phase = 0.0
        self.speed = 0.015
        self._palette_name = palette_name
        self._palette = self.PALETTES[palette_name]
        self._noise_offsets = [
            time.time() * 0.1,
            time.time() * 0.1 + 100.0,
            time.time() * 0.1 + 200.0,
        ]

    @staticmethod
    def _smoothstep(t: float) -> float:
        """Hermite smoothstep for silky interpolation."""
        t = max(0.0, min(1.0, t))
        return t * t * (3.0 - 2.0 * t)

    @staticmethod
    def _organic_noise(phase: float) -> float:
        """Multi-octave pseudo-noise for organic, non-repetitive movement.
        Combines incommensurate sine frequencies so it never visibly loops."""
        return (
            math.sin(phase * 1.0) * 0.50 +
            math.sin(phase * 2.317) * 0.25 +
            math.sin(phase * 5.149) * 0.15 +
            math.sin(phase * 11.0237) * 0.10
        )

    def _lerp_color(self, t: float) -> Tuple[float, float, float]:
        """Interpolate along the palette ring at position t (0-1)."""
        n = len(self._palette)
        t_scaled = (t % 1.0) * n
        idx = int(t_scaled)
        frac = t_scaled - idx

        c0 = self._palette[idx % n]
        c1 = self._palette[(idx + 1) % n]

        # Cubic Hermite smoothstep for buttery transitions
        frac = self._smoothstep(frac)

        h = c0[0] + (c1[0] - c0[0]) * frac
        s = c0[1] + (c1[1] - c0[1]) * frac
        l = c0[2] + (c1[2] - c0[2]) * frac

        # Handle hue wrapping (e.g. 350 -> 10)
        if abs(c1[0] - c0[0]) > 180:
            if c1[0] > c0[0]:
                h = c0[0] + (c1[0] - c0[0] - 360) * frac
            else:
                h = c0[0] + (c1[0] - c0[0] + 360) * frac
            h = h % 360

        return (h, s, l)

    @staticmethod
    def _hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
        """Convert HSL (h in degrees, s/l in 0-1) to RGB (0-255)."""
        h_norm = (h % 360) / 360.0
        r, g, b = colorsys.hls_to_rgb(h_norm, l, s)
        return (int(r * 255), int(g * 255), int(b * 255))

    def next_color(self) -> QColor:
        """Get the next color -- smooth, organic, premium."""
        self.phase += self.speed

        # Organic noise drives position along palette
        noise = self._organic_noise(self.phase)
        palette_pos = (self.phase * 0.12 + noise * 0.08) % 1.0

        h, s, l = self._lerp_color(palette_pos)

        # Subtle organic modulation of saturation and lightness
        s_mod = self._organic_noise(self.phase * 1.7 + 50.0) * 0.06
        l_mod = self._organic_noise(self.phase * 1.3 + 150.0) * 0.04

        s = max(0.35, min(0.92, s + s_mod))
        l = max(0.45, min(0.72, l + l_mod))

        r, g, b = self._hsl_to_rgb(h, s, l)
        return QColor(r, g, b)

    def set_speed(self, speed: float):
        self.speed = speed

    def set_palette(self, name: str):
        if name in self.PALETTES:
            self._palette_name = name
            self._palette = self.PALETTES[name]
