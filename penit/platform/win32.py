"""Windows platform backend using Win32 API."""

import ctypes
import ctypes.wintypes
from typing import Callable

from PyQt6.QtCore import Qt, QTimer

from penit.platform.base import InputPassthrough, GlobalHotkeys, OverlaySetup


class Win32InputPassthrough(InputPassthrough):
    """Windows click-through using WS_EX_TRANSPARENT extended window style."""

    GWL_EXSTYLE = -20
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_LAYERED = 0x00080000

    def __init__(self):
        self._user32 = None
        self._available = False
        self.initialize()

    def initialize(self) -> bool:
        try:
            self._user32 = ctypes.windll.user32
            self._available = True
            return True
        except Exception:
            return False

    def set_passthrough(self, window_id: int, passthrough: bool) -> bool:
        if not self._available:
            return False
        try:
            hwnd = window_id
            style = self._user32.GetWindowLongW(hwnd, self.GWL_EXSTYLE)
            if passthrough:
                style |= self.WS_EX_TRANSPARENT | self.WS_EX_LAYERED
            else:
                style &= ~self.WS_EX_TRANSPARENT
            self._user32.SetWindowLongW(hwnd, self.GWL_EXSTYLE, style)
            return True
        except Exception as e:
            print(f"Win32 passthrough error: {e}")
            return False

    def cleanup(self) -> None:
        pass


class Win32GlobalHotkeys(GlobalHotkeys):
    """Windows global hotkeys using RegisterHotKey."""

    MOD_MAP = {
        "ctrl": 0x0002,   # MOD_CONTROL
        "shift": 0x0004,  # MOD_SHIFT
        "alt": 0x0001,    # MOD_ALT
        "win": 0x0008,    # MOD_WIN
    }
    WM_HOTKEY = 0x0312

    def __init__(self):
        self._hotkeys: list[tuple[int, Callable]] = []
        self._next_id = 1
        self._user32 = None
        self._timer = None

    def register(self, key: str, modifiers: list[str], callback: Callable) -> bool:
        try:
            if self._user32 is None:
                self._user32 = ctypes.windll.user32

            mod_flags = 0
            for m in modifiers:
                mod_flags |= self.MOD_MAP.get(m.lower(), 0)

            vk = ord(key.upper())
            hotkey_id = self._next_id
            self._next_id += 1

            result = self._user32.RegisterHotKey(None, hotkey_id, mod_flags, vk)
            if result:
                self._hotkeys.append((hotkey_id, callback))
                return True
            return False
        except Exception as e:
            print(f"Win32 hotkey registration error: {e}")
            return False

    def unregister_all(self) -> None:
        if self._user32:
            for hotkey_id, _ in self._hotkeys:
                self._user32.UnregisterHotKey(None, hotkey_id)
        self._hotkeys.clear()

    def start_listening(self, poll_interval_ms: int = 16) -> None:
        self._timer = QTimer()
        self._timer.timeout.connect(self._poll_events)
        self._timer.start(poll_interval_ms)

    def _poll_events(self):
        if not self._user32:
            return
        msg = ctypes.wintypes.MSG()
        while self._user32.PeekMessageW(
            ctypes.byref(msg), None, self.WM_HOTKEY, self.WM_HOTKEY, 0x0001
        ):
            hotkey_id = msg.wParam
            for hid, callback in self._hotkeys:
                if hid == hotkey_id:
                    callback()
                    break

    def stop_listening(self) -> None:
        if self._timer:
            self._timer.stop()
            self._timer = None
        self.unregister_all()


class Win32OverlaySetup(OverlaySetup):
    """Windows-specific overlay window configuration."""

    def get_window_flags(self) -> int:
        return int(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

    def post_show_setup(self, widget) -> None:
        pass
