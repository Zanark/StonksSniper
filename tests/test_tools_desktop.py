from __future__ import annotations

import json
from dataclasses import replace

import pytest
from test_market_tools import history

from stonks_sniper.models import Candle
from stonks_sniper.tool_lessons import TOOL_LESSONS
from stonks_sniper.tools_ui import MarketTools

pytestmark = pytest.mark.usefixtures("qt_events")


@pytest.fixture
def desk():
    widget = MarketTools(history)
    yield widget
    widget.close()
    widget.deleteLater()


def test_capture_orders_alerts_and_charts_reveal_only_prefix(desk):
    desk.capture_button.click()
    assert len(desk.prefix()) == 1
    assert desk.watch_table.item(0, 1).text() == "2024-01-02"
    desk.order_kind.setCurrentText("Market")
    desk.submit_order.click()
    assert desk.account.units == 0
    desk.alert_level.setValue(105)
    desk.add_alert()
    assert desk.alert_table.item(0, 2).text() == "0"
    desk.next_day.click()
    assert desk.account.orders[0].status == "Filled"
    assert desk.account.orders[0].updated.isoformat() == "2024-01-03"
    assert desk.alert_table.item(0, 2).text() == "1"
    assert "2024-01-05" not in desk.quote.toPlainText()
    assert all(point.x() <= 2 for series in desk.chart.series() for point in series.points())
    assert desk.order_table.rowCount() == 1
    assert "unrealised" in desk.holdings.text()


def test_chart_modes_grouping_annotations_comparison_and_advance_to(desk):
    data = history()
    other = replace(
        data,
        symbol="TCS.NS",
        candles=tuple(
            Candle(b.session, b.open * 2, b.high * 2, b.low * 2, b.close * 2, b.volume)
            for b in data.candles
        ),
    )
    desk.capture_button.click()
    desk.snapshots["TCS.NS / NSE"] = other
    desk.compare_stock.addItem("TCS.NS / NSE")
    desk.jump_to.setValue(4)
    desk.reveal(3)
    desk.line_to.setValue(3)
    desk.add_line()
    desk.add_level()
    assert len(desk.lines) == len(desk.levels) == 1
    for mode in ("Candles", "Volume", "Paper money", "Compare (100)", "Line"):
        desk.chart_mode.setCurrentText(mode)
        if mode == "Compare (100)":
            desk.compare_stock.setCurrentText("TCS.NS / NSE")
            series = desk.chart.series()
            assert series[0].points() == series[1].points()
    desk.timeframe.setCurrentText("Weekly")
    assert len(desk.chart.axes()) == 2
    assert not desk.next_day.isEnabled()
    desk.submit_order.click()
    assert "No later observation" in desk.status.text()
    desk.reveal(0)
    assert "cannot rewind" in desk.status.text()


def test_capture_absent_and_calculator_errors_are_visible(desk):
    desk.capture = lambda: None
    desk.capture_button.click()
    assert "NOT COMPLETED" in desk.status.text()
    desk.risk_stop.setValue(110)
    desk.calculate_risk()
    assert "INVALID PLAN" in desk.risk_output.toPlainText()
    desk.weights.setText("60, 60")
    desk.calculate_allocation()
    assert "INVALID ALLOCATION" in desk.allocation_output.toPlainText()
    desk.bids.setText("not depth")
    desk.calculate_depth()
    assert "INVALID SCENARIO" in desk.depth_output.toPlainText()


def test_save_load_and_export_fail_without_overwrite(desk, monkeypatch, tmp_path):
    from stonks_sniper import tools_ui

    desk.capture_button.click()
    path = tmp_path / "watch.json"
    monkeypatch.setattr(tools_ui.QFileDialog, "getSaveFileName", lambda *_: (str(path), ""))
    desk.save_watchlist()
    assert json.loads(path.read_text())["instruments"][0]["symbol"] == "ICICIBANK.NS"
    before = path.read_bytes()
    desk.save_watchlist()
    assert "NOT COMPLETED" in desk.status.text() and path.read_bytes() == before
    monkeypatch.setattr(tools_ui.QFileDialog, "getOpenFileName", lambda *_: (str(path), ""))
    desk.open_watchlist()
    assert "Loaded identifiers" in desk.status.text()
    export = tmp_path / "paper.json"
    monkeypatch.setattr(tools_ui.QFileDialog, "getSaveFileName", lambda *_: (str(export), ""))
    desk.submit_order.click()
    desk.advance()
    desk.export_session()
    saved = json.loads(export.read_text())
    assert saved["orders"][0]["status"] == "Filled"
    assert len(saved["data"]["candles"]) == 4 and len(saved["equity_marks"]) == 2
    assert saved["revealed_session"] == "2024-01-03"
    assert "FUTURE" in " ".join(saved["limitations"])
    before = export.read_bytes()
    desk.export_session()
    assert export.read_bytes() == before and "NOT COMPLETED" in desk.status.text()


def test_tool_search_original_lessons_and_no_match(desk):
    assert len(TOOL_LESSONS) == 20
    desk.lesson_search.setText("GTT")
    assert desk.lesson_list.count() > 0
    assert "Everyday example" in desk.lesson_text.toPlainText()
    desk.lesson_search.setText("uncovered jargon zxzz")
    assert "No authored" in desk.lesson_text.toPlainText()


def test_reset_prompt_can_preserve_orders_or_drawings(desk, monkeypatch):
    from stonks_sniper import tools_ui

    desk.capture_button.click()
    desk.add_level()
    monkeypatch.setattr(
        tools_ui.QMessageBox, "question", lambda *_: tools_ui.QMessageBox.StandardButton.No
    )
    desk.capture_button.click()
    assert len(desk.levels) == 1
    desk.submit_order.click()
    desk.reset_account()
    assert len(desk.account.orders) == 1
    monkeypatch.setattr(
        tools_ui.QMessageBox, "question", lambda *_: tools_ui.QMessageBox.StandardButton.Yes
    )
    desk.reset_account()
    assert not desk.levels and not desk.account.orders


def test_watchlist_prices_sort_numerically_and_uncaptured_rows_do_not_get_quotes(desk):
    from PySide6.QtCore import Qt

    desk.capture_button.click()
    other = replace(
        history(),
        symbol="TCS.NS",
        candles=(replace(history().candles[0], open=90, high=95, low=85, close=90),),
    )
    desk.snapshots["TCS.NS / NSE"] = other
    desk.watch_entries = (*desk.watch_entries, ("TCS.NS", "NSE"), ("INFY.NS", "NSE"))
    desk.refresh_watch()
    desk.watch_table.sortItems(2, Qt.SortOrder.AscendingOrder)
    loaded = [
        desk.watch_table.item(row, 0).text()
        for row in range(3)
        if desk.watch_table.item(row, 1).text() != "Not loaded/revealed"
    ]
    assert loaded == ["TCS.NS / NSE", "ICICIBANK.NS / NSE"]
    unloaded = next(
        row for row in range(3) if desk.watch_table.item(row, 0).text() == "INFY.NS / NSE"
    )
    assert desk.watch_table.item(unloaded, 2).text() == "-"
