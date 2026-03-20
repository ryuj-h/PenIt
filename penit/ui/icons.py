"""Icon and cursor generation for PenIt."""

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QIcon, QPixmap, QCursor,
)


def create_cursor(brush_size: int) -> QCursor:
    """Create a crosshair cursor sized to the brush."""
    size = max(brush_size * 2, 20)
    pixmap = QPixmap(size + 4, size + 4)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    center = (size + 4) / 2

    # Outer circle
    p.setPen(QPen(QColor(0, 255, 255, 150), 1.5))
    p.drawEllipse(QRectF(2, 2, size, size))

    # Center dot
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(0, 255, 255, 200))
    p.drawEllipse(QRectF(center - 1.5, center - 1.5, 3, 3))

    # Crosshair lines
    cl = min(size / 4, 6)
    p.setPen(QPen(QColor(0, 255, 255, 100), 1))
    p.drawLine(int(center), int(center - cl - 2), int(center), int(center - 2))
    p.drawLine(int(center), int(center + 2), int(center), int(center + cl + 2))
    p.drawLine(int(center - cl - 2), int(center), int(center - 2), int(center))
    p.drawLine(int(center + 2), int(center), int(center + cl + 2), int(center))
    p.end()
    return QCursor(pixmap, int(center), int(center))


def create_app_icon() -> QIcon:
    """Create the PenIt app icon."""
    icon_pixmap = QPixmap(32, 32)
    icon_pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(icon_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(0, 220, 220))
    painter.drawEllipse(4, 4, 24, 24)
    painter.setPen(QPen(QColor(20, 20, 30), 2))
    painter.drawLine(10, 22, 22, 10)
    painter.drawLine(22, 10, 20, 8)
    painter.end()
    return QIcon(icon_pixmap)
