from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import asdict
from datetime import date
from html import escape
from pathlib import Path

from PySide6.QtCharts import (
    QCandlestickSeries,
    QCandlestickSet,
    QChart,
    QChartView,
    QLineSeries,
    QValueAxis,
)
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from stonks_sniper.demonstrations import rule_guides
from stonks_sniper.market_tools import (
    OrderType,
    PaperAccount,
    Side,
    allocation,
    comparison,
    crossings,
    depth_summary,
    grouped_bars,
    load_watchlist,
    option_payoff,
    position_size,
    quote_text,
    watchlist_document,
)
from stonks_sniper.models import Candle, DataError, MarketData
from stonks_sniper.theme import ACCENT, BASE, GREEN, ROSE, TEXT, WARM, YELLOW
from stonks_sniper.tool_lessons import TOOL_LESSONS

LOGGER = logging.getLogger(__name__)


class WatchNumber(QTableWidgetItem):
    def __init__(self, text: str, number: float | None) -> None:
        super().__init__(text)
        self.number = number
        self.setToolTip(text)

    def __lt__(self, other: QTableWidgetItem) -> bool:
        if isinstance(other, WatchNumber):
            return (self.number is None, self.number or 0) < (
                other.number is None,
                other.number or 0,
            )
        return super().__lt__(other)


def note(text: str) -> QLabel:
    widget = QLabel(text)
    widget.setWordWrap(True)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    return widget


def spin(value: float, minimum: float = 0.01, maximum: float = 1e9) -> QDoubleSpinBox:
    widget = QDoubleSpinBox()
    widget.setDecimals(4)
    widget.setRange(minimum, maximum)
    widget.setValue(value)
    return widget


def combo(items: list[str]) -> QComboBox:
    widget = QComboBox()
    widget.addItems(items)
    return widget


def table(headers: list[str]) -> QTableWidget:
    widget = QTableWidget(0, len(headers))
    widget.setHorizontalHeaderLabels(headers)
    widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    widget.horizontalHeader().setStretchLastSection(True)
    widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    return widget


def rows(widget: QTableWidget, values: list[list[str]]) -> None:
    widget.setSortingEnabled(False)
    widget.setRowCount(len(values))
    for row, fields in enumerate(values):
        for column, value in enumerate(fields):
            item = QTableWidgetItem(value)
            item.setToolTip(value)
            widget.setItem(row, column, item)


class MarketTools(QWidget):
    def __init__(self, capture: Callable[[], MarketData | None]) -> None:
        super().__init__()
        self.capture = capture
        self.snapshots: dict[str, MarketData] = {}
        self.watch_entries: tuple[tuple[str, str], ...] = ()
        self.data: MarketData | None = None
        self.replay_index = 0
        self.account = PaperAccount(10000)
        self.levels: list[float] = []
        self.lines: list[tuple[int, float, int, float]] = []
        self.alerts: list[tuple[str, float]] = []
        self.equity_marks: list[tuple[date, float]] = []
        outer = QVBoxLayout(self)
        outer.addWidget(
            note(
                "PRACTICE DESK | Real completed daily history; pretend money. "
                "No broker connection, live quotes or real orders. Start with Tool guide."
            )
        )
        controls = QHBoxLayout()
        self.capture_button = QPushButton("Capture Explore history")
        self.capture_button.clicked.connect(self.capture_history)
        controls.addWidget(self.capture_button)
        self.instrument = QComboBox()
        self.instrument.setMinimumWidth(170)
        self.instrument.currentTextChanged.connect(self.choose_data)
        controls.addWidget(self.instrument, 1)
        self.next_day = QPushButton("Next observed day")
        self.next_day.clicked.connect(self.advance)
        self.next_day.setEnabled(False)
        controls.addWidget(self.next_day)
        self.jump_to = QSpinBox()
        self.jump_to.setRange(1, 1)
        self.jump_to.setPrefix("Go to #")
        controls.addWidget(self.jump_to)
        reveal = QPushButton("Advance to")
        reveal.clicked.connect(lambda: self.reveal(self.jump_to.value() - 1))
        controls.addWidget(reveal)
        self.practice_date = note("No history captured")
        controls.addWidget(self.practice_date)
        outer.addLayout(controls)
        self.status = note(
            "Fetch actual history in Explore, then capture it. No network request is hidden here."
        )
        self.status.setAccessibleName("Practice desk status and errors")
        outer.addWidget(self.status)
        body = QHBoxLayout()
        self.navigation = QListWidget()
        self.navigation.addItems(
            [
                "Tool guide",
                "Watchlist",
                "Charts",
                "Historical alerts",
                "Paper orders & holdings",
                "Risk & allocation",
                "Depth & options labs",
            ]
        )
        self.navigation.setFixedWidth(190)
        body.addWidget(self.navigation)
        self.pages = QStackedWidget()
        body.addWidget(self.pages, 1)
        outer.addLayout(body, 1)
        self.build_guide()
        self.build_watchlist()
        self.build_charts()
        self.build_alerts()
        self.build_orders()
        self.build_risk()
        self.build_scenarios()
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.setCurrentRow(0)

    def page(self, explanation: str) -> QVBoxLayout:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(note(explanation))
        self.pages.addWidget(widget)
        return layout

    def error(self, error: Exception) -> None:
        LOGGER.warning("Practice desk: %s", error)
        self.status.setText(f"NOT COMPLETED: {error}")

    def build_guide(self) -> None:
        layout = self.page(
            "Twenty original tool lessons: what it does, a household example, a practical "
            "exercise and the exact boundary. Search words such as GTT, liquidity or margin."
        )
        self.lesson_search = QLineEdit()
        self.lesson_search.setPlaceholderText("Search tool names and explanations...")
        layout.addWidget(self.lesson_search)
        columns = QHBoxLayout()
        self.lesson_list = QListWidget()
        self.lesson_list.setFixedWidth(250)
        self.lesson_list.setWordWrap(True)
        self.lesson_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        columns.addWidget(self.lesson_list)
        self.lesson_text = QTextBrowser()
        self.lesson_text.setOpenExternalLinks(True)
        self.lesson_text.document().setDefaultStyleSheet(
            f"a {{ color: {ACCENT}; }} h1, h3 {{ color: {WARM}; }}"
        )
        columns.addWidget(self.lesson_text, 1)
        layout.addLayout(columns)
        self.lesson_indices: list[int] = []
        self.lesson_search.textChanged.connect(self.filter_lessons)
        self.lesson_list.currentRowChanged.connect(self.lesson_selected)
        self.filter_lessons("")

    def filter_lessons(self, query: str) -> None:
        self.lesson_indices = [
            i
            for i, lesson in enumerate(TOOL_LESSONS)
            if query.casefold() in " ".join(asdict(lesson).values()).casefold()
        ]
        self.lesson_list.clear()
        self.lesson_list.addItems([TOOL_LESSONS[i].title for i in self.lesson_indices])
        if self.lesson_indices:
            self.lesson_list.setCurrentRow(0)
        else:
            self.lesson_text.setPlainText("No authored tool lesson matches. Try a shorter word.")

    def lesson_selected(self, row: int) -> None:
        if 0 <= row < len(self.lesson_indices):
            self.lesson_text.setHtml(TOOL_LESSONS[self.lesson_indices[row]].html())

    def build_watchlist(self) -> None:
        layout = self.page(
            "Capture separately fetched histories to build a local watchlist. "
            "Rows show only observations at or before the active practice date. "
            "Saving remembers identifiers, NOT quotes, accounts or credentials."
        )
        actions = QHBoxLayout()
        for title, handler in (
            ("Save list as new JSON", self.save_watchlist),
            ("Load list JSON", self.open_watchlist),
            ("Remove selected", self.remove_watch),
        ):
            button = QPushButton(title)
            button.clicked.connect(handler)
            actions.addWidget(button)
        layout.addLayout(actions)
        self.watch_table = table(
            [
                "Instrument",
                "Observed date",
                "Adjusted close",
                "Change %",
                "Volume",
                "Study snapshot",
            ]
        )
        self.watch_table.setSortingEnabled(True)
        self.watch_table.cellDoubleClicked.connect(self.select_watch)
        layout.addWidget(self.watch_table, 1)
        self.quote = QTextBrowser()
        self.quote.setMaximumHeight(160)
        layout.addWidget(self.quote)

    def confirm_reset(self) -> bool:
        if not (self.account.orders or self.alerts or self.levels or self.lines):
            return True
        return (
            QMessageBox.question(
                self,
                "Discard local paper exercise?",
                "This starts a fresh account and discards unsaved orders, alerts and drawings. "
                "Export first if you need the record. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        )

    def capture_history(self) -> None:
        data = self.capture()
        if data is None:
            self.error(DataError("Fetch real history in Explore first."))
            return
        if not self.confirm_reset():
            return
        key = f"{data.symbol} / {data.exchange}"
        entry = (data.symbol, data.exchange)
        entries = (
            self.watch_entries if entry in self.watch_entries else (*self.watch_entries, entry)
        )
        try:
            watchlist_document(entries)
        except DataError as error:
            self.error(error)
            return
        self.watch_entries = entries
        self.snapshots[key] = data
        self.instrument.blockSignals(True)
        if self.instrument.findText(key) < 0:
            self.instrument.addItem(key)
            self.compare_stock.addItem(key)
        self.instrument.setCurrentText(key)
        self.instrument.blockSignals(False)
        self.activate(data)
        self.status.setText(
            f"Captured {key}: {len(data.candles)} observations; source dates "
            f"{data.candles[0].session} to {data.candles[-1].session}. "
            "Fresh paper account. Only the first session is revealed."
        )

    def choose_data(self, key: str) -> None:
        if key not in self.snapshots:
            return
        if not self.confirm_reset():
            self.instrument.blockSignals(True)
            if self.data is not None:
                self.instrument.setCurrentText(f"{self.data.symbol} / {self.data.exchange}")
            self.instrument.blockSignals(False)
            return
        self.activate(self.snapshots[key])
        self.status.setText("Selected snapshot; fresh paper account and first revealed session.")

    def activate(self, data: MarketData) -> None:
        self.data = data
        self.replay_index = 0
        self.jump_to.setRange(1, len(data.candles))
        self.account = PaperAccount(
            self.paper_capital.value(), self.paper_fee.value(), self.paper_slip.value()
        )
        self.account.advance(data.candles[0])
        self.levels.clear()
        self.lines.clear()
        self.alerts.clear()
        self.equity_marks = [(data.candles[0].session, self.account.capital)]
        self.refresh()

    def prefix(self) -> tuple[Candle, ...]:
        return self.data.candles[: self.replay_index + 1] if self.data else ()

    def advance(self) -> None:
        self.reveal(self.replay_index + 1)

    def reveal(self, target: int) -> None:
        if self.data is None:
            return
        if target <= self.replay_index:
            self.error(DataError("Paper clock cannot rewind. Reset to start a fresh exercise."))
            return
        for index in range(self.replay_index + 1, min(target + 1, len(self.data.candles))):
            bar = self.data.candles[index]
            self.account.advance(bar)
            self.equity_marks.append(
                (bar.session, self.account.cash + self.account.units * bar.close)
            )
            self.replay_index = index
        self.refresh()
        self.status.setText(
            f"Revealed through {self.prefix()[-1].session}. Paper ledger: "
            f"{sum(o.status == 'Filled' for o in self.account.orders)} filled, "
            f"{sum(o.status == 'Rejected' for o in self.account.orders)} rejected, "
            f"{sum(o.status == 'Pending' for o in self.account.orders)} pending."
        )

    def refresh(self) -> None:
        bars = self.prefix()
        if not bars or self.data is None:
            return
        self.practice_date.setText(
            f"{bars[-1].session} | {len(bars)} / {len(self.data.candles)} observations"
        )
        self.next_day.setEnabled(len(bars) < len(self.data.candles))
        for widget in (self.line_from, self.line_to, self.measure_from):
            widget.setMaximum(len(bars))
        self.quote.setPlainText(quote_text(self.data, bars[-1].session))
        self.refresh_watch()
        self.refresh_chart()
        self.refresh_alerts()
        self.refresh_orders()

    def refresh_watch(self) -> None:
        cutoff = self.prefix()[-1].session if self.prefix() else None
        values: list[list[str]] = []
        for symbol, exchange in self.watch_entries:
            key = f"{symbol} / {exchange}"
            data = self.snapshots.get(key)
            bars = (
                tuple(b for b in data.candles if cutoff is not None and b.session <= cutoff)
                if data
                else ()
            )
            if not bars:
                values.append([key, "Not loaded/revealed", "-", "-", "-", "No substitute quote"])
                continue
            last = bars[-1]
            change = (
                f"{100 * (last.close / bars[-2].close - 1):+.2f}" if len(bars) > 1 else "Unknown"
            )
            guide = rule_guides(bars, "sma")
            fast, slow = guide[0][1][-1], guide[1][1][-1]
            signal = (
                ("SMA10 > SMA30" if fast > slow else "SMA10 <= SMA30")
                if (fast is not None and slow is not None)
                else "SMA warmup"
            )
            values.append(
                [key, str(last.session), f"{last.close:.4f}", change, f"{last.volume:.0f}", signal]
            )
        rows(self.watch_table, values)
        for row, fields in enumerate(values):
            for column in (2, 3, 4):
                number = float(fields[column]) if fields[column] not in ("-", "Unknown") else None
                self.watch_table.setItem(row, column, WatchNumber(fields[column], number))
        self.watch_table.setSortingEnabled(True)

    def select_watch(self, row: int, column: int) -> None:
        item = self.watch_table.item(row, 0)
        if item is not None:
            key = item.text()
            if key in self.snapshots:
                self.instrument.setCurrentText(key)
            else:
                self.error(
                    DataError("Identifier only: fetch this instrument in Explore and capture it.")
                )

    def remove_watch(self) -> None:
        item = self.watch_table.item(self.watch_table.currentRow(), 0)
        if item is None:
            self.error(DataError("Select a watchlist row."))
            return
        self.watch_entries = tuple(
            entry for entry in self.watch_entries if f"{entry[0]} / {entry[1]}" != item.text()
        )
        self.refresh_watch()
        self.status.setText(
            "Removed watchlist identifier. Captured session data remains available."
        )

    def save_watchlist(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "New watchlist JSON", "", "JSON (*.json)")
        if not filename:
            return
        try:
            document = watchlist_document(self.watch_entries)
            with Path(filename).open("x", encoding="utf-8") as handle:
                json.dump(document, handle, indent=2)
            self.status.setText(f"Saved identifiers only: {Path(filename).resolve()}")
        except (OSError, ValueError) as error:
            self.error(error)

    def open_watchlist(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Watchlist JSON", "", "JSON (*.json)")
        if not filename:
            return
        try:
            self.watch_entries = load_watchlist(Path(filename))
            self.refresh_watch()
            self.status.setText(
                "Loaded identifiers; no automatic fetch or quote reuse from the file."
            )
        except (OSError, ValueError) as error:
            self.error(error)

    def build_charts(self) -> None:
        layout = self.page(
            "Real revealed observations only. Drag a rectangle to zoom; Reset zoom restores. "
            "Weekly/monthly periods may be partial. Ordinal x-axis counts displayed observations, "
            "not calendar days. Manual drawings are hypotheses, never signals."
        )
        settings = QHBoxLayout()
        self.timeframe = combo(["Daily", "Weekly", "Monthly"])
        self.chart_mode = combo(["Line", "Candles", "Volume", "Compare (100)", "Paper money"])
        self.study = combo(["No study", "sma", "ema", "bollinger", "donchian"])
        self.study.setToolTip("Shared exact existing study formulas; periods count displayed bars.")
        self.compare_stock = QComboBox()
        self.compare_stock.setPlaceholderText("Comparison stock")
        self.visible = QSpinBox()
        self.visible.setRange(10, 20000)
        self.visible.setValue(120)
        self.visible.setPrefix("Last ")
        self.visible.setSuffix(" bars")
        for widget in (
            self.timeframe,
            self.chart_mode,
            self.study,
            self.compare_stock,
            self.visible,
        ):
            settings.addWidget(widget)
        layout.addLayout(settings)
        self.chart = QChart()
        self.chart.setBackgroundBrush(QColor(BASE))
        self.chart.setBackgroundRoundness(0)
        self.chart.setTitleBrush(QColor(WARM))
        self.chart.legend().setLabelColor(QColor(TEXT))
        self.axis_x, self.axis_y = QValueAxis(), QValueAxis()
        self.axis_x.setTitleText("Displayed observation number")
        self.axis_x.setLabelFormat("%.0f")
        for axis in (self.axis_x, self.axis_y):
            axis.setLabelsColor(QColor(TEXT))
            axis.setTitleBrush(QColor(TEXT))
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setRubberBand(QChartView.RubberBand.RectangleRubberBand)
        layout.addWidget(self.chart_view, 1)
        self.chart_detail = note("No revealed data")
        layout.addWidget(self.chart_detail)
        drawing = QHBoxLayout()
        self.level = spin(100)
        add_level = QPushButton("Add level")
        add_level.clicked.connect(self.add_level)
        self.line_from, self.line_to, self.measure_from = QSpinBox(), QSpinBox(), QSpinBox()
        self.line_from.setPrefix("From #")
        self.line_to.setPrefix("To #")
        for field in (self.line_from, self.line_to, self.measure_from):
            field.setRange(1, 1)
        self.line_price_from, self.line_price_to = spin(100), spin(110)
        self.line_price_from.setPrefix("INR ")
        self.line_price_to.setPrefix("INR ")
        add_line = QPushButton("Add line")
        add_line.clicked.connect(self.add_line)
        clear = QPushButton("Clear drawings")
        clear.clicked.connect(self.clear_drawings)
        for drawing_widget in (
            self.level,
            add_level,
            self.line_from,
            self.line_price_from,
            self.line_to,
            self.line_price_to,
            add_line,
            clear,
        ):
            drawing.addWidget(drawing_widget)
        layout.addLayout(drawing)
        measure = QHBoxLayout()
        measure.addWidget(note("Measure from revealed daily session #"))
        measure.addWidget(self.measure_from)
        reset = QPushButton("Reset zoom")
        reset.clicked.connect(self.refresh_chart)
        measure.addWidget(reset)
        layout.addLayout(measure)
        for selector in (self.timeframe, self.chart_mode, self.study, self.compare_stock):
            selector.currentIndexChanged.connect(self.refresh_chart)
        self.visible.valueChanged.connect(self.refresh_chart)
        self.measure_from.valueChanged.connect(self.refresh_chart)

    def add_level(self) -> None:
        if self.data is None:
            self.error(DataError("Capture actual history first."))
            return
        self.levels.append(self.level.value())
        self.refresh_chart()

    def add_line(self) -> None:
        if self.line_from.value() >= self.line_to.value() or self.data is None:
            self.error(DataError("Choose two revealed DAILY session numbers, start before end."))
            return
        self.lines.append(
            (
                self.line_from.value(),
                self.line_price_from.value(),
                self.line_to.value(),
                self.line_price_to.value(),
            )
        )
        self.refresh_chart()

    def clear_drawings(self) -> None:
        self.levels.clear()
        self.lines.clear()
        self.refresh_chart()

    def plot(
        self,
        name: str,
        points: list[tuple[float, float]],
        color: str,
        *,
        hover_dates: tuple[date, ...] = (),
    ) -> None:
        series = QLineSeries()
        series.setName(name)
        series.setPen(QPen(QColor(color), 1.7))
        series.setPointsVisible(len(points) < 3)
        for x, y in points:
            series.append(x, y)
        if hover_dates:

            def hover(point: QPointF, entered: bool) -> None:
                if entered:
                    index = round(point.x()) - 1
                    if 0 <= index < len(hover_dates):
                        self.chart_detail.setText(
                            f"{name}: {hover_dates[index]} | {point.y():,.4f}"
                        )

            series.hovered.connect(hover)
        self.chart.addSeries(series)
        series.attachAxis(self.axis_x)
        series.attachAxis(self.axis_y)

    def refresh_chart(self) -> None:
        if not hasattr(self, "chart"):
            return
        self.chart.zoomReset()
        self.chart.removeAllSeries()
        prefix = self.prefix()
        if not prefix:
            return
        mode = self.chart_mode.currentText()
        self.timeframe.setEnabled(mode not in ("Compare (100)", "Paper money"))
        self.study.setEnabled(mode in ("Line", "Candles"))
        self.compare_stock.setEnabled(mode == "Compare (100)")
        bars = grouped_bars(prefix, self.timeframe.currentText())
        start = max(0, len(bars) - self.visible.value())
        points: list[tuple[float, float]] = []
        y_values: list[float] = []
        self.chart.setTitle(
            f"{self.instrument.currentText()} | {bars[start].session} to {bars[-1].session} | "
            f"{self.timeframe.currentText()} (edge periods may be partial)"
        )
        if mode == "Compare (100)":
            other = self.snapshots.get(self.compare_stock.currentText())
            if other is None:
                self.chart_detail.setText("Capture another stock, then select it for comparison.")
                return
            try:
                shared = comparison(
                    prefix, tuple(b for b in other.candles if b.session <= prefix[-1].session)
                )
            except DataError as error:
                self.chart_detail.setText(str(error))
                return
            for name, compare_values, color in (
                (self.instrument.currentText(), [item[1] for item in shared], ACCENT),
                (self.compare_stock.currentText(), [item[2] for item in shared], YELLOW),
            ):
                points = [(float(i + 1), value) for i, value in enumerate(compare_values)]
                self.plot(name, points, color)
                y_values.extend(y for _, y in points)
            self.axis_x.setRange(1, max(2, len(shared)))
            self.chart.setTitle(
                f"Daily exact shared sessions | {shared[0][0]} to {shared[-1][0]} | start = 100"
            )
        elif mode == "Paper money":
            points = [(float(i + 1), value) for i, (_, value) in enumerate(self.equity_marks)]
            self.plot("Marked paper account INR", points, ACCENT)
            y_values = [value for _, value in points]
            self.axis_x.setRange(1, max(2, len(points)))
            self.chart.setTitle("Daily paper account | cash plus unsold units at revealed closes")
        else:
            self.axis_x.setRange(max(0.5, start + 0.5), max(2, len(bars) + 0.5))
            if mode == "Candles":
                series = QCandlestickSeries()
                series.setName("Actual adjusted OHLC")
                series.setIncreasingColor(QColor(GREEN))
                series.setDecreasingColor(QColor(ROSE))
                for i, bar in enumerate(bars[start:], start):
                    series.append(QCandlestickSet(bar.open, bar.high, bar.low, bar.close, i + 1))
                self.chart.addSeries(series)
                series.attachAxis(self.axis_x)
                series.attachAxis(self.axis_y)
                y_values = [p for bar in bars[start:] for p in (bar.low, bar.high)]
            else:
                points = [
                    (float(i + 1), bar.volume if mode == "Volume" else bar.close)
                    for i, bar in enumerate(bars[start:], start)
                ]
                self.plot(
                    "Reported volume" if mode == "Volume" else "Adjusted close",
                    points,
                    ACCENT,
                    hover_dates=tuple(b.session for b in bars),
                )
                y_values = [value for _, value in points]
            if mode != "Volume":
                if self.study.currentIndex() > 0:
                    for j, (name, values) in enumerate(rule_guides(bars, self.study.currentText())):
                        segment: list[tuple[float, float]] = []
                        for i in range(start, len(values)):
                            value = values[i]
                            if value is not None:
                                segment.append((float(i + 1), value))
                                y_values.append(value)
                            elif segment:
                                self.plot(
                                    name.replace("day", "bar"), segment, (YELLOW, ROSE, TEXT)[j % 3]
                                )
                                segment = []
                        if segment:
                            self.plot(
                                name.replace("day", "bar"), segment, (YELLOW, ROSE, TEXT)[j % 3]
                            )
                for level in self.levels:
                    self.plot(
                        f"Manual level {level:g}",
                        [(start + 0.5, level), (len(bars) + 0.5, level)],
                        TEXT,
                    )
                    y_values.append(level)
                if self.timeframe.currentText() == "Daily":
                    for a, av, b, bv in self.lines:
                        self.plot("Manual line", [(float(a), av), (float(b), bv)], YELLOW)
                        y_values.extend((av, bv))
        if y_values:
            low, high = min(y_values), max(y_values)
            pad = max((high - low) * 0.06, abs(high) * 0.01, 0.01)
            self.axis_y.setRange(low - pad, high + pad)
        earlier = prefix[self.measure_from.value() - 1]
        latest = prefix[-1]
        self.chart_detail.setText(
            f"Daily close measurement {earlier.session} -> {latest.session}: "
            f"INR {latest.close - earlier.close:+,.4f} "
            f"({100 * (latest.close / earlier.close - 1):+.2f}%). "
            f"{len(self.levels)} levels; {len(self.lines)} lines (lines shown on daily price only)."
        )

    def build_alerts(self) -> None:
        layout = self.page(
            "Historical completed-CLOSE crossings, NOT live alerts. No email, automated "
            "action or app-closed monitoring. Crossings only appear as their sessions are revealed."
        )
        controls = QHBoxLayout()
        self.alert_direction = combo(["Cross above", "Cross below"])
        self.alert_level = spin(100)
        add = QPushButton("Add close-crossing study")
        add.clicked.connect(self.add_alert)
        for widget in (self.alert_direction, self.alert_level, add):
            controls.addWidget(widget)
        layout.addLayout(controls)
        self.alert_table = table(["Condition", "Level", "Revealed crossings", "Observed dates"])
        layout.addWidget(self.alert_table)
        clear = QPushButton("Clear alert studies")
        clear.clicked.connect(self.clear_alerts)
        layout.addWidget(clear)

    def add_alert(self) -> None:
        if self.data is None:
            self.error(DataError("Capture history before adding a historical alert study."))
            return
        alert = (self.alert_direction.currentText(), self.alert_level.value())
        if alert not in self.alerts:
            self.alerts.append(alert)
        self.refresh_alerts()

    def clear_alerts(self) -> None:
        self.alerts.clear()
        self.refresh_alerts()

    def refresh_alerts(self) -> None:
        values = []
        for direction, level in self.alerts:
            dates = crossings(self.prefix(), level, direction)
            values.append([direction, f"{level:g}", str(len(dates)), ", ".join(map(str, dates))])
        rows(self.alert_table, values)

    def build_orders(self) -> None:
        layout = self.page(
            "OPENING-ONLY order lab: submit after the revealed close; advance to a later open. "
            "No intraday touches, partial fills, cash reservation, liquidity or settlement model. "
            "Long/cash; fractional ADJUSTED research units, not literal historical shares."
        )
        settings = QHBoxLayout()
        self.paper_capital, self.paper_fee, self.paper_slip = (
            spin(10000),
            spin(10, 0, 9999),
            spin(10, 0, 9999),
        )
        for text, widget in (
            ("Capital INR", self.paper_capital),
            ("Fee bps", self.paper_fee),
            ("Slippage bps", self.paper_slip),
        ):
            settings.addWidget(note(text))
            settings.addWidget(widget)
        reset = QPushButton("Start / reset paper account")
        reset.clicked.connect(self.reset_account)
        settings.addWidget(reset)
        layout.addLayout(settings)
        layout.addWidget(
            note("Settings above apply ONLY on Start/reset. Active assumptions are shown below.")
        )
        fields = QHBoxLayout()
        self.side = combo(["Buy", "Sell"])
        self.order_kind = combo(["Market", "Limit", "Stop market", "Stop limit"])
        self.quantity, self.limit_price, self.trigger_price = spin(1), spin(100), spin(100)
        self.validity = combo(["Next opening", "Until cancelled"])
        for name, order_widget in (
            ("Side", self.side),
            ("Type", self.order_kind),
            ("Units", self.quantity),
            ("Limit", self.limit_price),
            ("Trigger", self.trigger_price),
            ("Local validity", self.validity),
        ):
            column = QVBoxLayout()
            column.addWidget(note(name))
            column.addWidget(order_widget)
            fields.addLayout(column)
        layout.addLayout(fields)
        self.order_kind.currentTextChanged.connect(self.order_fields)
        self.order_fields()
        actions = QHBoxLayout()
        self.submit_order = QPushButton("Queue paper instruction (no real order)")
        self.submit_order.clicked.connect(self.queue_order)
        actions.addWidget(self.submit_order)
        cancel = QPushButton("Cancel selected pending row")
        cancel.clicked.connect(self.cancel_order)
        actions.addWidget(cancel)
        export = QPushButton("Export session as new JSON")
        export.clicked.connect(self.export_session)
        actions.addWidget(export)
        layout.addLayout(actions)
        self.holdings = note("No paper history captured")
        layout.addWidget(self.holdings)
        self.order_table = table(
            [
                "#",
                "Submitted",
                "Side",
                "Type / local validity",
                "Units",
                "Limit / trigger",
                "Status / updated",
                "Fill / fee INR",
                "Reason",
            ]
        )
        layout.addWidget(self.order_table, 1)

    def order_fields(self) -> None:
        kind = self.order_kind.currentText()
        self.limit_price.setEnabled(kind in ("Limit", "Stop limit"))
        self.trigger_price.setEnabled(kind in ("Stop market", "Stop limit"))

    def reset_account(self) -> None:
        if self.data is None:
            self.error(DataError("Capture real history first."))
        elif self.confirm_reset():
            self.activate(self.data)
            self.status.setText(
                "New account; clock reset to first observed close. Unsaved exercise discarded."
            )

    def queue_order(self) -> None:
        if self.data is None:
            self.error(DataError("Capture actual history first."))
            return
        if self.replay_index == len(self.data.candles) - 1:
            self.error(
                DataError("No later observation for a paper fill. Reset or capture a wider range.")
            )
            return
        sides: tuple[Side, ...] = ("Buy", "Sell")
        kinds: tuple[OrderType, ...] = ("Market", "Limit", "Stop market", "Stop limit")
        try:
            self.account.submit(
                self.prefix()[-1].session,
                sides[self.side.currentIndex()],
                kinds[self.order_kind.currentIndex()],
                self.quantity.value(),
                self.limit_price.value() if self.limit_price.isEnabled() else None,
                self.trigger_price.value() if self.trigger_price.isEnabled() else None,
                "Next opening" if self.validity.currentIndex() == 0 else "Until cancelled",
            )
            self.refresh_orders()
            self.status.setText(
                "Paper instruction queued. Not a fill: advance to the next actual observation."
            )
        except DataError as error:
            self.error(error)

    def cancel_order(self) -> None:
        item = self.order_table.item(self.order_table.currentRow(), 0)
        try:
            if item is None:
                raise DataError("Select a pending order row.")
            self.account.cancel(int(item.text()))
            self.refresh_orders()
            self.status.setText("Pending instruction cancelled locally.")
        except DataError as error:
            self.error(error)

    def refresh_orders(self) -> None:
        bars = self.prefix()
        if bars:
            self.holdings.setText(
                f"ACTIVE: capital INR {self.account.capital:,.2f}; "
                f"fee {self.account.fee_bps:g} bps; "
                f"slippage {self.account.slippage_bps:g} bps\n"
                + self.account.summary(bars[-1].close)
            )
        rows(
            self.order_table,
            [
                [
                    str(o.number),
                    str(o.submitted),
                    o.side,
                    f"{o.kind} / {o.validity}",
                    f"{o.units:g}",
                    f"{o.limit if o.limit is not None else '-'} / "
                    f"{o.trigger if o.trigger is not None else '-'}",
                    f"{o.status} / {o.updated}",
                    (f"{o.price:,.4f}" if o.price is not None else "-") + f" / {o.fee:.4f}",
                    o.message,
                ]
                for o in self.account.orders
            ],
        )

    def session_document(self) -> dict[str, object]:
        if self.data is None:
            raise DataError("No captured history to export.")
        return {
            "schema": 1,
            "kind": "opening-only educational paper exercise",
            "limitations": [
                "Not a broker/exchange simulator. Assumed full opening fills, no intraday touches.",
                "Adjusted research units; no settlement, queue, liquidity, tax or reservations.",
                "Full captured history includes FUTURE observations beyond the revealed cursor.",
                "Observations/provenance are supplied claims, not independently authenticated.",
                "Read-only evidence export; no session import/resume is implemented.",
            ],
            "data": asdict(self.data),
            "revealed_session": str(self.prefix()[-1].session),
            "capital": self.account.capital,
            "fee_bps": self.account.fee_bps,
            "slippage_bps": self.account.slippage_bps,
            "cash": self.account.cash,
            "units": self.account.units,
            "remaining_cost": self.account.cost,
            "realised_pnl": self.account.realised,
            "fees": self.account.fees,
            "orders": [asdict(o) for o in self.account.orders],
            "equity_marks": self.equity_marks,
            "alerts": self.alerts,
            "horizontal_levels": self.levels,
            "daily_session_lines": self.lines,
            "chart_settings": {
                "mode": self.chart_mode.currentText(),
                "timeframe": self.timeframe.currentText(),
                "study": self.study.currentText(),
                "visible_bars": self.visible.value(),
                "measure_from_daily_session": self.measure_from.value(),
            },
            "comparison_snapshot": (
                asdict(self.snapshots[self.compare_stock.currentText()])
                if self.chart_mode.currentText() == "Compare (100)"
                and self.compare_stock.currentText() in self.snapshots
                else None
            ),
        }

    def export_session(self) -> None:
        if self.data is None:
            self.error(DataError("Capture actual history first."))
            return
        filename, _ = QFileDialog.getSaveFileName(
            self, "New paper session JSON", "", "JSON (*.json)"
        )
        if not filename:
            return
        try:
            document = self.session_document()
            text = json.dumps(
                document, indent=2, allow_nan=False, default=lambda value: value.isoformat()
            )
            with Path(filename).open("x", encoding="utf-8") as handle:
                handle.write(text)
            self.status.setText(
                f"Saved evidence (includes future captured bars): {Path(filename).resolve()}"
            )
        except (OSError, ValueError) as error:
            self.error(error)

    def build_risk(self) -> None:
        layout = self.page(
            "Manual hypothetical LONG plan. Planned stop loss is NOT a guaranteed loss cap: "
            "gaps, liquidity and unmodelled taxes/charges can make losses larger. "
            "These inputs are assumptions, not fetched prices or personal recommendations."
        )
        columns = QHBoxLayout()
        sizing = QFormLayout()
        self.risk_capital, self.risk_percent = spin(10000), spin(1, 0.0001, 100)
        self.risk_entry, self.risk_stop, self.risk_target = spin(100), spin(95), spin(110)
        self.risk_fee, self.risk_slip = spin(10, 0, 9999), spin(10, 0, 9999)
        for title, widget in (
            ("Capital INR", self.risk_capital),
            ("Risk budget %", self.risk_percent),
            ("Assumed entry", self.risk_entry),
            ("Assumed stop", self.risk_stop),
            ("Assumed target", self.risk_target),
            ("Fee each side bps", self.risk_fee),
            ("Slippage each side bps", self.risk_slip),
        ):
            sizing.addRow(title, widget)
        calculate = QPushButton("Calculate risk and quantity")
        calculate.clicked.connect(self.calculate_risk)
        sizing.addRow(calculate)
        columns.addLayout(sizing)
        allocation_form = QFormLayout()
        self.allocation_capital = spin(10000)
        self.weights = QLineEdit("40, 30, 20")
        allocation_form.addRow("Capital INR", self.allocation_capital)
        allocation_form.addRow("Percentage weights (comma-separated)", self.weights)
        allocation_form.addRow(
            note("Positions 1, 2, ... are budgets, not purchases. Sum may be below 100%.")
        )
        allocate = QPushButton("Calculate budgets and cash reserve")
        allocate.clicked.connect(self.calculate_allocation)
        allocation_form.addRow(allocate)
        columns.addLayout(allocation_form)
        layout.addLayout(columns)
        self.risk_output, self.allocation_output = QTextBrowser(), QTextBrowser()
        outputs = QHBoxLayout()
        outputs.addWidget(self.risk_output)
        outputs.addWidget(self.allocation_output)
        layout.addLayout(outputs)
        self.calculate_risk()
        self.calculate_allocation()

    def calculate_risk(self) -> None:
        try:
            result = position_size(
                self.risk_capital.value(),
                self.risk_percent.value(),
                self.risk_entry.value(),
                self.risk_stop.value(),
                self.risk_target.value(),
                self.risk_fee.value(),
                self.risk_slip.value(),
            )
            self.risk_output.setPlainText(
                f"Illustrative whole units: {result.units}\n"
                f"Risk budget INR {result.risk_budget:,.2f}\n"
                f"Planned loss at assumed stop INR {result.planned_loss:,.2f}\n"
                f"Cash required including entry costs INR {result.cash_needed:,.2f}\n"
                f"Net reward / planned risk: {result.reward_risk:.3f}\n"
                f"Break-even exit reference INR {result.break_even:,.4f}\n\n"
                "Integer sizing is a manual nominal-price plan. Historical paper/strategy "
                "units are adjusted research units, NOT directly interchangeable."
            )
        except DataError as error:
            self.risk_output.setPlainText(f"INVALID PLAN: {error}")
            self.error(error)

    def calculate_allocation(self) -> None:
        try:
            weights = tuple(float(part.strip()) for part in self.weights.text().split(","))
            budgets = allocation(self.allocation_capital.value(), weights)
            self.allocation_output.setPlainText(
                "\n".join(
                    f"Budget {i + 1}: {weight:g}% = INR {value:,.2f}"
                    for i, (weight, value) in enumerate(zip(weights, budgets, strict=True))
                )
                + f"\nUnallocated cash INR {self.allocation_capital.value() - sum(budgets):,.2f}"
                "\n\nBudget arithmetic only. No trades, market returns, diversification "
                "guarantee, shared-cash basket test or scheduling."
            )
        except ValueError as error:
            self.allocation_output.setPlainText(f"INVALID ALLOCATION: {error}")
            self.error(error)

    def build_scenarios(self) -> None:
        layout = self.page(
            "MANUAL SCENARIOS ONLY. Neither panel downloads data. Depth cannot be recovered "
            "from daily candles. Options are expiry arithmetic, NOT live option prices, "
            "Greeks, margin or a recommendation to trade derivatives."
        )
        columns = QHBoxLayout()
        depth = QFormLayout()
        self.bids = QLineEdit("99:10, 98:20")
        self.asks = QLineEdit("101:15, 102:25")
        depth.addRow("Manual bids price:quantity", self.bids)
        depth.addRow("Manual asks price:quantity", self.asks)
        depth.addRow(note("Comma-separated positive price:quantity pairs. No real order book."))
        button = QPushButton("Inspect manual spread")
        button.clicked.connect(self.calculate_depth)
        depth.addRow(button)
        self.depth_output = QTextBrowser()
        depth.addRow(self.depth_output)
        columns.addLayout(depth)
        options = QFormLayout()
        self.option_kind = combo(["Long call", "Long put"])
        self.strike, self.premium, self.settlement = spin(100), spin(5, 0), spin(110)
        self.option_units = QSpinBox()
        self.option_units.setRange(1, 1000000)
        self.option_units.setValue(1)
        for name, widget in (
            ("Bought option", self.option_kind),
            ("Strike", self.strike),
            ("Premium per underlying unit", self.premium),
            ("Total underlying units (lots x lot size)", self.option_units),
            ("Assumed expiry settlement", self.settlement),
        ):
            options.addRow(name, widget)
        button = QPushButton("Calculate expiry scenarios")
        button.clicked.connect(self.calculate_option)
        options.addRow(button)
        self.option_output = QTextBrowser()
        options.addRow(self.option_output)
        columns.addLayout(options)
        layout.addLayout(columns)
        self.calculate_depth()
        self.calculate_option()

    def calculate_depth(self) -> None:
        try:
            parsed = []
            for field in (self.bids, self.asks):
                levels = []
                for pair in field.text().split(","):
                    parts = pair.split(":")
                    if len(parts) != 2:
                        raise DataError("Use price:quantity pairs, separated by commas.")
                    levels.append((float(parts[0]), float(parts[1])))
                parsed.append(tuple(levels))
            bid, ask, spread = depth_summary(parsed[0], parsed[1])
            self.depth_output.setPlainText(
                f"MANUAL INPUTS, NOT MARKET DATA\n"
                f"Best bid {bid:g}; best ask {ask:g}; spread {spread:g}\n"
                f"Total displayed bid quantity {sum(q for _, q in parsed[0]):g}\n"
                f"Total displayed ask quantity {sum(q for _, q in parsed[1]):g}\n\n"
                "Quantities can disappear. Depth does not guarantee fills or predict direction."
            )
        except ValueError as error:
            self.depth_output.setPlainText(f"INVALID SCENARIO: {error}")
            self.error(error)

    def calculate_option(self) -> None:
        kind = self.option_kind.currentText()
        strike, premium, units = (
            self.strike.value(),
            self.premium.value(),
            self.option_units.value(),
        )
        try:
            pnl = option_payoff(kind, strike, premium, units, self.settlement.value())
            scenarios = [
                (strike * factor, option_payoff(kind, strike, premium, units, strike * factor))
                for factor in (0.5, 0.75, 0.9, 1, 1.1, 1.25, 1.5)
            ]
            even = strike + premium if kind == "Long call" else strike - premium
            self.option_output.setHtml(
                f"<h3>{escape(kind)}: manual expiry P&amp;L INR {pnl:+,.2f}</h3>"
                f"<p>Premium paid / maximum premium loss INR {premium * units:,.2f}. "
                f"Arithmetic break-even {even:,.4f} "
                "(a nonpositive put break-even is not a positive settlement price).</p>"
                "<table><tr><th>Assumed settlement</th><th>P&amp;L before costs</th></tr>"
                + "".join(
                    f"<tr><td>{price:,.2f}</td><td>{value:+,.2f}</td></tr>"
                    for price, value in scenarios
                )
                + "</table><p>No fees, lot discovery, pre-expiry valuation or physical "
                "delivery funding model. Exercise obligations can require additional funds.</p>"
            )
        except DataError as error:
            self.option_output.setPlainText(f"INVALID SCENARIO: {error}")
            self.error(error)
