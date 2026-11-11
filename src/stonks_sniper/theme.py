from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QFont, QIcon, QPainter, QPainterPath, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

BASE = "#000f13"
PANEL = "#001e26"
ACCENT = "#00a591"
TEXT = "#93a1a1"
MUTED = "#839496"
WARM = "#eee8d5"
BORDER = "#586e75"
GREEN = "#45d072"
ROSE = "#e84a5f"
YELLOW = "#ebe565"
LOGO = Path(__file__).parent / "assets" / "logo.svg"


def application_icon() -> QIcon:
    renderer = QSvgRenderer(str(LOGO))
    if not renderer.isValid():
        raise RuntimeError(f"Application logo could not be loaded: {LOGO}")
    pixmap = QPixmap(256, 256)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    # Match the circular SVG boundary even when Qt ignores its clip path.
    clip = QPainterPath()
    clip.addEllipse(QRectF(8.5, 8.5, 239, 239))
    painter.setClipPath(clip)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def configure_application(app: QApplication) -> None:
    app.setApplicationName("StonksSniper")
    app.setWindowIcon(application_icon())
    app.setFont(QFont("Segoe UI", 10))
    app.setStyle("Fusion")
    app.setStyleSheet(
        f"""
        QWidget {{ background: {BASE}; color: {TEXT}; font-size: 13px;
            border-radius: 0; }}
        QLabel {{ background: transparent; }}
        QLabel#brand {{ color: {WARM}; font-size: 21px; font-weight: 650; }}
        QLabel#quiet {{ color: {MUTED}; font-size: 12px; }}
        QLabel#eyebrow {{ color: {ACCENT}; font-size: 11px; font-weight: 600; }}
        QLabel#metric {{ color: {WARM}; font-size: 25px; font-weight: 600; }}
        QLabel#section {{ color: {WARM}; font-size: 16px; font-weight: 600; }}
        QFrame#card {{ background: {PANEL}; border-radius: 0; }}
        QFrame#card QLineEdit, QFrame#card QComboBox, QFrame#card QDateEdit,
        QFrame#card QDoubleSpinBox {{ background: {BASE}; }}
        QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox {{
            background: {PANEL}; color: {WARM}; padding: 7px 9px;
            border: 1px solid rgba(88,110,117,90); border-radius: 0;
            selection-background-color: {ACCENT}; selection-color: {BASE};
        }}
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {{
            border: 1px solid {ACCENT};
        }}
        QComboBox::drop-down, QDateEdit::drop-down {{ border: none; width: 22px; }}
        QComboBox QAbstractItemView {{ background: {PANEL}; color: {WARM};
            selection-background-color: {ACCENT}; selection-color: {BASE}; }}
        QPushButton {{
            background: {PANEL}; color: {WARM}; border: 1px solid rgba(88,110,117,100);
            padding: 8px 14px; border-radius: 0; font-weight: 600;
        }}
        QPushButton:hover {{ border-color: {ACCENT}; background: #002b36; }}
        QPushButton:focus {{ border: 1px solid {ACCENT}; }}
        QPushButton#primary {{ background: {ACCENT}; color: {BASE}; border: none; }}
        QPushButton#primary:hover {{ background: {TEXT}; }}
        QPushButton:checked {{ background: {ACCENT}; color: {BASE}; }}
        QPushButton:disabled {{ color: {BORDER}; background: {PANEL};
            border-color: rgba(88,110,117,45); }}
        QTabWidget::pane {{ border: none; }}
        QTabBar::tab {{ color: {MUTED}; background: transparent; padding: 10px 18px;
            border-bottom: 2px solid transparent; margin-right: 8px; border-radius: 0; }}
        QTabBar::tab:selected {{ color: {WARM}; border-bottom: 2px solid {ACCENT}; }}
        QTabBar::tab:hover {{ color: {WARM}; }}
        QTabWidget#inspector::pane {{ background: {PANEL}; border-radius: 0; }}
        QTextBrowser {{ background: {PANEL}; border: none; padding: 12px;
            selection-background-color: {ACCENT}; selection-color: {BASE}; }}
        QListWidget {{ background: {PANEL}; border: none; border-radius: 0;
            outline: none; padding: 8px; }}
        QListWidget::item {{ padding: 15px 10px; border-radius: 0; }}
        QListWidget::item:selected {{ background: #002b36; color: {WARM};
            border-left: 3px solid {ACCENT}; }}
        QTableWidget {{ background: {PANEL}; border: none; gridline-color: {PANEL};
            alternate-background-color: {BASE}; selection-background-color: #002b36; }}
        QHeaderView::section {{ background: {PANEL}; color: {MUTED}; border: none;
            padding: 8px 5px; font-size: 11px; }}
        QTableWidget::item {{ padding: 5px; }}
        QSlider::groove:horizontal {{ height: 4px; background: {BORDER};
            border-radius: 0; }}
        QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 0; }}
        QSlider::handle:horizontal {{ background: {WARM}; border: 3px solid {ACCENT};
            width: 10px; height: 10px; margin: -6px 0; border-radius: 0; }}
        QCheckBox {{ spacing: 7px; color: {MUTED}; background: transparent; }}
        QCheckBox::indicator {{ width: 13px; height: 13px; border-radius: 0;
            border: 1px solid {BORDER}; background: {PANEL}; }}
        QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
        QScrollBar:vertical {{ width: 7px; background: {PANEL}; }}
        QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 0;
            min-height: 25px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QSplitter::handle {{ background: {BASE}; width: 12px; }}
        QToolTip {{ background: {PANEL}; color: {WARM}; border: 1px solid {BORDER};
            padding: 8px; }}
        QStatusBar {{ color: {MUTED}; font-size: 11px; }}
        """
    )
