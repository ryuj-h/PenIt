"""Abstract base classes for platform-specific backends."""

from abc import ABC, abstractmethod
from typing import Callable


class InputPassthrough(ABC):
    """Handle click-through behavior for overlay windows."""

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the passthrough backend. Returns True if available."""
        ...

    @abstractmethod
    def set_passthrough(self, window_id: int, passthrough: bool) -> bool:
        """Set or unset click-through for the given window."""
        ...

    @abstractmethod
    def cleanup(self) -> None:
        """Release resources."""
        ...


class GlobalHotkeys(ABC):
    """Handle global keyboard shortcuts."""

    @abstractmethod
    def register(self, key: str, modifiers: list[str], callback: Callable) -> bool:
        """Register a global hotkey.

        Args:
            key: The key character (e.g., 'd', 'c', 'q').
            modifiers: List of modifier names (e.g., ['ctrl', 'shift']).
            callback: Function to call when the hotkey is pressed.
        """
        ...

    @abstractmethod
    def unregister_all(self) -> None:
        """Unregister all hotkeys."""
        ...

    @abstractmethod
    def start_listening(self, poll_interval_ms: int = 16) -> None:
        """Start listening for hotkey events."""
        ...

    @abstractmethod
    def stop_listening(self) -> None:
        """Stop listening for hotkey events."""
        ...


class OverlaySetup(ABC):
    """Handle platform-specific overlay window configuration."""

    @abstractmethod
    def get_window_flags(self) -> int:
        """Return the Qt window flags for the overlay."""
        ...

    @abstractmethod
    def post_show_setup(self, widget) -> None:
        """Perform any setup needed after the widget is shown."""
        ...
