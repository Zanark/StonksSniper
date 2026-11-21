from __future__ import annotations

import time
from dataclasses import replace
from threading import Event

import pytest
from PySide6.QtCore import QDate
from PySide6.QtTest import QTest
from test_book_desktop import snapshot
from test_research import observations

from stonks_sniper.app import (
    BookHistoryDemo,
    MainWindow,
    MarketDemoWindow,
    SimulationWindow,
    epoch,
)
from stonks_sniper.book import ReferenceDemo
from stonks_sniper.demonstrations import book_history_html, monthly_purchases, rule_guides
from stonks_sniper.engine import simulate
from stonks_sniper.patterns import PATTERNS

pytestmark = pytest.mark.usefixtures("qt_events")


@pytest.fixture
def main_window(qt_application):
    window = MainWindow()
    window.motion.setChecked(False)
    try:
        yield window
    finally:
        window.close()
        window.deleteLater()


@pytest.mark.parametrize("index", range(len(PATTERNS)), ids=[p.key for p in PATTERNS])
def test_each_learning_demo_captures_its_lesson_and_explains_only_revealed_measurements(
    main_window, index
):
    main = main_window
    data = observations()
    main.data_ready(data)
    original = main.result
    main.lesson_list.setCurrentRow(index)
    main.lesson_demo.click()
    picker = main.findChildren(MarketDemoWindow)[-1]
    assert picker.pattern is PATTERNS[index]
    picker.use_loaded.click()
    demo = main.findChildren(SimulationWindow)[-1]
    assert demo.learning and demo.pattern is PATTERNS[index]
    assert demo.replay.value() == PATTERNS[index].minimum_bars
    assert not demo.timer.isActive()
    for count in (90, max(50, PATTERNS[index].minimum_bars + 1)):
        demo.replay.setValue(count)
        expected = simulate(replace(data, candles=data.candles[:count]), PATTERNS[index])
        assert demo.money.text() == f"{expected.equity[-1]:,.2f}"
        assert str(data.candles[count - 1].session) in demo.rule_text.toPlainText()
        assert str(data.candles[count].session) not in demo.rule_text.toPlainText()
        assert len(demo.rule_chart.chart().axes()) == 2
        for series in demo.rule_chart.chart().series():
            points = series.sets() if hasattr(series, "sets") else series.points()
            assert all(
                (point.timestamp() if hasattr(point, "timestamp") else point.x())
                <= epoch(data.candles[count - 1].session)
                for point in points
            )
        for name, values in rule_guides(data.candles[:count], PATTERNS[index].key):
            assert name in demo.rule_text.toPlainText()
            if values[-1] is not None:
                assert f"{values[-1]:,.6f}" in demo.rule_text.toPlainText()
    assert main.result is original
    demo.finish.click()
    assert "Past application is not proof" in demo.rule_text.toPlainText()


def test_demo_event_navigation_and_date_changes_clear_explanations(main_window):
    main = main_window
    main.data_ready(observations())
    main.open_lesson_demo()
    picker = main.findChild(MarketDemoWindow)
    picker.use_loaded.click()
    demo = main.findChild(SimulationWindow)
    demo.next_trade.click()
    assert demo.trades.rowCount() == 1
    assert "filled today" in demo.rule_text.toPlainText()
    before = demo.replay.value()
    demo.next_signal.click()
    assert demo.replay.value() > before
    demo.finish.click()
    demo.next_trade.click()
    assert "No later trade" in demo.status.text()
    demo.start.setDate(QDate(2024, 1, 10))
    assert demo.experiment is None and not demo.rule_chart.chart().series()
    assert "Start a demo" in demo.rule_text.toPlainText()
    assert not demo.next_trade.isEnabled()


@pytest.mark.parametrize("fails", [False, True])
def test_demo_fetch_worker_owns_request_and_parent_close_is_guarded(
    main_window, qt_application, fails
):
    gate = Event()
    started = Event()
    requests = []

    class Provider:
        def fetch(self, *args):
            requests.append(args)
            started.set()
            assert gate.wait(5)
            if fails:
                raise ValueError("Explicit demo outage")
            return observations()

    main = main_window
    main.provider = Provider()
    main.open_lesson_demo()
    picker = main.findChild(MarketDemoWindow)
    picker.symbol.setText("ICICIBANK")
    picker.fetch.click()
    assert started.wait(2)
    assert not picker.fetch.isEnabled()
    assert not picker.close() and not main.close()
    gate.set()
    deadline = time.monotonic() + 5
    while picker.fetch_thread is not None and time.monotonic() < deadline:
        qt_application.processEvents()
        QTest.qWait(5)
    assert picker.fetch_thread is None and picker.fetch.isEnabled()
    assert requests[0][0:2] == ("ICICIBANK", "NSE")
    if fails:
        assert "Explicit demo outage" in picker.status.text()
        assert not main.findChildren(SimulationWindow)
    else:
        assert main.findChild(SimulationWindow).source_data.symbol == "TEST.NS"
    assert main.data is None


def test_book_history_and_reference_demos_are_bounded_and_do_not_erase_original(main_window):
    main = main_window
    main.data_ready(observations())
    book = main.book
    book.evidence.setText("Preserve my manual scenario")
    book.fields["price"].setText("999")
    for chapter in range(1, 21):
        book.chapters.setCurrentRow(chapter - 1)
        assert book.demo_button.isEnabled() == (chapter in {2, 3, 5, 7, 8, 11, 12, 13, 14, 15, 20})
    book.chapters.setCurrentRow(4)
    book.demo_button.click()
    main.findChildren(MarketDemoWindow)[-1].use_loaded.click()
    demo = main.findChild(BookHistoryDemo)
    demo.finish.click()
    assert len(monthly_purchases(observations().candles)) == 4
    assert demo.purchases.count() == 4
    text = demo.explanation.toPlainText()
    assert "INR 4,000.00" in text and "NOT annualised" in text
    demo.replay.setValue(20)
    assert demo.purchases.count() == 1 and "2024-02" not in demo.explanation.toPlainText()
    book.chapters.setCurrentRow(13)
    book.demo_button.click()
    reference = book.findChild(ReferenceDemo)
    reference.workbook.reference_ready(snapshot())
    assert (
        reference.workbook.report_html
        and "Not applicable" in reference.workbook.results.toPlainText()
    )
    assert book.fields["price"].text() == "999" and book.snapshot is None
    assert book.evidence.text() == "Preserve my manual scenario"


def test_inflation_demo_uses_period_scaled_explicit_assumption_and_causal_prices():
    data = observations()
    text = book_history_html(data, 1, 2, 1000, 6)
    assert "USER ASSUMPTION, not measured CPI" in text and "0.0000%" in text
    assert "2024-01-02" not in text
    text = book_history_html(data, 100, 8, 1000, 6)
    assert "NOT a buy/sell" in text and "permanent loss" in text
