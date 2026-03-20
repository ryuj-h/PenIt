"""macOS platform backend using PyObjC."""

from typing import Callable

from PyQt6.QtCore import Qt, QTimer

from penit.platform.base import InputPassthrough, GlobalHotkeys, OverlaySetup


class MacOSInputPassthrough(InputPassthrough):
    """macOS click-through using NSWindow.setIgnoresMouseEvents_."""

    def __init__(self):
        self._available = False
        self._widgets: dict[int, object] = {}
        self.initialize()

    def initialize(self) -> bool:
        try:
            import AppKit  # noqa: F401
            self._available = True
            return True
        except ImportError:
            print("pyobjc not available, macOS passthrough disabled")
            return False

    def set_passthrough(self, window_id: int, passthrough: bool) -> bool:
        if not self._available:
            return False
        try:
            import AppKit
            widget = self._widgets.get(window_id)
            if widget is None:
                return False
            # Get the NSWindow from the QWidget
            nsview = int(widget.winId())
            # Use the Objective-C bridge to get NSWindow
            from Cocoa import NSApp
            for window in NSApp.windows():
                if window.windowNumber() == nsview:
                    window.setIgnoresMouseEvents_(passthrough)
                    if not passthrough:
                        window.setLevel_(1000)  # NSScreenSaverWindowLevel-like
                    return True
            return False
        except Exception as e:
            print(f"macOS passthrough error: {e}")
            return False

    def register_widget(self, widget) -> None:
        """Register a widget for passthrough management."""
        self._widgets[int(widget.winId())] = widget

    def cleanup(self) -> None:
        self._widgets.clear()


class MacOSGlobalHotkeys(GlobalHotkeys):
    """macOS global hotkeys using CGEventTap or Carbon API."""

    def __init__(self):
        self._hotkeys: list[tuple[str, list[str], Callable]] = []
        self._tap = None
        self._timer = None

    def register(self, key: str, modifiers: list[str], callback: Callable) -> bool:
        self._hotkeys.append((key, modifiers, callback))
        return True

    def unregister_all(self) -> None:
        self._hotkeys.clear()

    def start_listening(self, poll_interval_ms: int = 16) -> None:
        try:
            import Quartz
            from Quartz import (
                CGEventTapCreate, kCGSessionEventTap,
                kCGHeadInsertEventTap, kCGEventTapOptionDefault,
                CGEventTapEnable, CFMachPortCreateRunLoopSource,
                CFRunLoopGetCurrent, CFRunLoopAddSource,
                kCFRunLoopCommonModes, CGEventMaskBit, kCGEventKeyDown,
            )

            modifier_map = {
                "ctrl": Quartz.kCGEventFlagMaskControl,
                "shift": Quartz.kCGEventFlagMaskShift,
                "alt": Quartz.kCGEventFlagMaskAlternate,
                "cmd": Quartz.kCGEventFlagMaskCommand,
            }

            key_map = {chr(i): i for i in range(256)}

            def callback(proxy, type_, event, refcon):
                flags = Quartz.CGEventGetFlags(event)
                keycode = Quartz.CGEventGetIntegerValueField(
                    event, Quartz.kCGKeyboardEventKeycode
                )
                for key, modifiers, cb in self._hotkeys:
                    required_flags = 0
                    for m in modifiers:
                        required_flags |= modifier_map.get(m.lower(), 0)
                    if (flags & required_flags) == required_flags:
                        cb()
                return event

            event_mask = CGEventMaskBit(kCGEventKeyDown)
            self._tap = CGEventTapCreate(
                kCGSessionEventTap,
                kCGHeadInsertEventTap,
                kCGEventTapOptionDefault,
                event_mask,
                callback,
                None,
            )
            if self._tap:
                source = CFMachPortCreateRunLoopSource(None, self._tap, 0)
                CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)
                CGEventTapEnable(self._tap, True)
        except Exception as e:
            print(f"macOS global shortcuts unavailable: {e}")
            print("Tip: Install pyobjc-framework-Quartz and grant Accessibility permissions")

    def stop_listening(self) -> None:
        if self._tap:
            try:
                from Quartz import CGEventTapEnable
                CGEventTapEnable(self._tap, False)
            except Exception:
                pass
            self._tap = None


class MacOSOverlaySetup(OverlaySetup):
    """macOS-specific overlay window configuration."""

    def get_window_flags(self) -> int:
        return int(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

    def post_show_setup(self, widget) -> None:
        try:
            from AppKit import NSApp
            for window in NSApp.windows():
                if window.windowNumber() == int(widget.winId()):
                    window.setLevel_(1000)
                    window.setCollectionBehavior_(
                        1 << 0 | 1 << 4  # canJoinAllSpaces | fullScreenAuxiliary
                    )
                    break
        except Exception:
            pass
