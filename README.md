<p align="center">
  <img src="assets/banner.png" alt="PenIt" width="700">
</p>

<p align="center">
  <b>Draw on your screen. Anywhere.</b><br>
  <sub>Full-screen transparent overlay drawing app with fading strokes and color palettes</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyQt6-6.5+-41CD52?logo=qt&logoColor=white" alt="PyQt6">
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/version-2.0.0-00e5e5" alt="Version">
</p>

---

<p align="center">
  <img src="assets/panel_crop.png" alt="Control Panel" width="250">
</p>

## Install

```bash
pip install -e ".[x11]"    # Linux X11
pip install -e ".[wayland]" # Linux Wayland
pip install -e .            # Windows / macOS
```

## Run

```bash
penit
```

## Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+Shift+D` | Toggle drawing |
| `Ctrl+Shift+C` | Clear screen |
| `Ctrl+Shift+Q` | Quit |
| `Esc` | Stop drawing |

## Features

- Transparent full-screen overlay
- Strokes fade out over time
- 13 color palettes (aurora, neon, sakura, galaxy...)
- Pulled-string smoothing (Lazy Nezumi style)
- Multi-monitor support
- System tray integration
- Cross-platform (Linux X11/Wayland, Windows, macOS)

## License

MIT
