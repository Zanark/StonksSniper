from __future__ import annotations

import json
import logging
import sys
from dataclasses import asdict
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from statistics import fmean, pstdev

from PySide6.QtCharts import (
    QAreaSeries,
    QCandlestickSeries,
    QCandlestickSet,
    QChart,
    QChartView,
    QDateTimeAxis,
    QLineSeries,
    QScatterSeries,
    QValueAxis,
)
from PySide6.QtCore import (
    QDate,
    QDateTime,
    QEasingCurve,
    QMargins,
    QObject,
    QSize,
    Qt,
    QThread,
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtGui import QBrush, QCloseEvent, QColor, QFont, QMovie, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from stonks_sniper.engine import Assumptions, Result, simulate
from stonks_sniper.glossary import TERMS, HelpBrowser, explain, search_terms, term_html, tooltip
from stonks_sniper.lessons import LESSONS
from stonks_sniper.models import Candle, DataError, MarketData
from stonks_sniper.patterns import PATTERNS, ema, wilder_rsi
from stonks_sniper.providers import INDIA, MarketDataProvider, YahooDailyProvider
from stonks_sniper.theme import (
    ACCENT,
    BASE,
    GREEN,
    MUTED,
    PANEL,
    ROSE,
    TEXT,
    WARM,
    YELLOW,
    application_icon,
    configure_application,
)

LOGGER = logging.getLogger(__name__)


class FetchWorker(QObject):
    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self, provider: MarketDataProvider, symbol: str, exchange: str, start: date, end: date
    ) -> None:
        super().__init__()
        self.provider = provider
        self.request = (symbol, exchange, start, end)

    @Slot()
    def run(self) -> None:
        try:
            data = self.provider.fetch(*self.request)
            self.succeeded.emit(data)
        except Exception as error:
            LOGGER.exception("Market-data fetch failed")
            self.failed.emit(f"{type(error).__name__}: {error}")
        finally:
            self.finished.emit()


def chart_view() -> QChartView:
    chart = QChart()
    chart.setTheme(QChart.ChartTheme.ChartThemeDark)
    chart.setBackgroundBrush(QColor(PANEL))
    chart.setPlotAreaBackgroundBrush(QColor(PANEL))
    chart.setDropShadowEnabled(False)
    chart.setBackgroundRoundness(0)
    chart.setMargins(QMargins(8, 8, 8, 4))
    chart.setTitleBrush(QColor(WARM))
    chart.setTitleFont(QFont("Segoe UI", 10))
    chart.legend().setLabelColor(QColor(TEXT))
    chart.legend().setFont(QFont("Segoe UI", 9))
    chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
    chart.setAnimationDuration(260)
    chart.setAnimationEasingCurve(QEasingCurve.Type.OutCubic)
    view = QChartView(chart)
    view.setRenderHint(QPainter.RenderHint.Antialiasing)
    view.setMinimumHeight(220)
    view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    return view


def label(text: str, role: str = "quiet", *, help_key: str | None = None) -> QLabel:
    widget = QLabel(text)
    widget.setObjectName(role)
    if help_key:
        widget.setToolTip(tooltip(help_key))
    return widget


def card() -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 12, 16, 12)
    layout.setSpacing(5)
    return frame, layout


def browser() -> HelpBrowser:
    return HelpBrowser()


def lesson_html(index: int, *, complete: bool) -> str:
    pattern = PATTERNS[index]
    lesson = LESSONS[pattern.key]
    heading = "h1" if complete else "h2"
    content = (
        f'<{heading} style="color:{WARM}">{escape(lesson.title)}</{heading}>'
        f"<p>{explain(lesson.idea)}</p>"
        f'<h3 style="color:{ACCENT}">1. When would it buy?</h3>'
        f"<p>{explain(lesson.buy)}</p>"
        f'<h3 style="color:{WARM}">2. When would it sell?</h3>'
        f"<p>{explain(lesson.sell)}</p>"
        "<p>The test only trades when it needs to change what it owns. "
        "It does not buy again every day that the buy rule is true.</p>"
    )
    if complete:
        content += (
            "<h3>Imagine a toy shop (a teaching example, not market data)</h3>"
            f"<p>{explain(TERMS[pattern.key].example)}</p>"
            f"<h3>The numbers, step by step</h3><p>{explain(lesson.example)}</p>"
            f"<h3>Words, explained</h3><p>{explain(lesson.words)}</p>"
        )
    else:
        content += (
            f"<h3>Imagine this</h3><p>{explain(TERMS[pattern.key].example)}</p>"
            "<p>Use <b>Explain pattern</b> for the full lesson. Hover a highlighted "
            "word for its meaning and an everyday example; click to open the dictionary.</p>"
        )
    content += (
        f'<h3 style="color:{YELLOW}">What can go wrong?</h3>'
        f"<p>{explain(lesson.catch)}</p>"
        "<h3>3. What does the test actually do?</h3>"
        "<p>Read the finished day. Make the decision. Buy or sell at the next "
        "available day's opening price, with your chosen costs. No peeking ahead.</p>"
        f"<p>It needs {pattern.minimum_bars} completed trading days to get ready. "
        "It needs one more day before a decision can become a trade.</p>"
    )
    return content


def epoch(session: date) -> float:
    return datetime.combine(session, datetime.min.time(), tzinfo=INDIA).timestamp() * 1000


class MainWindow(QMainWindow):
    def __init__(self, provider: MarketDataProvider | None = None) -> None:
        super().__init__()
        self.provider = provider if provider is not None else YahooDailyProvider()
        self.data: MarketData | None = None
        self.result: Result | None = None
        self.fetch_thread: QThread | None = None
        self.worker: FetchWorker | None = None
        self._animate_next = False
        self.setWindowTitle("StonksSniper | Learn a pattern. Test an idea.")
        self.setWindowIcon(application_icon())
        self.resize(1440, 900)
        self.setMinimumSize(1080, 720)
        root = QWidget()
        outer = QVBoxLayout(root)
        outer.setContentsMargins(22, 14, 22, 12)
        outer.setSpacing(10)
        header = QHBoxLayout()
        self.brand_mark = QLabel()
        self.brand_mark.setFixedSize(46, 46)
        self.brand_mark.setAccessibleName("StonksSniper circular candlestick scope")
        self.brand_movie = QMovie(str(Path(__file__).parent / "assets" / "logo.gif"), parent=self)
        if not self.brand_movie.isValid():
            raise RuntimeError(f"Logo animation could not be loaded: {self.brand_movie.fileName()}")
        self.brand_movie.setScaledSize(QSize(46, 46))
        self.brand_movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.brand_mark.setMovie(self.brand_movie)
        self.brand_movie.start()
        header.addWidget(self.brand_mark)
        brand = QVBoxLayout()
        brand.setSpacing(0)
        brand.addWidget(label("StonksSniper", "brand"))
        brand.addWidget(label("Understand an idea. Try it on real stock history."))
        header.addLayout(brand)
        header.addStretch()
        header.addWidget(label("REAL HISTORY  /  PRACTICE MONEY", "eyebrow"))
        self.motion = QCheckBox("Animations")
        self.motion.setChecked(True)
        self.motion.setToolTip(
            "Optional logo, chart and loading motion. Turn off to stop all animation and replay."
        )
        self.motion.toggled.connect(self.motion_changed)
        header.addWidget(self.motion)
        outer.addLayout(header)
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.stop_playback)
        self.workspace = QStackedWidget()
        self.workspace.addWidget(self.tabs)
        self.loading_page = QWidget()
        loading_layout = QVBoxLayout(self.loading_page)
        loading_layout.addStretch()
        loading_card, loading_content = card()
        loading_card.setFixedWidth(480)
        self.loading_status = label("Loading real stock history...", "section")
        self.loading_status.setTextFormat(Qt.TextFormat.PlainText)
        self.loading_status.setWordWrap(True)
        self.loading_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_content.addWidget(self.loading_status)
        self.loading_movie = QMovie(
            str(Path(__file__).parent / "assets" / "stonks-meme.gif"), parent=self
        )
        if not self.loading_movie.isValid():
            raise RuntimeError(
                f"Loading animation could not be loaded: {self.loading_movie.fileName()}"
            )
        self.loading_movie.setScaledSize(QSize(360, 270))
        self.loading_image = QLabel()
        self.loading_image.setFixedSize(360, 270)
        self.loading_image.setAccessibleName("Stonks meme while stock history loads")
        self.loading_image.setMovie(self.loading_movie)
        loading_content.addWidget(self.loading_image, 0, Qt.AlignmentFlag.AlignHCenter)
        loading_note = label(
            "Getting finished daily prices from Yahoo Finance.\n"
            "Your practice test starts when the download finishes."
        )
        loading_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_note.setWordWrap(True)
        loading_content.addWidget(loading_note)
        loading_layout.addWidget(loading_card, 0, Qt.AlignmentFlag.AlignHCenter)
        loading_layout.addStretch()
        self.workspace.addWidget(self.loading_page)
        outer.addWidget(self.workspace, 1)
        self.setCentralWidget(root)
        self.play_timer = QTimer(self)
        self.play_timer.setInterval(240)
        self.play_timer.timeout.connect(self.advance_replay)
        experiment = QWidget()
        layout = QVBoxLayout(experiment)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(10)
        control_card, control_layout = card()
        controls = QHBoxLayout()
        self.symbol = QLineEdit("RELIANCE")
        self.symbol.setMaximumWidth(130)
        self.symbol.setAccessibleName("Stock symbol")
        self.symbol.setToolTip(tooltip("symbol"))
        self.exchange = QComboBox()
        self.exchange.addItems(["NSE", "BSE"])
        self.exchange.setToolTip(tooltip("exchange"))
        self.exchange.currentTextChanged.connect(self.exchange_changed)
        today = datetime.now(INDIA).date()
        self.start = QDateEdit(QDate(today - timedelta(days=730)))
        self.end = QDateEdit(QDate(today))
        for field in (self.start, self.end):
            field.setCalendarPopup(True)
            field.setDisplayFormat("yyyy-MM-dd")
            field.setToolTip(tooltip("session"))
        self.fetch = QPushButton("1  Load stock")
        self.fetch.setObjectName("primary")
        self.fetch.setToolTip(tooltip("history"))
        self.fetch.clicked.connect(self.fetch_data)
        for name, widget, key in (
            ("Stock", self.symbol, "stock"),
            ("Market", self.exchange, "exchange"),
            ("From", self.start, "session"),
            ("To", self.end, "session"),
        ):
            controls.addWidget(label(name, help_key=key))
            controls.addWidget(widget)
        controls.addWidget(self.fetch)
        control_layout.addLayout(controls)

        options = QHBoxLayout()
        self.pattern = QComboBox()
        self.pattern.addItems([LESSONS[pattern.key].title for pattern in PATTERNS])
        for index, pattern in enumerate(PATTERNS):
            self.pattern.setItemData(index, tooltip(pattern.key), Qt.ItemDataRole.ToolTipRole)
        self.pattern.setAccessibleName("Idea to test")
        self.pattern.currentIndexChanged.connect(self.pattern_changed)
        options.addWidget(label("2  Pick an idea", "eyebrow", help_key="pattern"))
        options.addWidget(self.pattern, 2)
        self.pattern_help = QPushButton("Explain pattern")
        self.pattern_help.setToolTip(tooltip("pattern"))
        self.pattern_help.clicked.connect(self.open_pattern)
        options.addWidget(self.pattern_help)
        self.capital = self.spin(100_000, 1, 1_000_000_000)
        self.fees = self.spin(10, 0, 999)
        self.slippage = self.spin(10, 0, 999)
        for spin in (self.capital, self.fees, self.slippage):
            spin.valueChanged.connect(self.invalidate_result)
        self.capital.setMaximumWidth(145)
        self.capital.setGroupSeparatorShown(True)
        self.capital.setToolTip(tooltip("capital"))
        self.fees.setToolTip(tooltip("fee"))
        self.slippage.setToolTip(tooltip("slippage"))
        options.addWidget(label("Starting money (INR)", help_key="capital"))
        options.addWidget(self.capital)
        self.cost_dialog = QDialog(self)
        self.cost_dialog.setWindowTitle("Practice trading costs")
        cost_layout = QVBoxLayout(self.cost_dialog)
        cost_help = browser()
        cost_help.setMinimumHeight(155)
        cost_help.setHtml(
            "<p>"
            + explain(
                "Trading costs apply when buying and when selling. "
                "10 means 0.1%: roughly INR 10 for each INR 10,000 traded. "
                "This is not a full tax model."
            )
            + "</p><p>Imagine this: a toy marketplace charges a service fee, and "
            "the toy costs a little more than the sign said. Both reduce your play money.</p>"
        )
        cost_layout.addWidget(cost_help)
        cost_form = QFormLayout()
        cost_form.addRow("Fee per INR 10,000 traded", self.fees)
        cost_form.addRow("Worse price per INR 10,000 traded", self.slippage)
        cost_layout.addLayout(cost_form)
        cost_close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        cost_close.rejected.connect(self.cost_dialog.reject)
        cost_layout.addWidget(cost_close)
        costs = QPushButton("Trading costs")
        costs.setToolTip(tooltip("fee"))
        costs.clicked.connect(self.cost_dialog.show)
        options.addWidget(costs)
        self.run_button = QPushButton("3  Test idea")
        self.run_button.setObjectName("primary")
        self.run_button.setToolTip(tooltip("simulation"))
        self.run_button.setEnabled(False)
        self.run_button.clicked.connect(self.run_experiment)
        options.addWidget(self.run_button)
        self.export = QPushButton("Save results")
        self.export.setToolTip(tooltip("json"))
        self.export.setEnabled(False)
        self.export.clicked.connect(self.export_run)
        options.addWidget(self.export)
        control_layout.addLayout(options)
        layout.addWidget(control_card)
        self.provenance = label("Start here: load a stock, pick an idea, then see what happened.")
        self.provenance.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.provenance.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.provenance)
        self.metric_values: list[QLabel] = []
        self.metric_notes: list[QLabel] = []
        metrics = QHBoxLayout()
        metrics.setSpacing(10)
        for name, note, key in (
            ("Money now", "Your practice money, including the stock you still own", "equity"),
            ("Gain or loss", "Compared with your starting money", "return"),
            ("Biggest fall", "Largest drop from an earlier high", "drawdown"),
            ("Practice trades", "Buying and selling, not real orders", "fill"),
        ):
            frame, metric_layout = card()
            metric_layout.addWidget(label(name, help_key=key))
            value = label("--", "metric")
            metric_layout.addWidget(value)
            value.setToolTip(tooltip(key))
            detail = label(note)
            detail.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
            detail.setToolTip(tooltip(key))
            metric_layout.addWidget(detail)
            self.metric_values.append(value)
            self.metric_notes.append(detail)
            metrics.addWidget(frame, 1)
        layout.addLayout(metrics)

        split = QSplitter(Qt.Orientation.Horizontal)
        charts_widget = QWidget()
        charts_layout = QVBoxLayout(charts_widget)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        chart_controls = QHBoxLayout()
        self.chart_hint = label("A price line joins each day's closing price.", help_key="chart")
        self.chart_hint.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        chart_controls.addWidget(self.chart_hint, 1)
        chart_controls.addWidget(label("Show"))
        self.chart_span = QComboBox()
        self.chart_span.addItems(
            ["30 trading days", "90 trading days", "1 trading year", "All history"]
        )
        self.chart_span.setCurrentIndex(1)
        self.chart_span.setToolTip(
            tooltip("lookback") + "<p>This control changes only the drawing, not the test.</p>"
        )
        self.chart_span.currentIndexChanged.connect(self.refresh_chart)
        chart_controls.addWidget(self.chart_span)
        self.price_style = QComboBox()
        self.price_style.addItems(["Price line", "Candles"])
        self.price_style.setToolTip(tooltip("candle"))
        self.price_style.currentIndexChanged.connect(self.refresh_chart)
        chart_controls.addWidget(self.price_style)
        charts_layout.addLayout(chart_controls)
        self.chart_tabs = QTabWidget()
        self.price_chart = chart_view()
        self.equity_chart = chart_view()
        self.drawdown_chart = chart_view()
        self.rule_chart = chart_view()
        for view, key in (
            (self.price_chart, "price"),
            (self.equity_chart, "equity"),
            (self.drawdown_chart, "drawdown"),
            (self.rule_chart, "pattern"),
        ):
            view.setToolTip(tooltip(key))
        self.chart_tabs.addTab(self.price_chart, "Stock price")
        self.chart_tabs.addTab(self.equity_chart, "Your money")
        self.chart_tabs.addTab(self.drawdown_chart, "Falls from a high")
        self.chart_tabs.addTab(self.rule_chart, "See the rule")
        for index, key in enumerate(("price", "equity", "drawdown", "pattern")):
            self.chart_tabs.setTabToolTip(index, tooltip(key))
        self.chart_tabs.currentChanged.connect(self.refresh_chart)
        charts_layout.addWidget(self.chart_tabs, 1)
        self.summary = label("No result yet. Load real stock history to begin.")
        self.summary.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        charts_layout.addWidget(self.summary)
        split.addWidget(charts_widget)
        self.inspector = QTabWidget()
        self.inspector.setObjectName("inspector")
        self.inspector.setMinimumWidth(290)
        self.explanation = browser()
        self.inspector.addTab(self.explanation, "The idea")
        self.trades = QTableWidget(0, 7)
        self.trades.setHorizontalHeaderLabels(
            [
                "Decision day",
                "Trade day",
                "Action",
                "Price INR",
                "Test units",
                "Fee INR",
                "Cash INR",
            ]
        )
        self.trade_help_keys = ("signal", "fill", "fill", "price", "units", "fee", "cash")
        for index, key in enumerate(self.trade_help_keys):
            heading = self.trades.horizontalHeaderItem(index)
            assert heading is not None
            heading.setToolTip(tooltip(key))
        self.trades.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.trades.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.trades.setAlternatingRowColors(True)
        self.trades.setShowGrid(False)
        self.trades.setToolTip(tooltip("fill"))
        self.inspector.addTab(self.trades, "Trades")
        self.data_details = browser()
        self.data_details.setPlainText("No stock history loaded. Real daily observations only.")
        self.inspector.addTab(self.data_details, "Data")
        split.addWidget(self.inspector)
        split.setSizes([1000, 335])
        split.setCollapsible(0, False)
        split.setCollapsible(1, False)
        layout.addWidget(split, 1)

        replay = QHBoxLayout()
        self.play = QPushButton("Play days")
        self.play.setCheckable(True)
        self.play.setEnabled(False)
        self.play.setToolTip(tooltip("replay"))
        self.play.toggled.connect(self.toggle_playback)
        replay.addWidget(self.play)
        replay.addWidget(label("Travel through time", help_key="replay"))
        self.replay = QSlider(Qt.Orientation.Horizontal)
        self.replay.setEnabled(False)
        self.replay.setToolTip(tooltip("replay"))
        self.replay.valueChanged.connect(self.redraw)
        self.replay.sliderPressed.connect(self.stop_playback)
        replay.addWidget(self.replay, 1)
        self.replay_label = QLabel("No data")
        replay.addWidget(self.replay_label)
        layout.addLayout(replay)
        self.tabs.addTab(experiment, "Explore")
        catalogue = QWidget()
        library_layout = QHBoxLayout(catalogue)
        library_layout.setContentsMargins(0, 12, 0, 0)
        self.lesson_list = QListWidget()
        self.lesson_list.addItems([LESSONS[pattern.key].title for pattern in PATTERNS])
        self.lesson_list.setFixedWidth(270)
        for index, pattern in enumerate(PATTERNS):
            self.lesson_list.item(index).setToolTip(tooltip(pattern.key))
        self.lesson_list.currentRowChanged.connect(self.lesson_selected)
        library_layout.addWidget(self.lesson_list)
        self.lesson_tabs = QTabWidget()
        self.lesson_text = browser()
        self.technical_text = browser()
        self.lesson_tabs.addTab(self.lesson_text, "Explain it simply")
        self.lesson_tabs.addTab(self.technical_text, "Exact rules and source")
        library_layout.addWidget(self.lesson_tabs, 1)
        self.tabs.addTab(catalogue, "Learn the patterns")
        roadmap = browser()
        roadmap.setHtml(
            "<h1>What's next?</h1><p>These features are planned. They do not work yet.</p>"
            f"<h2>A basket of stocks</h2><p>{explain(TERMS['portfolio'].meaning)}</p>"
            f"<p>Imagine this: {explain(TERMS['portfolio'].example)}</p>"
            f"<h2>AI-proposed ideas</h2><p>{explain(TERMS['ai'].meaning)}</p>"
            f"<p>Imagine this: {explain(TERMS['ai'].example)}</p>"
            "<h2>More patterns and data sources</h2><p>Seven ideas work today. More need "
            "sources, plain-English lessons and checks before joining the tool. "
            "No broker account or real-money trading is connected.</p>"
        )
        self.tabs.addTab(roadmap, "What's next")
        self.dictionary = QWidget()
        dictionary_layout = QVBoxLayout(self.dictionary)
        dictionary_layout.setContentsMargins(0, 12, 0, 0)
        dictionary_layout.addWidget(label("No assumed knowledge. Start with any word.", "section"))
        dictionary_layout.addWidget(
            label(
                "Search a word or abbreviation. Every entry has a simple meaning "
                "and an everyday example."
            )
        )
        self.glossary_search = QLineEdit()
        self.glossary_search.setPlaceholderText("Try: stock, SMA, drawdown, fees, RSI...")
        self.glossary_search.setAccessibleName("Search the plain-English dictionary")
        self.glossary_search.textChanged.connect(self.filter_glossary)
        dictionary_layout.addWidget(self.glossary_search)
        dictionary_split = QSplitter(Qt.Orientation.Horizontal)
        self.glossary_list = QListWidget()
        self.glossary_list.setMinimumWidth(280)
        self.glossary_list.currentRowChanged.connect(self.glossary_selected)
        dictionary_split.addWidget(self.glossary_list)
        self.glossary_text = browser()
        dictionary_split.addWidget(self.glossary_text)
        dictionary_split.setSizes([320, 1000])
        dictionary_layout.addWidget(dictionary_split, 1)
        self.tabs.addTab(self.dictionary, "Dictionary")
        self.glossary_keys: list[str] = []
        self.filter_glossary("")
        for help_browser in self.findChildren(HelpBrowser):
            help_browser.term_selected.connect(self.open_glossary)
        self.lesson_list.setCurrentRow(0)
        self.pattern_changed()

    @staticmethod
    def spin(value: float, minimum: float, maximum: float) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        spin.setDecimals(2)
        spin.setValue(value)
        return spin

    @staticmethod
    def pattern_html(index: int) -> str:
        pattern = PATTERNS[index]
        return (
            f"<h2>{escape(pattern.name)}</h2>"
            f"<h3>Imagine this first</h3><p>{explain(TERMS[pattern.key].example)}</p>"
            f"<h3>Words first</h3><p>{explain(LESSONS[pattern.key].words)}</p>"
            "<p><b>Long</b> means owning the stock. <b>Cash</b> means not owning it. "
            "A <b>bar</b> or <b>session</b> is one reported trading day. "
            "<b>Warmup</b> is the history needed before the rule is ready. "
            "A <b>target</b> says whether the rule wants to own the stock; a "
            "<b>fill</b> is the later simulated trade. <b>Lookback</b> means how "
            "many earlier days a calculation uses.</p>"
            f"<h3>The exact rule this app tests</h3><p>{explain(pattern.rules)}</p>"
            f"<h3>Where it can fail</h3><p>{explain(pattern.limitations)}</p>"
            f'<p><a style="color:{ACCENT}" href="{escape(pattern.source)}">'
            "Read the background source</a></p>"
            "<p>The source explains the idea. This app chooses the specific numbers "
            "and buy/sell version; the source does not endorse this test.</p>"
        )

    @Slot()
    def open_pattern(self) -> None:
        self.lesson_list.setCurrentRow(self.pattern.currentIndex())
        self.lesson_tabs.setCurrentIndex(0)
        self.tabs.setCurrentIndex(1)

    @Slot(str)
    def filter_glossary(self, query: str) -> None:
        self.glossary_keys = search_terms(query)
        self.glossary_list.clear()
        self.glossary_list.addItems([TERMS[key].title for key in self.glossary_keys])
        if self.glossary_keys:
            self.glossary_list.setCurrentRow(0)
        else:
            self.glossary_text.setPlainText(
                "No explanation found for that search. Try a shorter word or abbreviation. "
                "This dictionary contains authored explanations, not invented AI answers."
            )

    @Slot(int)
    def glossary_selected(self, index: int) -> None:
        if 0 <= index < len(self.glossary_keys):
            self.glossary_text.setHtml(term_html(self.glossary_keys[index]))

    @Slot(str)
    def open_glossary(self, key: str) -> None:
        self.glossary_search.setText(TERMS[key].title)
        self.glossary_list.setCurrentRow(self.glossary_keys.index(key))
        self.tabs.setCurrentWidget(self.dictionary)

    @Slot(int)
    def lesson_selected(self, index: int) -> None:
        if index < 0:
            return
        self.lesson_text.setHtml(lesson_html(index, complete=True))
        self.technical_text.setHtml(self.pattern_html(index))

    @Slot()
    def motion_changed(self) -> None:
        self.stop_playback()
        self.brand_movie.setPaused(not self.motion.isChecked())
        if self.motion.isChecked():
            self.brand_mark.setMovie(self.brand_movie)
        else:
            self.brand_mark.setPixmap(self.windowIcon().pixmap(46, 46))
        if self.fetch_thread is not None:
            self.loading_movie.setPaused(not self.motion.isChecked())
        self.play.setEnabled(self.motion.isChecked() and self.result is not None)
        for view in (self.price_chart, self.equity_chart, self.drawdown_chart, self.rule_chart):
            view.chart().setAnimationOptions(QChart.AnimationOption.NoAnimation)

    @Slot()
    def stop_playback(self) -> None:
        self.play_timer.stop()
        self.play.setChecked(False)

    @Slot(bool)
    def toggle_playback(self, playing: bool) -> None:
        self.play.setText("Pause" if playing else "Play days")
        if not playing:
            self.play_timer.stop()
            return
        if self.result is None or not self.motion.isChecked():
            self.stop_playback()
            return
        if self.replay.value() == self.replay.maximum():
            self.replay.setValue(1)
        self.play_timer.start()

    @Slot()
    def advance_replay(self) -> None:
        self.replay.setValue(min(self.replay.value() + 1, self.replay.maximum()))
        if self.replay.value() == self.replay.maximum():
            self.stop_playback()

    @Slot()
    def refresh_chart(self) -> None:
        self._animate_next = True
        self.redraw()

    @Slot(str)
    def exchange_changed(self, exchange: str) -> None:
        self.symbol.setPlaceholderText(
            "Yahoo BSE ticker, e.g. TCS" if exchange == "BSE" else "RELIANCE"
        )

    @Slot()
    def invalidate_result(self) -> None:
        self.stop_playback()
        self.result = None
        self.export.setEnabled(False)
        self.redraw()

    @Slot()
    def pattern_changed(self) -> None:
        self.pattern.setToolTip(tooltip(PATTERNS[self.pattern.currentIndex()].key))
        self.explanation.setHtml(lesson_html(self.pattern.currentIndex(), complete=False))
        self.lesson_list.setCurrentRow(self.pattern.currentIndex())
        self.invalidate_result()

    @Slot()
    def fetch_data(self) -> None:
        if self.fetch_thread is not None:
            return
        symbol = self.symbol.text()
        exchange = self.exchange.currentText()
        self.stop_playback()
        self.data = None
        self.result = None
        self.export.setEnabled(False)
        self.run_button.setEnabled(False)
        self.replay.setEnabled(False)
        self.redraw()
        self.fetch.setEnabled(False)
        self.provenance.setText(
            f"Fetching {symbol} / {exchange} from Yahoo Finance (unofficial)..."
        )
        self.data_details.setPlainText("Loading actual history. No earlier result is being reused.")
        self.summary.setText("Waiting for actual observations; no experiment is loaded.")
        self.fetch_thread = QThread(self)
        start = self.start.date()
        end = self.end.date()
        self.worker = FetchWorker(
            self.provider,
            symbol,
            exchange,
            date(start.year(), start.month(), start.day()),
            date(end.year(), end.month(), end.day()),
        )
        self.worker.moveToThread(self.fetch_thread)
        self.fetch_thread.started.connect(self.worker.run)
        self.worker.succeeded.connect(self.data_ready)
        self.worker.failed.connect(self.fetch_failed)
        self.worker.finished.connect(self.fetch_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.fetch_thread.finished.connect(self.fetch_finished)
        self.fetch_thread.finished.connect(self.fetch_thread.deleteLater)
        self.loading_status.setText(f"Loading {symbol} / {exchange} stock history...")
        self.workspace.setCurrentWidget(self.loading_page)
        self.loading_movie.start()
        if not self.motion.isChecked():
            self.loading_movie.setPaused(True)
        self.fetch_thread.start()

    @Slot(object)
    def data_ready(self, data: MarketData) -> None:
        self.data = data
        self.provenance.setText(
            f"{data.symbol} / {data.exchange} / {data.currency}  |  "
            f"{len(data.candles)} daily observations  |  Latest: {data.candles[-1].session}"
            "  |  Yahoo (unofficial), not live quotes"
        )
        details = (
            "WHERE THESE PRICES COME FROM\n\n"
            f"{data.symbol} / {data.exchange} / {data.currency} / {data.interval}\n"
            f"Source: {data.source}\n"
            f"Observed: {data.candles[0].session} to {data.candles[-1].session}; "
            f"{len(data.candles)} bars. Fetched: {data.fetched_at.isoformat()}\n"
            f"Basis: {data.price_basis}\n\n"
            + "\n".join(data.warnings)
            + "\n\nPRICES, EXPLAINED\n\n"
            "These are real daily observations from an unofficial Yahoo connection, not live "
            "quotes. Today's unfinished or current-day observation is always left out.\n\n"
            "Adjusted prices account for events such as a company splitting one share "
            "into several, or paying cash to shareholders. They are useful for comparing "
            "history, but are not the exact old cash prices of real shares. The test owns "
            "fractional adjusted units, not a literal number of real shares.\n\n"
            "The reference line buys once, after this idea has enough history, and keeps "
            "holding. It pays the same entry costs. Its start day can differ between ideas, "
            "so comparing different ideas is not automatically a fair ranking.\n\n"
            "Save results to preserve this exact set of prices; a later download may change."
            f"\n\nIMAGINE THIS\n\n{TERMS['provider'].example}\n\n"
            f"{TERMS['adjusted'].example}\n\n{TERMS['benchmark'].example}"
        )
        self.data_details.setHtml(explain(details).replace("\n", "<br>"))
        self.provenance.setToolTip(self.data_details.toPlainText())
        self.replay.blockSignals(True)
        self.replay.setRange(1, len(data.candles))
        self.replay.setValue(len(data.candles))
        self.replay.blockSignals(False)
        self.replay.setEnabled(True)
        self.run_button.setEnabled(True)
        self.run_experiment()

    @Slot(str)
    def fetch_failed(self, message: str) -> None:
        self.provenance.setText(
            f"DATA UNAVAILABLE - {message}\nNo simulated market data was substituted."
        )
        self.data_details.setPlainText(self.provenance.text())
        self.provenance.setToolTip(self.provenance.text())
        self.summary.setText(
            "Fetch failed. Check the symbol, connection and provider availability."
        )

    @Slot()
    def fetch_finished(self) -> None:
        self.fetch_thread = None
        self.worker = None
        self.loading_movie.stop()
        self.workspace.setCurrentWidget(self.tabs)
        self.fetch.setEnabled(True)

    @Slot()
    def run_experiment(self) -> None:
        self.stop_playback()
        if self.data is None:
            return
        try:
            self.result = simulate(
                self.data,
                PATTERNS[self.pattern.currentIndex()],
                Assumptions(self.capital.value(), self.fees.value(), self.slippage.value()),
            )
        except (ValueError, DataError) as error:
            self.result = None
            self.export.setEnabled(False)
            self.redraw()
            self.summary.setText(f"Experiment not run: {error}")
            return
        self.export.setEnabled(True)
        self.play.setEnabled(self.motion.isChecked())
        self._animate_next = True
        self.redraw()

    def reset_chart(self, view: QChartView, title: str) -> QChart:
        chart = view.chart()
        chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        chart.removeAllSeries()
        for axis in chart.axes():
            chart.removeAxis(axis)
            axis.deleteLater()
        chart.setAnimationOptions(
            QChart.AnimationOption.SeriesAnimations
            if self._animate_next and self.motion.isChecked() and not self.play_timer.isActive()
            else QChart.AnimationOption.NoAnimation
        )
        chart.setTitle(title)
        return chart

    def axes(self, chart: QChart, sessions: list[date], low: float, high: float) -> None:
        horizontal = QDateTimeAxis()
        horizontal.setFormat("dd MMM yy")
        horizontal.setTickCount(4)
        horizontal.setLabelsColor(QColor(MUTED))
        horizontal.setLabelsFont(QFont("Segoe UI", 9))
        horizontal.setGridLineVisible(False)
        horizontal.setLineVisible(False)
        horizontal.setRange(
            QDateTime.fromMSecsSinceEpoch(int(epoch(sessions[0]) - 43_200_000)),
            QDateTime.fromMSecsSinceEpoch(int(epoch(sessions[-1]) + 43_200_000)),
        )
        chart.addAxis(horizontal, Qt.AlignmentFlag.AlignBottom)
        vertical = QValueAxis()
        vertical.setLabelsColor(QColor(MUTED))
        vertical.setLabelsFont(QFont("Segoe UI", 9))
        vertical.setGridLinePen(QPen(QColor(88, 110, 117, 45)))
        vertical.setLineVisible(False)
        vertical.setTickCount(5)
        vertical.setLabelFormat("%.1f")
        margin = max((high - low) * 0.06, abs(high) * 0.01, 0.01)
        vertical.setRange(low - margin, high + margin)
        chart.addAxis(vertical, Qt.AlignmentFlag.AlignLeft)
        for series in chart.series():
            series.attachAxis(horizontal)
            series.attachAxis(vertical)

    @Slot()
    def redraw(self) -> None:
        price = self.reset_chart(self.price_chart, "Daily stock price (adjusted INR)")
        equity_chart = self.reset_chart(self.equity_chart, "What happened to your practice money?")
        drawdown_chart = self.reset_chart(self.drawdown_chart, "How far below an earlier high? (%)")
        self.reset_chart(self.rule_chart, "The numbers behind the idea")
        self.trades.setRowCount(0)
        self.play.setEnabled(self.result is not None and self.motion.isChecked())
        for metric in self.metric_values:
            metric.setText("--")
        for note, text in zip(
            self.metric_notes,
            (
                "Your practice money",
                "Compared with starting money",
                "From an earlier high",
                "No result yet",
            ),
            strict=True,
        ):
            note.setText(text)
        if self.data is None:
            self.replay_label.setText("No data")
            self.summary.setText("No result yet. Load real stock history to begin.")
            self._animate_next = False
            return
        count = self.replay.value()
        bars = self.data.candles[:count]
        if not bars:
            return
        self.replay_label.setText(str(bars[-1].session))
        span = (30, 90, 252, len(bars))[self.chart_span.currentIndex()]
        shown = bars[-span:]
        first = len(bars) - len(shown)
        if self.price_style.currentIndex() == 1:
            candles = QCandlestickSeries()
            candles.setName("Body: open to close / thin line: low to high")
            candles.setIncreasingColor(QColor(ACCENT))
            candles.setDecreasingColor(QColor(ROSE))
            for bar in shown:
                candles.append(
                    QCandlestickSet(bar.open, bar.high, bar.low, bar.close, epoch(bar.session))
                )
            price.addSeries(candles)
        else:
            self.add_line(
                price,
                "Closing price",
                [bar.session for bar in shown],
                [bar.close for bar in shown],
                ACCENT,
            )
        low = min(bar.low for bar in shown)
        high = max(bar.high for bar in shown)
        self.draw_rule(bars, first)
        hints = (
            "A line joins daily closes. Dots mark practice trades."
            if self.price_style.currentIndex() == 0
            else "Body = open to close. Thin line = low to high.",
            "Solid = this idea. Dashed = buy once, then hold.",
            "0% = at a high. -10% = 10% below the earlier high.",
            "These are the measurements used by the selected rule.",
        )
        self.chart_hint.setText(hints[self.chart_tabs.currentIndex()])
        hint_key = (
            "candle" if self.price_style.currentIndex() else "chart",
            "benchmark",
            "drawdown",
            PATTERNS[self.pattern.currentIndex()].key,
        )[self.chart_tabs.currentIndex()]
        self.chart_hint.setToolTip(tooltip(hint_key))
        if self.result is None:
            self.axes(price, [bar.session for bar in shown], low, high)
            self.summary.setText(
                "Observations loaded. Run the selected pattern with current settings."
            )
            self._animate_next = False
            return
        visible_trades = [
            trade for trade in self.result.trades if trade.fill_session <= bars[-1].session
        ]
        for side in ("BUY", "SELL"):
            fills = QScatterSeries()
            fills.setName("Buy (circle)" if side == "BUY" else "Sell (square)")
            color = QColor(ACCENT if side == "BUY" else WARM)
            fills.setColor(color)
            fills.setBorderColor(QColor(BASE))
            fills.setMarkerShape(
                QScatterSeries.MarkerShape.MarkerShapeCircle
                if side == "BUY"
                else QScatterSeries.MarkerShape.MarkerShapeRectangle
            )
            fills.setMarkerSize(10)
            for trade in visible_trades:
                if trade.side == side and trade.fill_session >= shown[0].session:
                    fills.append(epoch(trade.fill_session), trade.price)
                    low, high = min(low, trade.price), max(high, trade.price)
            price.addSeries(fills)
        self.axes(price, [bar.session for bar in shown], low, high)
        sessions = [bar.session for bar in shown]
        self.add_line(
            equity_chart,
            "This idea",
            sessions,
            list(self.result.equity[first:count]),
            ACCENT,
            area=True,
        )
        self.add_line(
            equity_chart,
            "Buy once & hold",
            sessions,
            list(self.result.benchmark[first:count]),
            WARM,
            dashed=True,
        )
        all_values = self.result.equity[first:count] + self.result.benchmark[first:count]
        self.axes(equity_chart, sessions, min(all_values), max(all_values))
        capital = self.result.assumptions.initial_cash
        current_equity = self.result.equity[count - 1]
        peak = capital
        drawdown = 0.0
        falls: list[float] = []
        for value in self.result.equity[:count]:
            peak = max(peak, value)
            drawdown = max(drawdown, (peak - value) / peak * 100)
            falls.append((value / peak - 1) * 100)
        self.add_line(
            drawdown_chart, "Drop from earlier high", sessions, falls[first:], ROSE, area=True
        )
        self.axes(drawdown_chart, sessions, min(falls[first:]), 0)
        target = self.result.targets[count - 1]
        target_text = (
            "still gathering history" if target is None else "own stock" if target else "keep cash"
        )
        units = sum(
            trade.units if trade.side == "BUY" else -trade.units for trade in visible_trades
        )
        self.summary.setText(
            f"As of {bars[-1].session}: money now INR {current_equity:,.2f} | "
            f"rule wants to {target_text} next opening."
        )
        self.summary.setToolTip(
            tooltip("equity") + f"<p>Adjusted test units held: {units:.6f}.</p>"
        )
        values = (
            f"INR {current_equity:,.0f}",
            f"{(current_equity / capital - 1) * 100:+.2f}%",
            f"{drawdown:.2f}%",
            str(len(visible_trades)),
        )
        notes = (
            f"Started with INR {capital:,.0f}",
            f"Buy once & hold: {(self.result.benchmark[count - 1] / capital - 1) * 100:+.2f}%",
            "Worst fall so far, not today's fall",
            "Currently owns stock" if units > 0 else "Currently keeping cash",
        )
        for value_label, text in zip(self.metric_values, values, strict=True):
            value_label.setText(text)
        self.metric_values[1].setStyleSheet(
            f"color: {GREEN if current_equity >= capital else ROSE};"
        )
        for note, text, key in zip(
            self.metric_notes, notes, ("capital", "benchmark", "drawdown", "long"), strict=True
        ):
            note.setText(text)
            note.setToolTip(tooltip(key))
        self.trades.setRowCount(len(visible_trades))
        for row, trade in enumerate(visible_trades):
            cells = (
                str(trade.signal_session),
                str(trade.fill_session),
                trade.side,
                f"{trade.price:.4f}",
                f"{trade.units:.6f}",
                f"{trade.fee:.2f}",
                f"{trade.cash_after:.2f}",
            )
            for column, cell_text in enumerate(cells):
                item = QTableWidgetItem(cell_text)
                key = trade.side.lower() if column == 2 else self.trade_help_keys[column]
                item.setToolTip(tooltip(key))
                self.trades.setItem(row, column, item)
        self._animate_next = False

    @staticmethod
    def add_line(
        chart: QChart,
        name: str,
        sessions: list[date],
        values: list[float],
        color: str,
        *,
        dashed: bool = False,
        area: bool = False,
    ) -> None:
        line = QLineSeries()
        line.setName(name)
        pen = QPen(QColor(color), 2)
        if dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        line.setPen(pen)
        for session, value in zip(sessions, values, strict=True):
            line.append(epoch(session), value)
        if area:
            fill = QAreaSeries(line)
            line.setParent(fill)
            fill.setName(name)
            fill.setPen(pen)
            tint = QColor(color)
            tint.setAlpha(25)
            fill.setBrush(QBrush(tint))
            chart.addSeries(fill)
        else:
            chart.addSeries(line)

    def draw_rule(self, bars: tuple[Candle, ...], first: int) -> None:
        pattern = PATTERNS[self.pattern.currentIndex()]
        key = pattern.key
        closes = [bar.close for bar in bars]
        guides: list[tuple[str, list[float | None], str]] = []
        if key == "sma":
            for period, color in ((10, ACCENT), (30, WARM)):
                average: list[float | None] = [
                    fmean(closes[i - period + 1 : i + 1]) if i + 1 >= period else None
                    for i in range(len(bars))
                ]
                guides.append((f"{period}-day average", average, color))
        elif key in ("ema", "macd"):
            fast, slow = ema(closes, 12), ema(closes, 26)
            if key == "ema":
                guides = [
                    ("12-day weighted average", fast, ACCENT),
                    ("26-day weighted average", slow, WARM),
                ]
            else:
                difference = [
                    a - b
                    for a, b in zip(fast, slow, strict=True)
                    if a is not None and b is not None
                ]
                macd: list[float | None] = [None] * min(25, len(bars)) + difference
                signal: list[float | None] = [None] * min(25, len(bars))
                signal.extend(ema(difference, 9))
                guides = [
                    ("Fast minus slow (MACD)", macd, ACCENT),
                    ("Smoothed difference", signal, WARM),
                ]
        elif key == "rsi":
            guides = [
                ("Recent gains vs losses (RSI)", wilder_rsi(closes), ACCENT),
                ("Buy at 30 or below", [30.0] * len(bars), WARM),
                ("Sell at 70 or above", [70.0] * len(bars), ROSE),
            ]
        elif key == "donchian":
            top: list[float | None] = [
                max(bar.high for bar in bars[i - 20 : i]) if i >= 20 else None
                for i in range(len(bars))
            ]
            bottom: list[float | None] = [
                min(bar.low for bar in bars[i - 20 : i]) if i >= 20 else None
                for i in range(len(bars))
            ]
            guides = [
                ("Close", list(closes), TEXT),
                ("Old 20-day high", top, ACCENT),
                ("Old 20-day low", bottom, WARM),
            ]
        elif key == "bollinger":
            middle: list[float | None] = [
                fmean(closes[i - 19 : i + 1]) if i >= 19 else None for i in range(len(bars))
            ]
            lower: list[float | None] = [
                fmean(closes[i - 19 : i + 1]) - 2 * pstdev(closes[i - 19 : i + 1])
                if i >= 19
                else None
                for i in range(len(bars))
            ]
            guides = [
                ("Close", list(closes), TEXT),
                ("20-day average (sell)", middle, WARM),
                ("Lower band (buy below)", lower, ACCENT),
            ]
        else:
            candles = QCandlestickSeries()
            candles.setName("Compare neighbouring bodies, not the thin lines")
            candles.setIncreasingColor(QColor(ACCENT))
            candles.setDecreasingColor(QColor(ROSE))
            for bar in bars[first:]:
                candles.append(
                    QCandlestickSet(bar.open, bar.high, bar.low, bar.close, epoch(bar.session))
                )
            chart = self.rule_chart.chart()
            chart.addSeries(candles)
            self.axes(
                chart,
                [bar.session for bar in bars[first:]],
                min(bar.low for bar in bars[first:]),
                max(bar.high for bar in bars[first:]),
            )
            return
        chart = self.rule_chart.chart()
        all_values: list[float] = []
        for name, values, color in guides:
            points = [
                (bar.session, value)
                for bar, value in zip(bars[first:], values[first:], strict=True)
                if value is not None
            ]
            if points:
                self.add_line(
                    chart,
                    name,
                    [point[0] for point in points],
                    [point[1] for point in points],
                    color,
                )
                all_values.extend(point[1] for point in points)
        if all_values:
            self.axes(
                chart,
                [bar.session for bar in bars[first:]],
                0 if key == "rsi" else min(all_values),
                100 if key == "rsi" else max(all_values),
            )
        else:
            chart.setTitle("Move forward in time: this idea needs more finished days.")

    @Slot()
    def export_run(self) -> None:
        if self.data is None or self.result is None:
            return
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export observations, rules and simulated results",
            "experiment.json",
            "JSON (*.json)",
        )
        if not filename:
            return
        payload = {
            "schema": 1,
            "application": "StonksSniper 0.1.0",
            "observations": asdict(self.data),
            "experiment": asdict(self.result),
            "replay_as_of": str(self.data.candles[self.replay.value() - 1].session),
            "execution": "Next available open; long/cash; fractional adjusted units; "
            "last holdings marked, not liquidated; no complete tax model.",
        }
        try:
            Path(filename).write_text(
                json.dumps(payload, default=str, indent=2, allow_nan=False), encoding="utf-8"
            )
        except (OSError, ValueError) as error:
            LOGGER.exception("Experiment export failed")
            QMessageBox.critical(self, "Export failed", str(error))
            return
        self.statusBar().showMessage(f"Exported full experiment to {filename}", 10_000)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.stop_playback()
        if self.fetch_thread is not None:
            self.statusBar().showMessage(
                "A bounded data request is running; close after it finishes."
            )
            event.ignore()
            return
        self.brand_movie.stop()
        super().closeEvent(event)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    app = QApplication(sys.argv)
    configure_application(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
