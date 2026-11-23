from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QLineEdit,
    QPushButton,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

SPEC = importlib.util.spec_from_file_location(
    "build_presentation", Path(__file__).resolve().parents[1] / "scripts" / "build_presentation.py"
)
assert SPEC is not None and SPEC.loader is not None
presentation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(presentation)


def test_gallery_refuses_visible_platform_before_constructing_a_window(monkeypatch):
    def forbidden_window():
        pytest.fail("A visible-platform capture must not construct an application window.")

    monkeypatch.setattr("stonks_sniper.app.MainWindow", forbidden_window)
    with pytest.raises(RuntimeError, match="before creating any windows"):
        presentation.build_gallery(SimpleNamespace(platformName=lambda: "windows"), None)


def test_walkthrough_click_changes_native_state_and_rejects_hidden_targets(
    qt_events, qt_application
):
    window = QWidget()
    layout = QVBoxLayout(window)
    button = QPushButton("Do something")
    layout.addWidget(button)
    clicked = []
    button.clicked.connect(lambda: clicked.append(True))
    window.show()
    try:
        tour = presentation.Walkthrough(
            qt_application, window, "A labelled UI test, not market data."
        )
        tour.click(button, "Click the actual button.")
        assert clicked == [True]
        assert tour.actions[-1]["kind"] == "click"
        button.hide()
        with pytest.raises(RuntimeError, match="hidden/disabled"):
            tour.click(button, "Must not fake a click.")
        assert clicked == [True]
    finally:
        window.close()
        window.deleteLater()


def test_walkthrough_uses_visible_tabs_dropdown_items_and_native_typing(qt_events, qt_application):
    window = QTabWidget()
    window.addTab(QWidget(), "First")
    page = QWidget()
    layout = QVBoxLayout(page)
    choice = QComboBox()
    choice.addItems(["Daily", "Weekly", "Monthly"])
    entry = QLineEdit("old")
    layout.addWidget(choice)
    layout.addWidget(entry)
    layout.addStretch()
    window.addTab(page, "Tools")
    window.show()
    try:
        tour = presentation.Walkthrough(qt_application, window, "Labelled native interaction test.")
        tour.tab(window, "Tools", "Open Tools.")
        tour.choose(choice, 2, "Choose Monthly.")
        tour.enter(entry, "ICICIBANK", "Type the stock identifier.")
        assert window.currentIndex() == 1
        assert choice.currentText() == "Monthly"
        assert entry.text() == "ICICIBANK"
    finally:
        window.close()
        window.deleteLater()


def test_walkthrough_drag_reveals_native_slider_positions(qt_events, qt_application):
    window = QWidget()
    layout = QVBoxLayout(window)
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(1, 496)
    slider.setValue(30)
    layout.addWidget(slider)
    changes = []
    slider.valueChanged.connect(changes.append)
    window.show()
    try:
        tour = presentation.Walkthrough(qt_application, window, "Labelled native drag test.")
        tour.drag(slider, 230, "Reveal observations.", steps=5)
        assert len(changes) >= 4
        assert changes == sorted(changes)
        assert abs(slider.value() - 230) <= 2
        assert tour.actions[-1]["actual"] == slider.value()
    finally:
        window.close()
        window.deleteLater()
