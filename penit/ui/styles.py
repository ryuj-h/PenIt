"""QSS stylesheets for PenIt UI."""

CONTROL_PANEL_STYLE = """
    #container {
        background-color: rgba(20, 20, 30, 230);
        border-radius: 16px;
        border: 1px solid rgba(0, 220, 220, 80);
    }
    #title {
        color: #00e5e5;
        font-size: 16px;
        font-weight: bold;
        font-family: 'Segoe UI', 'Noto Sans KR', sans-serif;
    }
    #closeBtn {
        background: rgba(255, 80, 80, 60);
        border: none;
        border-radius: 12px;
        color: #ff6666;
        font-size: 12px;
        font-weight: bold;
    }
    #closeBtn:hover {
        background: rgba(255, 80, 80, 150);
        color: white;
    }
    #separator {
        color: rgba(0, 220, 220, 40);
        margin: 4px 0px;
    }
    #toggleBtn {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(0, 180, 180, 40), stop:1 rgba(0, 220, 220, 40));
        border: 1px solid rgba(0, 220, 220, 100);
        border-radius: 10px;
        color: #00e5e5;
        font-size: 14px;
        font-weight: bold;
        font-family: 'Segoe UI', 'Noto Sans KR', sans-serif;
        padding: 8px;
    }
    #toggleBtn:checked {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(0, 220, 180, 120), stop:1 rgba(0, 180, 255, 120));
        border: 1px solid rgba(0, 255, 220, 180);
        color: white;
    }
    #toggleBtn:hover {
        border: 1px solid rgba(0, 255, 255, 180);
    }
    #sliderLabel {
        color: rgba(200, 220, 230, 200);
        font-size: 12px;
        font-family: 'Segoe UI', 'Noto Sans KR', sans-serif;
    }
    #valueLabel {
        color: #00e5e5;
        font-size: 12px;
        font-weight: bold;
        font-family: 'Segoe UI', 'Noto Sans KR', sans-serif;
    }
    QSlider::groove:horizontal {
        height: 6px;
        background: rgba(0, 220, 220, 30);
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        width: 16px;
        height: 16px;
        margin: -5px 0;
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
            fx:0.5, fy:0.3, stop:0 #00ffff, stop:1 #008888);
        border-radius: 8px;
        border: 1px solid rgba(0, 255, 255, 100);
    }
    QSlider::handle:horizontal:hover {
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
            fx:0.5, fy:0.3, stop:0 #44ffff, stop:1 #00bbbb);
    }
    QSlider::sub-page:horizontal {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(0, 200, 200, 120), stop:1 rgba(0, 255, 255, 80));
        border-radius: 3px;
    }
    #actionBtn {
        background: rgba(0, 180, 180, 30);
        border: 1px solid rgba(0, 180, 180, 60);
        border-radius: 8px;
        color: rgba(200, 230, 230, 200);
        font-size: 12px;
        font-family: 'Segoe UI', 'Noto Sans KR', sans-serif;
        padding: 6px 12px;
    }
    #actionBtn:hover {
        background: rgba(0, 200, 200, 60);
        border-color: rgba(0, 255, 255, 120);
        color: white;
    }
    #quitBtn {
        background: rgba(180, 60, 60, 30);
        border: 1px solid rgba(180, 60, 60, 60);
        border-radius: 8px;
        color: rgba(230, 150, 150, 200);
        font-size: 12px;
        font-family: 'Segoe UI', 'Noto Sans KR', sans-serif;
        padding: 6px 12px;
    }
    #quitBtn:hover {
        background: rgba(220, 60, 60, 80);
        border-color: rgba(255, 80, 80, 150);
        color: white;
    }
    #hints {
        color: rgba(150, 170, 180, 120);
        font-size: 10px;
        font-family: 'Segoe UI', 'Noto Sans KR', sans-serif;
        margin-top: 4px;
    }
"""
