"""Floating control panel for drawing settings."""

from PyQt6.QtWidgets import (
    QWidget, QSlider, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal

from penit.engine.color_cycler import ColorCycler
from penit.ui.styles import CONTROL_PANEL_STYLE


class ControlPanel(QWidget):
    """Floating control panel for drawing settings."""

    drawing_toggled = pyqtSignal(bool)
    clear_requested = pyqtSignal()
    brush_size_changed = pyqtSignal(int)
    fade_duration_changed = pyqtSignal(float)
    color_speed_changed = pyqtSignal(float)
    palette_changed = pyqtSignal(str)
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None
        self._is_drawing = False
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Container frame
        self.container = QFrame()
        self.container.setObjectName("container")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(16, 12, 16, 16)
        container_layout.setSpacing(8)

        # Title bar
        title_bar = QHBoxLayout()
        self._title_label = QLabel("\U0001f58a PenIt")
        self._title_label.setObjectName("title")
        title_bar.addWidget(self._title_label)
        title_bar.addStretch()

        minimize_btn = QPushButton("\u2500")
        minimize_btn.setObjectName("closeBtn")
        minimize_btn.setFixedSize(24, 24)
        minimize_btn.clicked.connect(self.showMinimized)
        title_bar.addWidget(minimize_btn)

        close_btn = QPushButton("\u2715")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.hide)
        title_bar.addWidget(close_btn)
        container_layout.addLayout(title_bar)

        # Separator
        self._separator = QFrame()
        self._separator.setFrameShape(QFrame.Shape.HLine)
        self._separator.setObjectName("separator")
        container_layout.addWidget(self._separator)

        # Body widget
        self._body = QWidget()
        body_layout = QVBoxLayout(self._body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(8)
        self._body_layout = body_layout

        # Toggle button
        self.toggle_btn = QPushButton("\u25b6 \uadf8\ub9ac\uae30 \uc2dc\uc791  (Ctrl+Shift+D)")
        self.toggle_btn.setObjectName("toggleBtn")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setMinimumHeight(40)
        self.toggle_btn.clicked.connect(self._on_toggle)
        body_layout.addWidget(self.toggle_btn)

        # Brush size slider
        brush_layout = QVBoxLayout()
        brush_label = QHBoxLayout()
        lbl = QLabel("\ube0c\ub7ec\uc2dc \ud06c\uae30")
        lbl.setObjectName("sliderLabel")
        self.brush_value_label = QLabel("4")
        self.brush_value_label.setObjectName("valueLabel")
        brush_label.addWidget(lbl)
        brush_label.addStretch()
        brush_label.addWidget(self.brush_value_label)
        brush_layout.addLayout(brush_label)

        self.brush_slider = QSlider(Qt.Orientation.Horizontal)
        self.brush_slider.setRange(1, 30)
        self.brush_slider.setValue(4)
        self.brush_slider.valueChanged.connect(self._on_brush_change)
        brush_layout.addWidget(self.brush_slider)
        body_layout.addLayout(brush_layout)

        # Fade duration slider
        fade_layout = QVBoxLayout()
        fade_label = QHBoxLayout()
        lbl2 = QLabel("\uc0ac\ub77c\uc9c0\ub294 \uc2dc\uac04")
        lbl2.setObjectName("sliderLabel")
        self.fade_value_label = QLabel("3.0\ucd08")
        self.fade_value_label.setObjectName("valueLabel")
        fade_label.addWidget(lbl2)
        fade_label.addStretch()
        fade_label.addWidget(self.fade_value_label)
        fade_layout.addLayout(fade_label)

        self.fade_slider = QSlider(Qt.Orientation.Horizontal)
        self.fade_slider.setRange(5, 100)
        self.fade_slider.setValue(30)
        self.fade_slider.valueChanged.connect(self._on_fade_change)
        fade_layout.addWidget(self.fade_slider)
        body_layout.addLayout(fade_layout)

        # Color speed slider
        color_layout = QVBoxLayout()
        color_label = QHBoxLayout()
        lbl3 = QLabel("\uc0c9\uc0c1 \ubcc0\ud654 \uc18d\ub3c4")
        lbl3.setObjectName("sliderLabel")
        self.color_value_label = QLabel("\ubcf4\ud1b5")
        self.color_value_label.setObjectName("valueLabel")
        color_label.addWidget(lbl3)
        color_label.addStretch()
        color_label.addWidget(self.color_value_label)
        color_layout.addLayout(color_label)

        self.color_slider = QSlider(Qt.Orientation.Horizontal)
        self.color_slider.setRange(1, 100)
        self.color_slider.setValue(20)
        self.color_slider.valueChanged.connect(self._on_color_speed_change)
        color_layout.addWidget(self.color_slider)
        body_layout.addLayout(color_layout)

        # Palette selector
        palette_layout = QVBoxLayout()
        palette_lbl = QLabel("\uc0c9\uc0c1 \ud314\ub808\ud2b8")
        palette_lbl.setObjectName("sliderLabel")
        palette_layout.addWidget(palette_lbl)

        palette_grid = QGridLayout()
        palette_grid.setSpacing(4)
        self._palette_buttons = {}
        palette_info = [
            ("aurora",   "\uc624\ub85c\ub77c",   [(100,200,200), (140,160,210), (170,140,190)]),
            ("ember",    "\uc5e0\ubc84",     [(210,140,110), (220,180,120), (200,130,150)]),
            ("neon_ink", "\ub124\uc628\uc789\ud06c", [(80,220,230),  (170,130,220), (220,120,190)]),
            ("sakura",   "\uc0ac\ucfe0\ub77c",   [(220,150,170), (200,130,160), (210,120,180)]),
            ("ocean",    "\uc624\uc158",     [(50,120,180),  (60,140,190),  (40,160,170)]),
            ("forest",   "\ud3ec\ub808\uc2a4\ud2b8", [(60,130,70),   (80,140,80),   (50,150,100)]),
            ("sunset",   "\uc120\uc14b",     [(230,160,80),  (220,120,90),  (240,180,100)]),
            ("galaxy",   "\uac24\ub7ed\uc2dc",   [(100,70,150),  (80,90,170),   (130,60,140)]),
            ("pastel",   "\ud30c\uc2a4\ud154",   [(170,190,220), (180,210,190), (220,180,200)]),
            ("ice",      "\uc544\uc774\uc2a4",   [(190,210,230), (180,200,220), (200,215,235)]),
            ("toxic",    "\ud1a1\uc2dd",     [(80,220,90),   (120,230,60),  (60,200,110)]),
            ("blood",    "\ube14\ub7ec\ub4dc",   [(180,40,40),   (150,30,50),   (200,60,45)]),
            ("rainbow",  "\ub808\uc778\ubcf4\uc6b0", [(220,80,80),   (80,200,80),   (80,80,220)]),
        ]
        for i, (name, label, colors) in enumerate(palette_info):
            btn = QPushButton(label)
            btn.setObjectName("paletteBtn")
            btn.setCheckable(True)
            btn.setChecked(name == "aurora")
            btn.setFixedHeight(26)
            c0, c1, c2 = colors
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba({c0[0]},{c0[1]},{c0[2]},100),
                        stop:0.5 rgba({c1[0]},{c1[1]},{c1[2]},100),
                        stop:1 rgba({c2[0]},{c2[1]},{c2[2]},100));
                    border: 1px solid rgba({c1[0]},{c1[1]},{c1[2]},80);
                    border-radius: 5px;
                    color: rgba(230,235,240,200);
                    font-size: 10px;
                    font-family: 'Noto Sans KR', sans-serif;
                    padding: 2px 4px;
                }}
                QPushButton:checked {{
                    border: 2px solid rgba({c1[0]},{c1[1]},{c1[2]},220);
                    color: white;
                }}
                QPushButton:hover {{
                    border-color: rgba({c1[0]},{c1[1]},{c1[2]},180);
                }}
            """)
            btn.clicked.connect(lambda checked, n=name: self._on_palette_change(n))
            palette_grid.addWidget(btn, i // 3, i % 3)
            self._palette_buttons[name] = btn

        palette_layout.addLayout(palette_grid)
        body_layout.addLayout(palette_layout)

        # Action buttons row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.clear_btn = QPushButton("\U0001f5d1 \uc9c0\uc6b0\uae30")
        self.clear_btn.setObjectName("actionBtn")
        self.clear_btn.clicked.connect(self.clear_requested.emit)
        btn_layout.addWidget(self.clear_btn)

        self.quit_btn = QPushButton("\uc885\ub8cc")
        self.quit_btn.setObjectName("quitBtn")
        self.quit_btn.clicked.connect(self.quit_requested.emit)
        btn_layout.addWidget(self.quit_btn)

        body_layout.addLayout(btn_layout)

        # Shortcut hints
        hints = QLabel("Ctrl+Shift+D: \ud1a0\uae00 | Ctrl+Shift+C: \uc9c0\uc6b0\uae30 | Ctrl+Shift+Q: \uc885\ub8cc")
        hints.setObjectName("hints")
        hints.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.addWidget(hints)

        container_layout.addWidget(self._body)
        layout.addWidget(self.container)

    def _apply_style(self):
        self.setStyleSheet(CONTROL_PANEL_STYLE)

    def set_drawing_state(self, active: bool):
        self._is_drawing = active
        self.toggle_btn.setChecked(active)
        if active:
            self.toggle_btn.setText("\u23f8 \uadf8\ub9ac\uae30 \uc911\uc9c0  (Ctrl+Shift+D)")
        else:
            self.toggle_btn.setText("\u25b6 \uadf8\ub9ac\uae30 \uc2dc\uc791  (Ctrl+Shift+D)")

    def _on_toggle(self, checked):
        self.set_drawing_state(checked)
        self.drawing_toggled.emit(checked)

    def _on_brush_change(self, value):
        self.brush_value_label.setText(str(value))
        self.brush_size_changed.emit(value)

    def _on_fade_change(self, value):
        duration = value / 10.0
        self.fade_value_label.setText(f"{duration:.1f}\ucd08")
        self.fade_duration_changed.emit(duration)

    def _on_color_speed_change(self, value):
        speed = value / 1000.0
        labels = {
            range(1, 20): "\ub290\ub9bc",
            range(20, 50): "\ubcf4\ud1b5",
            range(50, 80): "\ube60\ub984",
            range(80, 101): "\ub9e4\uc6b0 \ube60\ub984",
        }
        for r, label in labels.items():
            if value in r:
                self.color_value_label.setText(label)
                break
        self.color_speed_changed.emit(speed)

    def _on_palette_change(self, name: str):
        for pname, btn in self._palette_buttons.items():
            btn.setChecked(pname == name)
        self.palette_changed.emit(name)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
