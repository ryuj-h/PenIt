"""Drawing data models."""

import time
from dataclasses import dataclass, field
from typing import List

from PyQt6.QtGui import QColor


@dataclass
class DrawPoint:
    """A single point in the drawing with timestamp for fading."""
    x: float
    y: float
    timestamp: float
    color: QColor
    size: float
    pressure: float = 1.0


@dataclass
class Stroke:
    """A complete stroke consisting of multiple points."""
    points: List[DrawPoint] = field(default_factory=list)
    creation_time: float = 0.0
    release_time: float = 0.0  # 0 = still drawing (mouse held)

    def __post_init__(self):
        if self.creation_time == 0.0:
            self.creation_time = time.time()
