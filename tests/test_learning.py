from __future__ import annotations

import os
from dataclasses import replace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCharts import QAreaSeries, QCandlestickSeries, QChart  # noqa: E402
from PySide6.QtCore import QEvent, QPointF, Qt  # noqa: E402
from PySide6.QtGui import QMouseEvent  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication, QToolTip  # noqa: E402
from test_research import observations  # noqa: E402

from stonks_sniper.app import MainWindow  # noqa: E402
from stonks_sniper.glossary import explain, search_terms, tooltip  # noqa: E402
from stonks_sniper.patterns import PATTERNS  # noqa: E402


@pytest.fixture
def learning_window():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.motion.setChecked(False)
    yield window
    QToolTip.hideText()
    window.close()
    window.deleteLater()
    app.processEvents()


def test_pattern_button_and_term_help_preserve_the_experiment(learning_window):
    window = learning_window
    assert not window.windowIcon().pixmap(46, 46).isNull()
    window.pattern.setCurrentIndex(2)
    window.data_ready(observations())
    result = window.result
    window.pattern_help.click()
    assert window.tabs.currentIndex() == 1
    assert window.lesson_list.currentRow() == 2
    assert "Imagine a toy shop" in window.lesson_text.toPlainText()
    assert "score of 28" in window.lesson_text.toPlainText()
    assert window.result is result

    window.show()
    QApplication.processEvents()
    cursor = window.lesson_text.document().find("RSI")
    cursor.setPosition(cursor.selectionStart() + 1)
    position = window.lesson_text.cursorRect(cursor).center()
    viewport = window.lesson_text.viewport()
    mouse = QMouseEvent(
        QEvent.Type.MouseMove,
        QPointF(position),
        QPointF(viewport.mapToGlobal(position)),
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    QApplication.sendEvent(viewport, mouse)
    assert QToolTip.text() == tooltip("rsi")
    assert "28 is not a 28% chance" in QToolTip.text()
    cursor.setPosition(0)
    window.lesson_text.setTextCursor(cursor)
    window.lesson_text.setFocus(Qt.FocusReason.OtherFocusReason)
    QTest.keyClick(window.lesson_text, Qt.Key.Key_Tab)
    QTest.keyClick(window.lesson_text, Qt.Key.Key_Return)
    assert window.tabs.currentWidget() is window.dictionary
    assert window.glossary_keys[window.glossary_list.currentRow()] == "rsi"
    assert "Imagine this" in window.glossary_text.toPlainText()
    assert "28 is not a 28% chance" in window.glossary_text.toPlainText()
    assert window.result is result


def test_dictionary_search_and_safe_explanations(learning_window):
    window = learning_window
    for query, key in (("RSI", "rsi"), ("bps", "bps"), ("sigma", "spread"), ("share", "stock")):
        window.glossary_search.setText(query)
        assert window.glossary_keys[0] == key
        assert "Imagine this" in window.glossary_text.toPlainText()
    window.glossary_search.setText("not-a-known-market-word")
    assert window.glossary_list.count() == 0
    assert "No explanation found" in window.glossary_text.toPlainText()
    assert "square root" not in window.glossary_text.toPlainText()
    window.open_glossary("square-root")
    assert window.glossary_keys[window.glossary_list.currentRow()] == "square-root"
    assert "Nine toy blocks" in window.glossary_text.toPlainText()
    assert search_terms("  sMa  ")[0] == "sma"
    annotated = explain("<stock> & RSI")
    assert "&lt;" in annotated and "&gt; &amp;" in annotated
    assert "<stock>" not in annotated
    assert 'href="term:stock"' in annotated and 'href="term:rsi"' in annotated


def rule_points(window):
    result = []
    for series in window.rule_chart.chart().series():
        if isinstance(series, QCandlestickSeries):
            points = [
                (item.timestamp(), item.open(), item.high(), item.low(), item.close())
                for item in series.sets()
            ]
        else:
            points = [(point.x(), point.y()) for point in series.points()]
        result.append((series.name(), points))
    return result


@pytest.mark.parametrize("index", range(len(PATTERNS)), ids=[p.key for p in PATTERNS])
def test_rule_guides_do_not_read_beyond_replay_day(learning_window, index):
    window = learning_window
    data = observations()
    window.pattern.setCurrentIndex(index)
    window.data_ready(data)
    window.replay.setValue(50)
    full_history_guides = rule_points(window)
    window.data_ready(replace(data, candles=data.candles[:50]))
    assert rule_points(window) == full_history_guides


def test_drawing_window_preserves_results_and_motion_off_stops_replay(learning_window):
    window = learning_window
    window.data_ready(observations())
    window.replay.setValue(50)
    result = window.result
    metrics = [item.text() for item in window.metric_values]
    area = window.drawdown_chart.chart().series()[0]
    assert isinstance(area, QAreaSeries)
    falls = [(point.x(), point.y()) for point in area.upperSeries().points()]
    window.chart_span.setCurrentIndex(0)
    shortened = window.drawdown_chart.chart().series()[0]
    assert [(p.x(), p.y()) for p in shortened.upperSeries().points()] == falls[-30:]
    assert window.result is result
    assert [item.text() for item in window.metric_values] == metrics
    window.motion.setChecked(True)
    window.play.click()
    assert window.play_timer.isActive()
    window.motion.setChecked(False)
    assert not window.play_timer.isActive()
    assert not window.play.isChecked() and not window.play.isEnabled()
    for view in (window.price_chart, window.equity_chart, window.drawdown_chart, window.rule_chart):
        assert view.chart().animationOptions() == QChart.AnimationOption.NoAnimation
