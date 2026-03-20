"""Drawing state management and tick logic."""

from __future__ import annotations

import time
from typing import List, TYPE_CHECKING

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer, QRect

from penit.models.drawing import DrawPoint, Stroke
from penit.models.settings import load_settings, save_settings
from penit.engine.color_cycler import ColorCycler
from penit.ui.icons import create_cursor
from penit.ui.control_panel import ControlPanel

if TYPE_CHECKING:
    from penit.ui.overlay_window import OverlayWindow
    from penit.platform.base import InputPassthrough, GlobalHotkeys, OverlaySetup


class DrawingManager:
    """Central manager: shared state, controls, shortcuts. Owns per-screen overlays."""

    def __init__(
        self,
        input_passthrough: InputPassthrough,
        global_hotkeys: GlobalHotkeys,
        overlay_setup: OverlaySetup,
    ):
        self.is_drawing = False
        self.strokes: List[Stroke] = []
        self.current_stroke: Stroke | None = None
        self.fade_start_ratio = 0.4

        # Load persisted settings
        cfg = load_settings()
        self.brush_size = cfg["brush_size"]
        self.fade_duration = cfg["fade_duration"]
        self.color_cycler = ColorCycler(palette_name=cfg["palette"])
        self.color_cycler.set_speed(cfg["color_speed"])

        self._input_passthrough = input_passthrough
        self._overlay_setup = overlay_setup
        self._global_hotkeys = global_hotkeys

        # Create an overlay for each screen
        from penit.ui.overlay_window import OverlayWindow
        self._overlays: List[OverlayWindow] = []
        for screen in QApplication.screens():
            ov = OverlayWindow(screen, self, input_passthrough, overlay_setup)
            self._overlays.append(ov)

        # Handle screens added/removed at runtime
        QApplication.instance().screenAdded.connect(self._on_screen_added)
        QApplication.instance().screenRemoved.connect(self._on_screen_removed)

        # Tick timer -- ~166Hz for high-refresh monitors
        self._timer = QTimer()
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.timeout.connect(self._tick)
        self._timer.start(6)

        # Control panel -- apply saved settings to UI
        self._control_panel = ControlPanel()
        self._control_panel.setWindowTitle("PenIt")
        self._control_panel.brush_slider.setValue(self.brush_size)
        self._control_panel.fade_slider.setValue(int(self.fade_duration * 10))
        self._control_panel.color_slider.setValue(int(self.color_cycler.speed * 1000))
        self._control_panel._on_palette_change(cfg["palette"])

        self._control_panel.drawing_toggled.connect(self.set_drawing_mode)
        self._control_panel.clear_requested.connect(self.clear_all)
        self._control_panel.brush_size_changed.connect(self._set_brush_size)
        self._control_panel.fade_duration_changed.connect(self._set_fade_duration)
        self._control_panel.color_speed_changed.connect(self._set_color_speed)
        self._control_panel.palette_changed.connect(self._set_palette)
        self._control_panel.quit_requested.connect(lambda: QApplication.quit())

        screen = QApplication.primaryScreen().geometry()
        self._control_panel.move(screen.right() - 320, 60)
        self._control_panel.resize(280, 400)
        self._control_panel.show()

        # Global key hooks
        self._setup_shortcuts()

    @property
    def control_panel(self) -> ControlPanel:
        return self._control_panel

    def _on_screen_added(self, screen):
        from penit.ui.overlay_window import OverlayWindow
        ov = OverlayWindow(screen, self, self._input_passthrough, self._overlay_setup)
        self._overlays.append(ov)
        if self.is_drawing:
            ov.set_passthrough(False)

    def _on_screen_removed(self, screen):
        self._overlays = [o for o in self._overlays if o._screen != screen]

    def _setup_shortcuts(self):
        """Register global hotkeys via platform backend."""
        self._global_hotkeys.register("d", ["ctrl", "shift"], self._toggle_drawing)
        self._global_hotkeys.register("c", ["ctrl", "shift"], self.clear_all)
        self._global_hotkeys.register("q", ["ctrl", "shift"], lambda: QApplication.quit())
        self._global_hotkeys.start_listening()

    def _toggle_drawing(self):
        self.set_drawing_mode(not self.is_drawing)

    # -- Drawing state --

    def set_drawing_mode(self, active: bool):
        self.is_drawing = active
        self._control_panel.set_drawing_state(active)
        for ov in self._overlays:
            ov.set_passthrough(not active)

    def clear_all(self):
        self.strokes.clear()
        self.current_stroke = None
        for ov in self._overlays:
            ov.update()

    def begin_stroke(self, gx: float, gy: float):
        self.current_stroke = Stroke()
        self._add_point(gx, gy)

    def continue_stroke(self, gx: float, gy: float):
        if self.current_stroke and self.current_stroke.points:
            last = self.current_stroke.points[-1]
            dx = gx - last.x
            dy = gy - last.y
            if dx*dx + dy*dy < 2.0:
                return
        self._add_point(gx, gy)

    def end_stroke(self):
        if self.current_stroke and self.current_stroke.points:
            self.current_stroke.release_time = time.time()
            self.strokes.append(self.current_stroke)
        self.current_stroke = None

    def _add_point(self, x: float, y: float):
        if self.current_stroke is None:
            return
        self.current_stroke.points.append(DrawPoint(
            x=x, y=y, timestamp=time.time(),
            color=self.color_cycler.next_color(), size=self.brush_size))

    def _save_settings(self):
        save_settings({
            "brush_size": self.brush_size,
            "fade_duration": self.fade_duration,
            "color_speed": self.color_cycler.speed,
            "palette": self.color_cycler._palette_name,
        })

    def _set_brush_size(self, size: int):
        self.brush_size = size
        self._save_settings()
        if self.is_drawing:
            cursor = create_cursor(self.brush_size)
            for ov in self._overlays:
                ov.setCursor(cursor)

    def _set_fade_duration(self, d: float):
        self.fade_duration = d
        self._save_settings()

    def _set_color_speed(self, s: float):
        self.color_cycler.set_speed(s)
        self._save_settings()

    def _set_palette(self, name: str):
        self.color_cycler.set_palette(name)
        self._save_settings()

    def _calc_dirty_rect(self) -> QRect:
        """Compute global bounding box of all visible content."""
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        margin = self.brush_size * 3

        all_strokes = self.strokes
        if self.current_stroke and self.current_stroke.points:
            all_strokes = list(self.strokes) + [self.current_stroke]

        for stroke in all_strokes:
            for p in stroke.points:
                if p.x - margin < min_x:
                    min_x = p.x - margin
                if p.y - margin < min_y:
                    min_y = p.y - margin
                if p.x + margin > max_x:
                    max_x = p.x + margin
                if p.y + margin > max_y:
                    max_y = p.y + margin

        if min_x > max_x:
            return QRect()
        return QRect(int(min_x), int(min_y),
                     int(max_x - min_x) + 1, int(max_y - min_y) + 1)

    def _tick(self):
        now = time.time()
        fade = self.fade_duration
        old_len = len(self.strokes)
        self.strokes[:] = [s for s in self.strokes
                           if s.points and (s.release_time == 0 or now - s.release_time < fade)]
        has_content = bool(self.strokes) or self.current_stroke is not None
        something_expired = old_len > len(self.strokes)

        if has_content or something_expired:
            dirty = self._calc_dirty_rect()
            if dirty.isNull():
                for ov in self._overlays:
                    ov.request_full_update()
            else:
                for ov in self._overlays:
                    ov.request_dirty_update(dirty)
