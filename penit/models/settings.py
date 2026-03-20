"""Cross-platform settings management using QStandardPaths."""

import json
import shutil
from pathlib import Path

from PyQt6.QtCore import QStandardPaths


DEFAULTS = {
    "brush_size": 4,
    "fade_duration": 3.0,
    "color_speed": 0.015,
    "palette": "aurora",
}


def _config_dir() -> Path:
    """Get the cross-platform config directory for PenIt."""
    base = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppConfigLocation
    )
    return Path(base) / "penit"


def _legacy_config_dir() -> Path:
    """Legacy Linux-only config path."""
    return Path.home() / ".config" / "penit"


def _migrate_legacy_settings():
    """Migrate settings from legacy path to new cross-platform path if needed."""
    new_dir = _config_dir()
    legacy_dir = _legacy_config_dir()

    # Skip if same directory or new config already exists
    if new_dir == legacy_dir:
        return
    new_file = new_dir / "settings.json"
    if new_file.exists():
        return

    legacy_file = legacy_dir / "settings.json"
    if legacy_file.exists():
        new_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(legacy_file, new_file)


def load_settings() -> dict:
    """Load settings from disk, falling back to defaults."""
    _migrate_legacy_settings()
    config_file = _config_dir() / "settings.json"
    try:
        return {**DEFAULTS, **json.loads(config_file.read_text())}
    except Exception:
        return dict(DEFAULTS)


def save_settings(settings: dict):
    """Save settings to disk."""
    config_dir = _config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "settings.json"
    config_file.write_text(json.dumps(settings, indent=2))
