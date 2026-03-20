"""System tray icon and menu."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction

from penit.ui.icons import create_app_icon

if TYPE_CHECKING:
    from penit.engine.drawing_manager import DrawingManager
    from penit.ui.control_panel import ControlPanel


def setup_tray(
    app: QApplication,
    manager: DrawingManager,
    control_panel: ControlPanel,
) -> QSystemTrayIcon:
    """Create and configure the system tray icon."""
    icon = create_app_icon()
    app.setWindowIcon(icon)
    tray_icon = QSystemTrayIcon(icon, app)

    tray_menu = QMenu()

    toggle_action = QAction("\uadf8\ub9ac\uae30 \ud1a0\uae00 (Ctrl+Shift+D)", app)
    toggle_action.triggered.connect(
        lambda: manager.set_drawing_mode(not manager.is_drawing)
    )
    tray_menu.addAction(toggle_action)

    panel_action = QAction("\uc124\uc815 \ud328\ub110 \ubcf4\uae30", app)
    panel_action.triggered.connect(control_panel.show)
    tray_menu.addAction(panel_action)

    clear_action = QAction("\uc9c0\uc6b0\uae30 (Ctrl+Shift+C)", app)
    clear_action.triggered.connect(manager.clear_all)
    tray_menu.addAction(clear_action)

    tray_menu.addSeparator()

    quit_action = QAction("\uc885\ub8cc (Ctrl+Shift+Q)", app)
    quit_action.triggered.connect(QApplication.quit)
    tray_menu.addAction(quit_action)

    tray_icon.setContextMenu(tray_menu)
    tray_icon.setToolTip("PenIt - \ud654\uba74 \uadf8\ub9ac\uae30")
    tray_icon.show()

    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            manager.set_drawing_mode(not manager.is_drawing)
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            control_panel.show()
            control_panel.raise_()

    tray_icon.activated.connect(on_tray_activated)
    return tray_icon
