"""PenItApp - Main application orchestrator."""

import sys

from PyQt6.QtWidgets import QApplication

from penit.platform import get_backend
from penit.engine.drawing_manager import DrawingManager
from penit.ui.tray import setup_tray


class PenItApp:
    """Main application controller.

    Orchestrates platform backends, drawing engine, and UI components.
    """

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("PenIt")
        self.app.setQuitOnLastWindowClosed(False)

        # Initialize platform backends
        input_pt, hotkeys, overlay_setup = get_backend()

        # Create the drawing manager (owns overlays and control panel)
        self.manager = DrawingManager(input_pt, hotkeys, overlay_setup)

        # Create system tray
        self.tray_icon = setup_tray(
            self.app, self.manager, self.manager.control_panel
        )

    def run(self) -> int:
        return self.app.exec()
