"""Stroke smoothing algorithms."""

import math
from typing import Tuple


def pulled_string_smooth(
    pen_x: float, pen_y: float,
    raw_x: float, raw_y: float,
    string_len: float
) -> Tuple[float, float, bool]:
    """Lazy Nezumi / Pulled-string smoothing.

    Pen is on a "string" of fixed length. Only moves when cursor
    pulls it beyond the string length, and only by the excess.

    Returns (new_pen_x, new_pen_y, moved).
    """
    dx = raw_x - pen_x
    dy = raw_y - pen_y
    dist = math.sqrt(dx * dx + dy * dy)

    if dist > string_len:
        pull = dist - string_len
        new_x = pen_x + dx / dist * pull
        new_y = pen_y + dy / dist * pull
        return new_x, new_y, True
    return pen_x, pen_y, False


def catmull_rom_to_bezier(
    p0x: float, p0y: float,
    p1x: float, p1y: float,
    p2x: float, p2y: float,
    p3x: float, p3y: float,
) -> Tuple[float, float, float, float]:
    """Convert Catmull-Rom control points to cubic Bezier control points.

    Returns (cp1x, cp1y, cp2x, cp2y).
    """
    t = 1.0 / 6.0
    return (
        p1x + t * (p2x - p0x), p1y + t * (p2y - p0y),
        p2x - t * (p3x - p1x), p2y - t * (p3y - p1y),
    )
