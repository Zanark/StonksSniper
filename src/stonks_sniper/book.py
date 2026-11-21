from __future__ import annotations

import logging
from html import escape

from PySide6.QtCore import QDate, QObject, Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from stonks_sniper.fundamentals import FundamentalSnapshot, YahooFundamentalsProvider
from stonks_sniper.glossary import HelpBrowser
from stonks_sniper.graham import (
    BOOK_LESSONS,
    FIELDS,
    SCOPE,
    SOURCES,
    equal_money,
    evaluate,
    real_return,
    rebalance,
)
from stonks_sniper.models import DataError
from stonks_sniper.providers import yahoo_symbol
from stonks_sniper.theme import ACCENT

LOGGER = logging.getLogger(__name__)


def book_html(index: int) -> str:
    lesson = BOOK_LESSONS[index]
    return (
        f"<h1>Chapter {lesson.chapter}: {escape(lesson.title)}</h1>"
        f"<p>{escape(SCOPE)}</p>"
        f"<h2>ELI15: the idea</h2><p>{escape(lesson.idea)}</p>"
        f"<h2>Imagine this (illustrative, not market data)</h2><p>{escape(lesson.example)}</p>"
        f"<h2>Apply it to an Indian stock</h2><p>{escape(lesson.practical)}</p>"
        f"<h2>What this does NOT prove</h2><p>{escape(lesson.caution)}</p>"
        "<h2>Read alongside your copy</h2>"
        + "".join(
            f'<p><a style="color:{ACCENT}" href="{escape(SOURCES[key][1])}">'
            f"{escape(SOURCES[key][0])}</a></p>"
            for key in ("edition", *lesson.sources)
        )
        + "<p>Use the Fundamental workbook for calculations and evidence checks. "
        "Conceptual chapters provide research tasks, not invented daily trading algorithms.</p>"
    )


class FundamentalWorker(QObject):
    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, provider: YahooFundamentalsProvider, symbol: str, exchange: str) -> None:
        super().__init__()
        self.provider = provider
        self.symbol = symbol
        self.exchange = exchange

    @Slot()
    def run(self) -> None:
        try:
            self.succeeded.emit(self.provider.fetch(self.symbol, self.exchange))
        except Exception as error:
            LOGGER.exception("Fundamental reference fetch failed")
            self.failed.emit(f"{type(error).__name__}: {error}")
        finally:
            self.finished.emit()


class BookCompanion(QTabWidget):
    def __init__(self) -> None:
        super().__init__()
        self.provider = YahooFundamentalsProvider()
        self.fetch_thread: QThread | None = None
        self.worker: FundamentalWorker | None = None
        self.snapshot: FundamentalSnapshot | None = None
        self.field_sources: dict[str, str] = {}
        self.report_html = ""
        reading = QWidget()
        reading_layout = QHBoxLayout(reading)
        self.chapters = QListWidget()
        self.chapters.setWordWrap(True)
        self.chapters.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chapters.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.chapters.setFixedWidth(290)
        self.chapters.addItems([f"{item.chapter}. {item.title}" for item in BOOK_LESSONS])
        self.chapter_text = HelpBrowser()
        self.chapters.currentRowChanged.connect(self.chapter_selected)
        reading_layout.addWidget(self.chapters)
        reading_layout.addWidget(self.chapter_text, 1)
        self.addTab(reading, "Read alongside the book")
        workbook = QWidget()
        layout = QVBoxLayout(workbook)
        note = QLabel(
            "Current fundamental research, NOT a historical simulation or an order. "
            "Blank = unknown; numbers are not independently audited. "
            "Review dates, INR units, consolidated accounts and share/split basis."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        identity = QHBoxLayout()
        self.stock = QLineEdit("RELIANCE")
        self.stock.setMaximumWidth(150)
        self.stock.setAccessibleName("Fundamental research stock")
        self.exchange = QComboBox()
        self.exchange.addItems(["NSE", "BSE"])
        self.copy_stock = QPushButton("Use Explore stock")
        self.copy_stock.setToolTip("Copies the Explore ticker/market and clears this workbook.")
        self.load_button = QPushButton("Fetch latest reference")
        self.load_button.clicked.connect(self.fetch_reference)
        identity.addWidget(QLabel("Stock"))
        identity.addWidget(self.stock)
        identity.addWidget(self.exchange)
        identity.addWidget(self.copy_stock)
        identity.addWidget(self.load_button)
        layout.addLayout(identity)
        self.stock.textChanged.connect(self.identity_changed)
        self.exchange.currentTextChanged.connect(self.identity_changed)
        self.provenance = QLabel(
            "No reference loaded. Enter sourced figures manually or fetch Yahoo reference data. "
            "Weekend/closed-market requests use the latest available prior daily close."
        )
        self.provenance.setWordWrap(True)
        self.provenance.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.provenance)
        self.classification = QComboBox()
        self.classification.addItems(
            [
                "Unclassified: industrial screens disabled",
                "Non-financial industrial (I verified this)",
                "Bank / insurer / utility / other: screens disabled",
            ]
        )
        self.classification.currentIndexChanged.connect(self.invalidate)
        layout.addWidget(self.classification)
        split = QSplitter(Qt.Orientation.Horizontal)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_widget = QWidget()
        form = QFormLayout(form_widget)
        self.evidence = QLineEdit()
        self.evidence.setPlaceholderText("Annual report / URL / page, or explicit scenario")
        self.evidence.textChanged.connect(self.invalidate)
        form.addRow("Manual evidence/source", self.evidence)
        self.as_of = QDateEdit(QDate.currentDate())
        self.as_of.setDisplayFormat("yyyy-MM-dd")
        self.as_of.setCalendarPopup(True)
        self.as_of.dateChanged.connect(self.invalidate)
        form.addRow("Manual evidence as-of", self.as_of)
        self.fields: dict[str, QLineEdit] = {}
        for field in FIELDS:
            entry = QLineEdit()
            entry.setPlaceholderText("Unknown (leave blank)")
            entry.setAccessibleName(field.title)
            entry.setToolTip(field.help + " Plain decimal numbers; no currency symbols or commas.")
            entry.textChanged.connect(lambda _text, key=field.key: self.field_edited(key))
            self.fields[field.key] = entry
            form.addRow(field.title, entry)
        scroll.setWidget(form_widget)
        split.addWidget(scroll)
        self.results = HelpBrowser()
        split.addWidget(self.results)
        split.setSizes([470, 800])
        layout.addWidget(split, 1)
        actions = QHBoxLayout()
        self.calculate = QPushButton("Calculate / check evidence")
        self.calculate.clicked.connect(self.calculate_results)
        self.save = QPushButton("Save worksheet HTML")
        self.save.setEnabled(False)
        self.save.clicked.connect(self.save_report)
        self.clear_button = QPushButton("Clear figures")
        self.clear_button.clicked.connect(self.clear_figures)
        for button in (self.calculate, self.save, self.clear_button):
            actions.addWidget(button)
        layout.addLayout(actions)
        self.addTab(workbook, "Fundamental workbook")
        self.build_scenarios()
        self.chapters.setCurrentRow(0)
        self.invalidate()

    @Slot(int)
    def chapter_selected(self, index: int) -> None:
        if 0 <= index < len(BOOK_LESSONS):
            self.chapter_text.setHtml(book_html(index))

    @Slot()
    def invalidate(self) -> None:
        self.report_html = ""
        self.save.setEnabled(False)
        self.save.setText("Save worksheet HTML")
        self.results.setPlainText(
            "No current calculation. Enter evidence and figures, then Calculate. "
            "Changing an input clears the old result. Unknown facts cannot pass a screen."
        )

    def field_edited(self, key: str) -> None:
        self.field_sources.pop(key, None)
        self.invalidate()

    @Slot()
    def clear_figures(self) -> None:
        for entry in self.fields.values():
            entry.clear()
        self.field_sources.clear()
        self.snapshot = None
        self.classification.setCurrentIndex(0)
        self.evidence.clear()
        self.provenance.setText("Figures cleared. No reference loaded or earlier result reused.")
        self.provenance.setToolTip("")
        self.invalidate()

    @Slot()
    def identity_changed(self) -> None:
        self.clear_figures()

    def set_stock(self, symbol: str, exchange: str) -> None:
        self.stock.setText(symbol)
        self.exchange.setCurrentText(exchange)
        self.clear_figures()
        self.setCurrentIndex(1)

    @Slot()
    def fetch_reference(self) -> None:
        if self.fetch_thread is not None:
            return
        try:
            symbol = yahoo_symbol(self.stock.text(), self.exchange.currentText())
        except DataError as error:
            self.provenance.setText(str(error))
            return
        self.clear_figures()
        self.provenance.setText(f"Fetching actual {symbol} reference. No earlier values reused.")
        for widget in (
            self.stock,
            self.exchange,
            self.copy_stock,
            self.load_button,
            self.clear_button,
        ):
            widget.setEnabled(False)
        for control in (
            self.evidence,
            self.as_of,
            self.classification,
            self.calculate,
            *self.fields.values(),
        ):
            control.setEnabled(False)
        self.fetch_thread = QThread(self)
        self.worker = FundamentalWorker(self.provider, symbol, self.exchange.currentText())
        self.worker.moveToThread(self.fetch_thread)
        self.fetch_thread.started.connect(self.worker.run)
        self.worker.succeeded.connect(self.reference_ready)
        self.worker.failed.connect(self.reference_failed)
        self.worker.finished.connect(self.fetch_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.fetch_thread.finished.connect(self.reference_finished)
        self.fetch_thread.finished.connect(self.fetch_thread.deleteLater)
        self.fetch_thread.start()

    @Slot(object)
    def reference_ready(self, snapshot: FundamentalSnapshot) -> None:
        self.snapshot = snapshot
        for item in snapshot.values:
            field = self.fields[item.key]
            field.blockSignals(True)
            field.setText(format(item.value, ".15g"))
            field.blockSignals(False)
            self.field_sources[item.key] = item.source
        if snapshot.sector == "Financial Services":
            self.classification.setCurrentIndex(2)
        self.provenance.setText(
            f"{snapshot.symbol} / {snapshot.exchange} / INR | Sector: {snapshot.sector}\n"
            f"Completed close: {snapshot.price_session}; "
            f"fetched {snapshot.fetched_at.isoformat()}. "
            "Statement period ends are listed with each imported input in the calculation. "
            "Missing fields require sourced manual evidence. No historical backtest."
        )
        self.provenance.setToolTip("\n".join(snapshot.warnings))
        self.invalidate()

    @Slot(str)
    def reference_failed(self, message: str) -> None:
        self.provenance.setText(f"REFERENCE UNAVAILABLE: {message}. No substitute data used.")

    @Slot()
    def reference_finished(self) -> None:
        # finished can arrive before native thread-local cleanup has completed.
        if self.fetch_thread is not None:
            self.fetch_thread.wait()
        self.fetch_thread = None
        self.worker = None
        for widget in (
            self.stock,
            self.exchange,
            self.copy_stock,
            self.load_button,
            self.clear_button,
        ):
            widget.setEnabled(True)
        for control in (
            self.evidence,
            self.as_of,
            self.classification,
            self.calculate,
            *self.fields.values(),
        ):
            control.setEnabled(True)

    @Slot()
    def calculate_results(self) -> None:
        self.invalidate()
        try:
            symbol = yahoo_symbol(self.stock.text(), self.exchange.currentText())
            values: dict[str, float] = {}
            for field in FIELDS:
                text = self.fields[field.key].text().strip()
                if text:
                    try:
                        values[field.key] = float(text)
                    except ValueError as error:
                        raise DataError(f"{field.title}: enter a plain decimal number.") from error
            manual = set(values) - self.field_sources.keys()
            if manual and not self.evidence.text().strip():
                raise DataError(
                    "Give a source/report/page or explicitly label manual scenario inputs."
                )
            if not values:
                raise DataError("Enter figures or fetch a reference first.")
            sections = evaluate(values, industrial=self.classification.currentIndex() == 1)
        except (ValueError, DataError) as error:
            self.results.setPlainText(f"Cannot calculate: {error}")
            return
        colors = {"Pass": "#6ce9a6", "Fail": "#ff9d9d", "Unknown": "#f0d484"}
        html = (
            f"<h1>{escape(symbol)}: fundamental study</h1><p>{escape(SCOPE)}</p>"
            "<p><b>No overall buy/sell rating.</b> Pass means only the displayed arithmetic "
            "met that check. These present-day facts are never fed into historical Simulate. "
            "Historical thresholds, subjective classifications and manual evidence "
            "require review.</p>"
            f"<p>Classification: {escape(self.classification.currentText())}.</p>"
        )
        if self.snapshot:
            html += f"<p>{escape(self.provenance.text())}</p>"
            html += "".join(f"<p>{escape(warning)}</p>" for warning in self.snapshot.warnings)
        html += "<h2>Inputs and provenance</h2>"
        for field in FIELDS:
            if field.key in values:
                source = self.field_sources.get(field.key)
                if source is None:
                    source = (
                        f"USER INPUT: {self.evidence.text()}; "
                        f"manual as-of {self.as_of.date().toString('yyyy-MM-dd')}"
                    )
                html += (
                    f"<p><b>{escape(field.title)}</b>: {values[field.key]:,.8g}<br>"
                    f"{escape(source)}</p>"
                )
        for heading, rows in sections.items():
            html += f"<h2>{heading}</h2>"
            for row in rows:
                html += (
                    f'<h3>{escape(row.title)}: <span style="color:'
                    f'{colors.get(row.status, "#c8e8ed")}">{row.status}</span></h3>'
                    f"<p>{escape(row.detail)}</p>"
                )
        html += "<h2>Sources and boundaries</h2>"
        html += "".join(
            f'<p><a style="color:{ACCENT}" href="{escape(url)}">{escape(title)}</a></p>'
            for title, url in SOURCES.values()
        )
        self.report_html = html
        self.results.setHtml(html)
        self.save.setEnabled(True)

    @Slot()
    def save_report(self) -> None:
        from pathlib import Path

        if not self.report_html:
            return
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save fundamental worksheet", "fundamental-study.html", "HTML (*.html)"
        )
        if not filename:
            return
        document = (
            '<!doctype html><html lang="en"><meta charset="utf-8">'
            "<title>Stonks Sniper fundamental study</title><body>"
            + self.report_html
            + "</body></html>"
        )
        try:
            Path(filename).write_text(document, encoding="utf-8")
        except OSError as error:
            LOGGER.exception("Fundamental worksheet export failed")
            QMessageBox.critical(self, "Worksheet export failed", str(error))
            return
        self.save.setText("Worksheet saved")
        self.save.setToolTip(f"Saved worksheet: {filename}")

    def build_scenarios(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        description = QLabel(
            "Optional arithmetic exercises, not fetched market data. Enter your own assumptions. "
            "No fees, taxes, fractional-share restrictions or live portfolio execution "
            "are modelled."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        self.exercise = QComboBox()
        self.exercise.addItems(["Inflation", "Allocation", "Equal-money purchases"])
        layout.addWidget(self.exercise)
        self.exercise_help = QLabel()
        self.exercise_help.setWordWrap(True)
        layout.addWidget(self.exercise_help)
        form = QFormLayout()
        self.exercise_inputs = [QLineEdit() for _ in range(3)]
        for name, entry in zip(("A", "B", "C"), self.exercise_inputs, strict=True):
            entry.setPlaceholderText("Enter your own assumption")
            entry.textChanged.connect(self.clear_exercise)
            form.addRow(name, entry)
        layout.addLayout(form)
        run = QPushButton("Calculate exercise")
        run.clicked.connect(self.calculate_exercise)
        layout.addWidget(run)
        self.exercise_result = QLabel()
        self.exercise_result.setWordWrap(True)
        self.exercise_result.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.exercise_result)
        layout.addStretch()
        self.exercise.currentIndexChanged.connect(self.exercise_changed)
        self.exercise_changed()
        self.addTab(page, "Portfolio and inflation exercises")

    @Slot()
    def clear_exercise(self) -> None:
        self.exercise_result.setText("No current exercise result.")

    @Slot()
    def exercise_changed(self) -> None:
        index = self.exercise.currentIndex()
        self.exercise_help.setText(
            (
                "A = nominal return %, B = inflation %. Real return = "
                "[(1 + A/100) / (1 + B/100) - 1] x 100. C is unused.",
                "A = current shares value INR, B = fixed-income value INR, C = target shares %. "
                "Transfer = (A+B) x C/100 - A. Positive: add to shares; negative: reduce shares. "
                "Your target is an assumption, not a personal recommendation.",
                "A = equal INR invested at EACH purchase, B = comma-separated positive prices. "
                "Units = sum(A / each price); average cost = total money / units. "
                "C is unused. Illustrative fractional units, not broker orders.",
            )[index]
        )
        for entry in self.exercise_inputs:
            entry.clear()
        self.exercise_inputs[2].setEnabled(index == 1)
        self.clear_exercise()

    @Slot()
    def calculate_exercise(self) -> None:
        a, b, c = (entry.text().strip() for entry in self.exercise_inputs)
        try:
            index = self.exercise.currentIndex()
            if index == 0:
                text = f"Real purchasing-power return: {real_return(float(a), float(b)):,.4f}%."
            elif index == 1:
                transfer = rebalance(float(a), float(b), float(c))
                text = (
                    f"Signed transfer to shares: INR {transfer:,.2f}. "
                    "Positive = add to shares; negative = move from shares to fixed income. "
                    "Before fees/taxes; no transactions executed."
                )
            else:
                units, average = equal_money(
                    float(a), tuple(float(x.strip()) for x in b.split(","))
                )
                text = (
                    f"Illustrative units: {units:,.6f}; average cost INR {average:,.4f}. "
                    "This does not calculate a return or guarantee a profit."
                )
        except (ValueError, DataError) as error:
            self.exercise_result.setText(f"Cannot calculate exercise: {error}")
            return
        self.exercise_result.setText(text)
