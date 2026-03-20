"""Transparent overlay window for drawing on screen."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, QRect
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QPainterPath, QLinearGradient,
)

from penit.engine.smoothing import pulled_string_smooth, catmull_rom_to_bezier
from penit.ui.icons import create_cursor

if TYPE_CHECKING:
    from penit.engine.drawing_manager import DrawingManager
    from penit.platform.base import InputPassthrough, OverlaySetup


class OverlayWindow(QWidget):
    """Single-screen transparent overlay for drawing. One per monitor."""

    def __init__(
        self,
        screen,
        manager: DrawingManager,
        input_passthrough: InputPassthrough,
        overlay_setup: OverlaySetup,
    ):
        super().__init__()
        self._screen = screen
        self._manager = manager
        self._input_passthrough = input_passthrough
        self._overlay_setup = overlay_setup

        self._is_mouse_down = False
        self._pen_x = 0.0
        self._pen_y = 0.0
        self._string_len = 12.0  # pulled-string length in px
        self._prev_dirty = QRect()
        self._indicator_drawn = False

        # Apply platform-specific window flags
        flags = overlay_setup.get_window_flags()
        self.setWindowFlags(Qt.WindowType(flags))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        geo = screen.geometry()
        self.setGeometry(geo)
        self.show()
        self.setGeometry(geo)  # re-apply after show (WM may override)

        # Platform-specific post-show setup
        overlay_setup.post_show_setup(self)

        QTimer.singleShot(100, self._apply_initial_passthrough)

    def _apply_initial_passthrough(self):
        wid = int(self.winId())
        self._input_passthrough.set_passthrough(wid, True)

    def set_passthrough(self, passthrough: bool):
        wid = int(self.winId())
        self._input_passthrough.set_passthrough(wid, passthrough)
        if not passthrough:
            self.setCursor(create_cursor(self._manager.brush_size))
            self.activateWindow()
            self.raise_()
        else:
            self._is_mouse_down = False
            self.unsetCursor()
        self.request_full_update()

    # -- Input events --

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self._manager.is_drawing:
            self._manager.set_drawing_mode(False)

    def mousePressEvent(self, event):
        if not self._manager.is_drawing:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_mouse_down = True
            gpos = event.globalPosition().toPoint()
            gx = float(gpos.x())
            gy = float(gpos.y())
            self._pen_x = gx
            self._pen_y = gy
            self._manager.begin_stroke(gx, gy)

    def mouseMoveEvent(self, event):
        if not self._manager.is_drawing or not self._is_mouse_down:
            return
        gpos = event.globalPosition().toPoint()
        raw_x = float(gpos.x())
        raw_y = float(gpos.y())

        new_x, new_y, moved = pulled_string_smooth(
            self._pen_x, self._pen_y, raw_x, raw_y, self._string_len
        )
        if moved:
            self._pen_x = new_x
            self._pen_y = new_y
            self._manager.continue_stroke(self._pen_x, self._pen_y)

    def mouseReleaseEvent(self, event):
        if not self._manager.is_drawing:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_mouse_down = False
            self._manager.end_stroke()

    # -- Painting --

    def request_dirty_update(self, global_rect: QRect):
        """Schedule repaint for a region (global coords -> local coords)."""
        geo = self._screen.geometry()
        local = global_rect.translated(-geo.x(), -geo.y())
        combined = local.united(self._prev_dirty) if not self._prev_dirty.isNull() else local
        self._prev_dirty = local
        self.update(combined)

    def request_full_update(self):
        """Full repaint (for mode indicator toggle)."""
        self._prev_dirty = QRect()
        self._indicator_drawn = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        now = time.time()
        geo = self._screen.geometry()
        clip = event.rect()
        painter.setClipRect(clip)

        if self._manager.is_drawing and not self._indicator_drawn:
            self._draw_mode_indicator(painter)
            self._indicator_drawn = True
        elif not self._manager.is_drawing:
            self._indicator_drawn = False

        all_strokes = list(self._manager.strokes)
        cs = self._manager.current_stroke
        if cs and cs.points:
            all_strokes.append(cs)

        for stroke in all_strokes:
            self._draw_stroke(painter, stroke, now, geo)

        painter.end()

    def _draw_mode_indicator(self, painter: QPainter):
        rect = self.rect()
        g = 3
        for x1, y1, x2, y2, w, h, c0a, c1a in [
            (0, 0, 0, g*3, rect.width(), g*3, 60, 0),
            (0, rect.height()-g*3, 0, rect.height(), rect.width(), g*3, 0, 60),
        ]:
            grad = QLinearGradient(x1, y1, x2, y2)
            grad.setColorAt(0, QColor(0, 230, 230, c0a))
            grad.setColorAt(1, QColor(0, 230, 230, c1a))
            painter.fillRect(QRectF(x1, y1 if c0a else rect.height()-g*3, w, h), grad)
        for x1, y1, x2, y2, rx, ry, w, h, c0a, c1a in [
            (0, 0, g*3, 0, 0, 0, g*3, rect.height(), 60, 0),
            (rect.width()-g*3, 0, rect.width(), 0, rect.width()-g*3, 0, g*3, rect.height(), 0, 60),
        ]:
            grad = QLinearGradient(x1, y1, x2, y2)
            grad.setColorAt(0, QColor(0, 230, 230, c0a))
            grad.setColorAt(1, QColor(0, 230, 230, c1a))
            painter.fillRect(QRectF(rx, ry, w, h), grad)

    def _draw_stroke(self, painter, stroke, now, screen_geo):
        points = stroke.points
        n = len(points)
        if n == 0:
            return

        fade = self._manager.fade_duration
        fade_start = self._manager.fade_start_ratio
        inv_fade_tail = 1.0 / (1.0 - fade_start) if fade_start < 1.0 else 1.0
        ox = screen_geo.x()
        oy = screen_geo.y()

        # Still drawing (mouse held) -> full opacity, no fade
        released = stroke.release_time > 0
        if released:
            age_since_release = now - stroke.release_time
            if age_since_release >= fade:
                return
            r = age_since_release / fade
            stroke_alpha = 1.0 if r < fade_start else 1.0 - ((r - fade_start) * inv_fade_tail) ** 3
        else:
            stroke_alpha = 1.0

        if n == 1:
            p = points[0]
            c = QColor(p.color)
            c.setAlpha(int(stroke_alpha * 255))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(c)
            painter.drawEllipse(QRectF(p.x-ox - p.size/2, p.y-oy - p.size/2, p.size, p.size))
            return

        if n == 2:
            p0, p1 = points
            c = QColor(p1.color)
            c.setAlpha(int(stroke_alpha * 255))
            painter.setPen(QPen(c, p1.size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(int(p0.x-ox), int(p0.y-oy), int(p1.x-ox), int(p1.y-oy))
            return

        # Two-pass rendering: 1) black outline  2) colored fill
        a255 = int(stroke_alpha * 255)
        segments = []
        for i in range(n - 1):
            p1 = points[i]
            p2 = points[i+1]
            p0 = points[i-1] if i > 0 else p1
            p3 = points[i+2] if i+2 < n else p2

            cp1x, cp1y, cp2x, cp2y = catmull_rom_to_bezier(
                p0.x, p0.y, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)

            path = QPainterPath()
            path.moveTo(p1.x-ox, p1.y-oy)
            path.cubicTo(cp1x-ox, cp1y-oy, cp2x-ox, cp2y-oy, p2.x-ox, p2.y-oy)

            segments.append((path, p2))

        # Pass 1: black outline (thicker)
        for path, p2 in segments:
            sz = p2.size
            outline_sz = sz + 3
            bc = QColor(0, 0, 0, a255)

            painter.setPen(QPen(bc, outline_sz, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap, Qt.PenJoinStyle.RoundJoin))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

            half = outline_sz * 0.5
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bc)
            painter.drawEllipse(QRectF(p2.x-ox - half, p2.y-oy - half, outline_sz, outline_sz))

        # Pass 2: colored stroke on top
        for path, p2 in segments:
            c = QColor(p2.color)
            c.setAlpha(a255)
            sz = p2.size

            painter.setPen(QPen(c, sz, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap, Qt.PenJoinStyle.RoundJoin))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

            half = sz * 0.5
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(c)
            painter.drawEllipse(QRectF(p2.x-ox - half, p2.y-oy - half, sz, sz))

            # Glow
            if a255 > 100:
                gc = QColor(p2.color)
                gc.setAlpha(a255 >> 2)
                painter.setPen(QPen(gc, sz * 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap, Qt.PenJoinStyle.RoundJoin))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawPath(path)
