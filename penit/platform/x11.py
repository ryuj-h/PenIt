"""X11 platform backend using python-xlib and libXfixes."""

import ctypes
import ctypes.util
from typing import Callable

from PyQt6.QtCore import Qt, QTimer

from penit.platform.base import InputPassthrough, GlobalHotkeys, OverlaySetup


class X11InputPassthrough(InputPassthrough):
    """Handle X11 input shape to make window click-through on Linux/X11."""

    SHAPE_INPUT = 2  # ShapeInput kind

    def __init__(self):
        self._xlib = None
        self._xfixes = None
        self._display = None
        self._available = False
        self.initialize()

    def initialize(self) -> bool:
        try:
            x11_path = ctypes.util.find_library('X11')
            xfixes_path = ctypes.util.find_library('Xfixes')
            if not x11_path or not xfixes_path:
                return False

            self._xlib = ctypes.cdll.LoadLibrary(x11_path)
            self._xfixes = ctypes.cdll.LoadLibrary(xfixes_path)

            self._xlib.XOpenDisplay.restype = ctypes.c_void_p
            self._xlib.XOpenDisplay.argtypes = [ctypes.c_char_p]

            self._display = self._xlib.XOpenDisplay(None)
            if not self._display:
                return False

            self._xfixes.XFixesCreateRegion.restype = ctypes.c_ulong
            self._xfixes.XFixesCreateRegion.argtypes = [
                ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int
            ]
            self._xfixes.XFixesSetWindowShapeRegion.argtypes = [
                ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int,
                ctypes.c_int, ctypes.c_int, ctypes.c_ulong
            ]
            self._xfixes.XFixesDestroyRegion.argtypes = [
                ctypes.c_void_p, ctypes.c_ulong
            ]
            self._xlib.XFlush.argtypes = [ctypes.c_void_p]

            self._available = True
            return True
        except Exception as e:
            print(f"X11 input passthrough init failed: {e}")
            return False

    def set_passthrough(self, window_id: int, passthrough: bool) -> bool:
        if not self._available:
            return False
        try:
            if passthrough:
                region = self._xfixes.XFixesCreateRegion(
                    self._display, None, 0
                )
                self._xfixes.XFixesSetWindowShapeRegion(
                    self._display, window_id, self.SHAPE_INPUT, 0, 0, region
                )
                self._xfixes.XFixesDestroyRegion(self._display, region)
            else:
                self._xfixes.XFixesSetWindowShapeRegion(
                    self._display, window_id, self.SHAPE_INPUT, 0, 0, 0
                )
            self._xlib.XFlush(self._display)
            return True
        except Exception as e:
            print(f"X11 passthrough error: {e}")
            return False

    def cleanup(self) -> None:
        pass


class X11GlobalHotkeys(GlobalHotkeys):
    """Global hotkeys via X11 XGrabKey on root window."""

    def __init__(self):
        self._hotkeys: list[tuple[str, list[str], Callable]] = []
        self._grab_display = None
        self._grab_timer = None
        self._keycode_map: dict[int, Callable] = {}

    def register(self, key: str, modifiers: list[str], callback: Callable) -> bool:
        self._hotkeys.append((key, modifiers, callback))
        return True

    def unregister_all(self) -> None:
        self._hotkeys.clear()
        self._keycode_map.clear()

    def start_listening(self, poll_interval_ms: int = 16) -> None:
        try:
            import Xlib
            import Xlib.XK
            from Xlib import X, display as xdisplay
        except ImportError:
            print("python-xlib not available, global hotkeys disabled")
            return

        self._grab_display = xdisplay.Display()
        root = self._grab_display.screen().root

        ctrl_shift = X.ControlMask | X.ShiftMask
        num_lock = Xlib.X.Mod2Mask
        caps_lock = X.LockMask
        lock_combos = [0, num_lock, caps_lock, num_lock | caps_lock]

        for key, modifiers, callback in self._hotkeys:
            kc = self._grab_display.keysym_to_keycode(
                Xlib.XK.string_to_keysym(key))
            self._keycode_map[kc] = callback
            for extra in lock_combos:
                root.grab_key(kc, ctrl_shift | extra,
                              True, X.GrabModeAsync, X.GrabModeAsync)

        self._grab_display.flush()
        root.change_attributes(event_mask=X.KeyPressMask)
        self._grab_display.flush()

        self._grab_timer = QTimer()
        self._grab_timer.timeout.connect(self._poll_events)
        self._grab_timer.start(poll_interval_ms)

    def _poll_events(self):
        from Xlib import X
        while self._grab_display.pending_events():
            ev = self._grab_display.next_event()
            if ev.type == X.KeyPress:
                cb = self._keycode_map.get(ev.detail)
                if cb:
                    cb()

    def stop_listening(self) -> None:
        if self._grab_timer:
            self._grab_timer.stop()
            self._grab_timer = None


class X11OverlaySetup(OverlaySetup):
    """X11-specific overlay window configuration."""

    def get_window_flags(self) -> int:
        return int(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.X11BypassWindowManagerHint
        )

    def post_show_setup(self, widget) -> None:
        pass
