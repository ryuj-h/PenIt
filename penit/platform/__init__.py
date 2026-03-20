"""Platform detection and backend selection."""

import sys
import os


def detect_platform() -> str:
    """Detect the current platform and return a backend identifier."""
    if sys.platform == "win32":
        return "win32"
    if sys.platform == "darwin":
        return "macos"
    # Linux: check Wayland vs X11
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if session_type == "wayland" or os.environ.get("WAYLAND_DISPLAY"):
        return "wayland"
    return "x11"


def get_backend():
    """Return the platform backend tuple (InputPassthrough, GlobalHotkeys, OverlaySetup)."""
    platform = detect_platform()

    if platform == "x11":
        from penit.platform.x11 import X11InputPassthrough, X11GlobalHotkeys, X11OverlaySetup
        return X11InputPassthrough(), X11GlobalHotkeys(), X11OverlaySetup()
    elif platform == "wayland":
        from penit.platform.wayland import WaylandInputPassthrough, WaylandGlobalHotkeys, WaylandOverlaySetup
        return WaylandInputPassthrough(), WaylandGlobalHotkeys(), WaylandOverlaySetup()
    elif platform == "win32":
        from penit.platform.win32 import Win32InputPassthrough, Win32GlobalHotkeys, Win32OverlaySetup
        return Win32InputPassthrough(), Win32GlobalHotkeys(), Win32OverlaySetup()
    elif platform == "macos":
        from penit.platform.macos import MacOSInputPassthrough, MacOSGlobalHotkeys, MacOSOverlaySetup
        return MacOSInputPassthrough(), MacOSGlobalHotkeys(), MacOSOverlaySetup()
    else:
        raise RuntimeError(f"Unsupported platform: {platform}")
