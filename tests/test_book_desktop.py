from __future__ import annotations

import time
from datetime import date, datetime
from threading import Event

import pytest
from PySide6.QtCore import QDate
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QFileDialog

from stonks_sniper.app import MainWindow
from stonks_sniper.book import BookCompanion
from stonks_sniper.fundamentals import FundamentalSnapshot, FundamentalValue
from stonks_sniper.models import DataError
from stonks_sniper.providers import INDIA

pytestmark = pytest.mark.usefixtures("qt_events")


@pytest.fixture
def companion(qt_application):
    widget = BookCompanion()
    try:
        yield widget
    finally:
        widget.close()
        widget.deleteLater()


def snapshot():
    return FundamentalSnapshot(
        "ICICIBANK.NS",
        "NSE",
        datetime(2026, 11, 21, 20, tzinfo=INDIA),
        date(2026, 11, 20),
        "Financial Services",
        tuple(
            FundamentalValue(key, value, f"Source {key}, period 2026-03-31")
            for key, value in (
                ("price", 140),
                ("eps1", 8),
                ("eps2", 10),
                ("eps3", 12),
                ("book", 90),
            )
        ),
        ("Explicit provider warning",),
    )


def wait_fetch(widget, app):
    deadline = time.monotonic() + 5
    while widget.fetch_thread is not None and time.monotonic() < deadline:
        app.processEvents()
        QTest.qWait(5)
    assert widget.fetch_thread is None


def test_learning_sections_keep_technical_explanations_and_book_independent(qt_application):
    main = MainWindow()
    try:
        assert main.learning_sections.tabText(0) == "Internet technical strategies"
        assert main.learning_sections.tabText(1) == "The Intelligent Investor"
        main.learning_sections.setCurrentIndex(1)
        main.pattern.setCurrentIndex(3)
        main.open_pattern()
        assert main.tabs.currentIndex() == 1
        assert main.learning_sections.currentIndex() == 0
        assert main.lesson_list.currentRow() == 3
        main.symbol.setText("ICICIBANK")
        main.book.copy_stock.click()
        assert main.book.stock.text() == "ICICIBANK"
        assert main.book.currentIndex() == 1
        for index in range(20):
            main.book.chapters.setCurrentRow(index)
            text = main.book.chapter_text.toPlainText()
            assert f"Chapter {index + 1}:" in text
            assert "ELI15" in text and "Apply it to an Indian stock" in text
            assert "What this does NOT prove" in text
    finally:
        main.close()
        main.deleteLater()


def test_manual_inputs_require_provenance_and_changes_invalidate_result(companion):
    book = companion
    book.fields["price"].setText("140")
    book.calculate.click()
    assert "Give a source" in book.results.toPlainText()
    book.evidence.setText("Illustrative scenario, not ICICIBANK financials")
    for key, value in (("eps1", "8"), ("eps2", "10"), ("eps3", "12"), ("book", "90")):
        book.fields[key].setText(value)
    book.calculate.click()
    text = book.results.toPlainText()
    assert "142.3025" in text and "Not applicable" in text
    assert "USER INPUT: Illustrative scenario" in text
    assert book.save.isEnabled()
    book.as_of.setDate(QDate(2025, 1, 1))
    assert not book.save.isEnabled() and not book.report_html
    book.calculate.click()
    assert "manual as-of 2025-01-01" in book.results.toPlainText()
    book.fields["price"].setText("nan")
    book.calculate.click()
    assert "Cannot calculate" in book.results.toPlainText()
    assert not book.save.isEnabled()


def test_imported_bank_reference_has_dated_provenance_and_no_automatic_industrial_passes(companion):
    book = companion
    book.set_stock("ICICIBANK", "NSE")
    book.reference_ready(snapshot())
    assert book.classification.currentIndex() == 2
    book.calculate.click()
    text = book.results.toPlainText()
    assert "ICICIBANK.NS" in text and "Explicit provider warning" in text
    assert "Source eps1, period 2026-03-31" in text
    assert (
        "Not applicable" in text and "Unknown" in text and "Pass" not in text.split("Valuation")[1]
    )
    book.fields["price"].setText("141")
    assert "price" not in book.field_sources
    book.calculate.click()
    assert "Give a source" in book.results.toPlainText()
    book.stock.setText("TCS")
    assert book.snapshot is None and not book.report_html
    assert all(not field.text() for field in book.fields.values())
    assert not book.field_sources


def test_saved_worksheet_escapes_evidence_and_keeps_source_and_missing_data(
    companion, monkeypatch, tmp_path
):
    book = companion
    book.evidence.setText("Scenario <script>alert('not HTML')</script>")
    book.fields["price"].setText("100")
    book.calculate.click()
    filename = tmp_path / "study.html"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *_: (str(filename), "HTML"))
    book.save.click()
    text = filename.read_text(encoding="utf-8")
    assert "&lt;script&gt;" in text and "<script>" not in text
    assert "Unknown" in text and "No overall buy/sell rating" in text
    assert "investopedia.com" in text


def test_portfolio_exercises_calculate_and_clear_stale_results(companion):
    book = companion
    book.exercise_inputs[0].setText("8")
    book.exercise_inputs[1].setText("6")
    book.calculate_exercise()
    assert "1.8868%" in book.exercise_result.text()
    book.exercise.setCurrentIndex(1)
    assert "No current" in book.exercise_result.text()
    for field, value in zip(book.exercise_inputs, ("60000", "40000", "50"), strict=True):
        field.setText(value)
    book.calculate_exercise()
    assert "-10,000.00" in book.exercise_result.text()
    book.exercise.setCurrentIndex(2)
    book.exercise_inputs[0].setText("1000")
    book.exercise_inputs[1].setText("100,50")
    book.calculate_exercise()
    assert "30.000000" in book.exercise_result.text() and "66.6667" in book.exercise_result.text()
    book.exercise_inputs[1].setText("100,0")
    assert "No current" in book.exercise_result.text()
    book.calculate_exercise()
    assert "Cannot calculate" in book.exercise_result.text()


@pytest.mark.parametrize("fails", [False, True])
def test_threaded_reference_load_clears_previous_values_and_recovers_controls(
    companion, qt_application, monkeypatch, fails
):
    book = companion
    book.set_stock("ICICIBANK", "NSE")
    book.fields["price"].setText("999")
    calls = []

    def fetch(symbol, exchange):
        calls.append((symbol, exchange))
        if fails:
            raise DataError("Explicit reference failure")
        return snapshot()

    monkeypatch.setattr(book.provider, "fetch", fetch)
    book.load_button.click()
    assert not book.load_button.isEnabled() and not book.fields["price"].isEnabled()
    assert book.fields["price"].text() == ""
    wait_fetch(book, qt_application)
    assert calls == [("ICICIBANK.NS", "NSE")]
    assert book.load_button.isEnabled() and book.fields["price"].isEnabled()
    if fails:
        assert "Explicit reference failure" in book.provenance.text()
        assert book.snapshot is None and not book.fields["price"].text()
    else:
        assert book.snapshot is not None and book.fields["price"].text() == "140"


def test_main_cannot_destroy_owned_fundamental_thread(qt_application, monkeypatch):
    main = MainWindow()
    done = Event()

    def fetch(*_):
        if not done.wait(timeout=5):
            raise DataError("Test did not release its owned worker")
        return snapshot()

    monkeypatch.setattr(main.book.provider, "fetch", fetch)
    try:
        main.show()
        main.book.load_button.click()
        assert main.close() is False
        assert main.isVisible()
    finally:
        done.set()
        wait_fetch(main.book, qt_application)
        main.close()
        main.deleteLater()
