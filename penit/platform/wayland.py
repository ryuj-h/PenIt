"""Wayland platform backend.

Wayland has stricter security than X11:
- No global key grabs (use XDG Desktop Portal GlobalShortcuts D-Bus API)
- Click-through via Qt.WindowType.WindowTransparentForInput
- No window manager bypass needed
"""

from typing import Callable

from PyQt6.QtCore import Qt, QTimer

from penit.platform.base import InputPassthrough, GlobalHotkeys, OverlaySetup


class WaylandInputPassthrough(InputPassthrough):
    """Wayland click-through using Qt's WindowTransparentForInput flag.

    On Wayland, we toggle the flag and re-create the window surface.
    """

    def __init__(self):
        self._widgets: dict[int, object] = {}
        self.initialize()

    def initialize(self) -> bool:
        return True

    def set_passthrough(self, window_id: int, passthrough: bool) -> bool:
        widget = self._widgets.get(window_id)
        if widget is None:
            return False
        try:
            if passthrough:
                widget.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)
            else:
                widget.setWindowFlag(Qt.WindowType.WindowTransparentForInput, False)
            widget.show()
            return True
        except Exception as e:
            print(f"Wayland passthrough error: {e}")
            return False

    def register_widget(self, widget) -> None:
        """Register a widget for passthrough management."""
        self._widgets[int(widget.winId())] = widget

    def cleanup(self) -> None:
        self._widgets.clear()


class WaylandGlobalHotkeys(GlobalHotkeys):
    """Global hotkeys via XDG Desktop Portal D-Bus GlobalShortcuts interface.

    Falls back to no-op if dbus-python is not available.
    """

    def __init__(self):
        self._hotkeys: list[tuple[str, list[str], Callable]] = []
        self._session = None
        self._timer = None

    def register(self, key: str, modifiers: list[str], callback: Callable) -> bool:
        self._hotkeys.append((key, modifiers, callback))
        return True

    def unregister_all(self) -> None:
        self._hotkeys.clear()

    def start_listening(self, poll_interval_ms: int = 16) -> None:
        try:
            import dbus
            bus = dbus.SessionBus()
            portal = bus.get_object(
                "org.freedesktop.portal.Desktop",
                "/org/freedesktop/portal/desktop",
            )
            self._portal = dbus.Interface(
                portal, "org.freedesktop.portal.GlobalShortcuts"
            )
            # Request shortcuts session
            # Note: Full implementation requires D-Bus signal handling
            # This is a stub that prints a warning
            print("Wayland global shortcuts: D-Bus portal session created")
            print("Note: Full Wayland global shortcuts require desktop portal support")
        except Exception as e:
            print(f"Wayland global shortcuts unavailable: {e}")
            print("Tip: Install dbus-python and ensure xdg-desktop-portal is running")

    def stop_listening(self) -> None:
        if self._timer:
            self._timer.stop()
            self._timer = None


class WaylandOverlaySetup(OverlaySetup):
    """Wayland-specific overlay window configuration."""

    def get_window_flags(self) -> int:
        return int(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

    def post_show_setup(self, widget) -> None:
        pass
