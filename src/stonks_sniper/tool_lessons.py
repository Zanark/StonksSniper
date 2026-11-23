"""Original beginner notes, not a reproduction of the Kite manual."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape

MANUAL = "https://kite.trade/docs/kite/"
GTT = (
    "https://support.zerodha.com/category/trading-and-markets/charts-and-orders/"
    "gtt/articles/what-is-the-good-till-triggered-gtt-feature"
)


@dataclass(frozen=True)
class ToolLesson:
    title: str
    meaning: str
    example: str
    exercise: str
    boundary: str
    source: str

    def html(self) -> str:
        sections = (
            ("What it does and why", self.meaning),
            ("Everyday example", self.example),
            ("Try it here", self.exercise),
            ("Do not confuse it with", self.boundary),
        )
        return (
            f"<h1>{escape(self.title)}</h1>"
            + "".join(f"<h3>{name}</h3><p>{escape(text)}</p>" for name, text in sections)
            + f'<p><a href="{escape(self.source)}">Official background source</a></p>'
            "<p>Independent educational adaptation; not affiliated with Zerodha. "
            "Sources reviewed 2026-11-23. Broker rules and availability can change.</p>"
        )


TOOL_LESSONS = (
    ToolLesson(
        "Start here: your practice route",
        "A trading terminal is a set of tools, not a machine that knows the next price. "
        "Learn to observe, write a plan, place a hypothetical order and explain the result.",
        "A weighing scale helps a shopkeeper measure; it does not decide which shop will succeed.",
        "Fetch ICICIBANK in Explore, capture it here, inspect Watchlist, advance days, add a "
        "chart study, create a close alert, then queue one paper order. Compare marked P&L "
        "with the original strategy's Simulate window. Use Risk before choosing a quantity.",
        "Daily adjusted research history is not a live quote, actual purchasable share "
        "series or tomorrow's prediction. Every tool below declares its own limits.",
        MANUAL,
    ),
    ToolLesson(
        "Watchlists, quotes and OHLCV",
        "A watchlist remembers instruments you want to inspect. OHLC means opening, highest, "
        "lowest and closing prices; V is reported volume. Absolute change is money per unit; "
        "percentage change divides that movement by the previous observed close.",
        "Keep a list of vegetable prices to visit; writing a tomato on the list does not buy it.",
        "Capture separately fetched Explore histories, choose a stock, sort Watchlist columns "
        "and save instrument identifiers. Quotes show dates, source, adjustment basis and "
        "warnings. Reloading a saved list does not fetch or invent quotes.",
        "No LTP (last traded price), live streaming, universal instrument search or cloud sync. "
        "Daily close is not LTP; a missing previous bar means change is unknown.",
        MANUAL + "marketwatch/",
    ),
    ToolLesson(
        "Depth, bid, ask, spread and liquidity",
        "Bids are offered buying prices; asks are offered selling prices. The best ask minus "
        "best bid is the spread. Depth lists quantities at price levels; liquidity describes "
        "how easily size can trade without moving price.",
        "A buyer offers 99 for a toy and a seller wants 101: the spread is 2. "
        "Ten toys advertised at 101 do not promise they remain there when you arrive.",
        "Use Depth lab with explicitly manual bid/ask rows. Change the best ask and see "
        "the spread change. These inputs are arithmetic scenarios, never an actual order book.",
        "OHLCV cannot reconstruct 5/20-level depth, queue priority, hidden orders, LTT, LTQ, "
        "bid/ask liquidity or circuit limits. High reported volume is not guaranteed liquidity.",
        MANUAL + "marketwatch/#market-depth",
    ),
    ToolLesson(
        "Charts, candles and timeframes",
        "A line joins closes. A candle shows the open/close body and high/low wicks. "
        "Weekly/monthly aggregation combines actual observed daily bars; it changes detail, "
        "not the underlying observations.",
        "A weekly grocery total hides which day you spent most; a daily diary keeps that detail.",
        "Use Charts: line/candles, Daily/Weekly/Monthly, visible-session window, drag zoom "
        "and Reset zoom. Hover a close for its date/value. The selected cursor is the "
        "latest revealed close, not the end of the downloaded file.",
        "No intraday bars are fabricated. First/last aggregated periods may be partial; "
        "missing sessions stay missing. Aggregated dates label the last observed session.",
        MANUAL + "charting/",
    ),
    ToolLesson(
        "Indicators and volume",
        "An indicator transforms prices or volume. A moving average smooths observations; "
        "RSI summarises recent gains/losses. Two indicators using the same prices are not "
        "independent proof. VWAP needs an explicit price/volume sampling definition.",
        "A rolling average of grocery bills reduces day-to-day noise but cannot predict next week.",
        "Charts overlays shared SMA10/30, EMA12/26, Bollinger and Donchian guides. "
        "A separate Volume view shows reported volume. Existing Learn lessons cover all 27 "
        "rules, including oscillators, with actual measurements and demos.",
        "No daily approximation is labelled intraday VWAP. No 100-indicator parity, "
        "TradingView/ChartIQ embed, predictive score or guaranteed confirmation.",
        MANUAL + "charting/#indicatorsstudies",
    ),
    ToolLesson(
        "Levels, trend lines and measuring",
        "A horizontal level marks a price you want to watch. A trend line joins two chosen "
        "dated prices. Support/resistance are hypotheses about reactions, not physical barriers.",
        "Draw last month's milk price on a graph; the shop can still charge more tomorrow.",
        "Charts lets you add/remove a horizontal level and a two-point line by revealed "
        "session numbers/prices. Change the cursor to measure close-to-close movement from "
        "a selected earlier session. Label the hypothesis before looking ahead.",
        "Manual annotations are not detected patterns or automatic trades. Lines may fit past "
        "noise; no claim that touching them guarantees a bounce.",
        MANUAL + "charting/#drawing-tools",
    ),
    ToolLesson(
        "Compare instruments fairly",
        "Rebase both stocks to 100 at the first exactly shared observation so different unit "
        "prices can be compared. A price of 2,000 is not inherently more expensive in value "
        "terms than a price of 200.",
        "Two runners start at the same line even if one has longer legs.",
        "Capture at least two histories, select a comparison stock in Charts and choose "
        "Compare (100). Only exactly shared sessions up to the practice date are plotted.",
        "This is adjusted-price relative movement, not a funded rebalanced portfolio, "
        "valuation ranking or proof of diversification. Different sources can revise data.",
        MANUAL + "charting/#compare-instruments",
    ),
    ToolLesson(
        "Market and limit orders",
        "A market instruction prioritises execution, not a guaranteed price. A buy limit caps "
        "price; a sell limit sets a floor. A touched level does not guarantee a real fill.",
        "Buy a toy at the next available price versus refusing to pay more than 100.",
        "Paper orders: choose units and type, queue after the revealed close, then Next day. "
        "Only the next observed OPEN is examined. A marketable limit gets a bounded assumed "
        "fill; otherwise it expires or remains locally pending according to chosen validity.",
        "This deliberately opening-only exercise ignores intraday touches, volume queues and "
        "partial fills. It is not the algorithm engine or an exchange execution simulator.",
        MANUAL + "orders/#order-types",
    ),
    ToolLesson(
        "Stop market and stop limit",
        "A trigger activates an instruction. Stop market can fill far past the stop after a gap. "
        "Stop limit protects price but may never fill. Buy stops trigger up; sell stops down.",
        "An alarm tells you the milk has boiled over; it cannot undo the spill.",
        "Queue a paper stop after a revealed close. Only later openings activate it here. "
        "For buy stop limit use limit >= trigger; for sell use limit <= trigger. "
        "A triggered persistent limit remains active at later openings.",
        "Not an intraday stop or guaranteed maximum loss. Daily highs/lows reveal neither "
        "event order nor available liquidity; this desk does not infer a fill from them.",
        MANUAL + "orders/#stoploss-or-trigger-orders-sl-and-sl-m",
    ),
    ToolLesson(
        "Order book, validity, rejection and cancellation",
        "An order is an instruction; a trade is a fill. Pending, filled, expired, cancelled "
        "and rejected mean different things. Rejection needs a reason, not a fake trade.",
        "Sending a shopping request is not the same as receiving the goods.",
        "Inspect each paper order row, cancel a pending row, or cancel and replace it "
        "with corrected details. Try buying more than available cash or selling unowned units. "
        "Export an immutable JSON session with full observations, settings and order ledger.",
        "Next opening and Until cancelled are LOCAL exercise validity, not Kite DAY/GTT. "
        "No IOC/minute validity, exchange acknowledgements, cash reservations or settlement. "
        "Orders are evaluated in submission sequence using available cash at each fill.",
        MANUAL + "orders/#order-book",
    ),
    ToolLesson(
        "GTT, OCO, trailing stops and AMO",
        "GTT is a broker-held trigger, not a resting exchange fill. OCO cancels the other "
        "trigger when one activates. A trailing stop follows favourable movement. AMO queues "
        "an instruction for a later market session, not a closed-market trade.",
        "Ask a shop to call at a price, then decide which purchase instruction to send. "
        "The call is not a promise the item is still available.",
        "Explore trigger-versus-fill in Paper orders. Use Alerts to see completed-close "
        "crossings. Read the current official GTT support page for real product conditions.",
        "GTT/OCO/trailing and AMO scheduling are explained, NOT reproduced. Current support "
        "allows protected-market GTT variants as well as limits, unlike older manual wording. "
        "No app-closed monitoring, annual expiry service or broker guarantees.",
        GTT,
    ),
    ToolLesson(
        "Alerts and automated actions",
        "An alert reports a condition. A crossing alert fires only when price moves across a "
        "level, not on every day it stays above. An alert is not permission to place an order.",
        "A doorbell tells you someone arrived; it does not open the door automatically.",
        "Alerts lists all above/below CLOSE crossings in the revealed prefix and a count. "
        "Advance sessions to reveal later events. A first observation already above the "
        "threshold is not counted as a crossing.",
        "Historical inspection only, no live cloud email/push, scheduler, webhook or ATO "
        "(alert-triggered orders). No background worker continues after you close the app.",
        MANUAL + "orders/#kite-alerts",
    ),
    ToolLesson(
        "Holdings, positions, average cost and P&L",
        "Holdings mean owned assets; positions include trading exposures. Realised profit "
        "comes from sales; unrealised profit is a changing mark on unsold units. Fees matter. "
        "Average cost here includes entry fees and allocates cost proportionally on sale.",
        "Five unsold toys worth more than you paid are not extra cash in your wallet.",
        "Paper orders reports available cash, owned adjusted units, cost, realised and "
        "unrealised P&L, total marked INR/% and fees. Sell only some units and reconcile "
        "cash plus remaining marked stock with starting capital.",
        "Not a demat account, contract note, FIFO tax report, T1 delivery or settlement model. "
        "The manual's T+2 paragraph is old; do not learn current settlement rules from it. "
        "Console is separate back-office reporting, not this practice balance.",
        MANUAL + "portfolio/",
    ),
    ToolLesson(
        "Risk sizing, gaps, costs and break-even",
        "Choose a loss budget before quantity. Planned loss is units times entry cost minus "
        "assumed stop proceeds, including modelled costs. Capital affordability can bind first. "
        "Break-even is the exit reference price needed to recover entry and exit costs.",
        "Decide how many fragile jars you can afford to lose before filling the delivery van.",
        "Risk calculator: enter capital, risk %, entry, stop, target, fee and slippage. "
        "Inspect integer planned units, cash needed, reward/risk and break-even; raise costs "
        "and compare. Zero units is valid when a plan is unaffordable.",
        "The stop is an assumption, not a guaranteed loss cap. This proportional fee model "
        "does not include all Indian brokerage, STT, stamp duty, GST, SEBI or DP charges. "
        "The official brokerage calculator remains the source for broker-specific estimates.",
        MANUAL + "utilities/#brokerage-calculator",
    ),
    ToolLesson(
        "Baskets, allocation and stock SIP",
        "A basket groups instructions; it does not make execution atomic or diversify "
        "automatically. Allocation divides hypothetical capital. A stock SIP repeats purchases, "
        "not a guarantee that averaging will become profitable.",
        "A grocery list can contain five items; one sold-out item does not cancel the others.",
        "Allocation accepts percentage weights and reports INR budgets plus unallocated "
        "cash. The book chapter 5 real-history exercise demonstrates scheduled equal-money "
        "purchases. Headless lab can test each strategy separately.",
        "No multi-stock shared-cash execution, automatic rebalancing, basket margin netting "
        "or SIP scheduler. Budget arithmetic is not a portfolio backtest; SS-08 remains open.",
        MANUAL + "orders/#basket-orders",
    ),
    ToolLesson(
        "CNC, MIS, NRML, leverage and margin",
        "CNC labels cash delivery, MIS intraday exposure, NRML normal derivatives positions. "
        "Margin is collateral/risk security, not the maximum possible loss. Leverage magnifies "
        "gains and losses; auto-square-off is not a guaranteed exit.",
        "A rental deposit is smaller than the value of the car you could damage.",
        "Use the fully funded long/cash paper account first. Change risk assumptions before "
        "thinking about leverage. Read the linked product documentation for current rules.",
        "No MIS/NRML/MTF, pledging, loans, SPAN or broker buying-power calculator. Actual "
        "rules depend on instrument and broker; capital here is pretend and never transferred.",
        MANUAL + "funds/",
    ),
    ToolLesson(
        "Options, contracts, premiums, expiry and Greeks",
        "A bought call has a right linked to price rising; a bought put to falling. Strike is "
        "the agreed reference; premium is the price of the right. Expiry payoff is different "
        "from its market price before expiry. Delta/gamma/theta/vega describe model sensitivities.",
        "Pay a nonrefundable reservation fee for the right, but not obligation, to buy a toy "
        "at an agreed price. A useful right may still be worth less than its fee.",
        "Options lab calculates LONG call/put expiry P&L from manual strike, premium, total "
        "underlying units and settlement assumption. Change settlement to see the curve. "
        "Maximum premium loss is visible; no strategy recommendation is made.",
        "No live option chain/OI, Greeks valuation, implied volatility, short writing, "
        "lot-size discovery or exercise/physical-settlement/tax advice. Sensibull is the "
        "external option-chain widget in Kite; its features are not included here.",
        MANUAL + "widgets/#option-chain-by-sensibull",
    ),
    ToolLesson(
        "Technology, charts, APIs and independent services",
        "Kite is the trading terminal. Console handles back-office reports; Varsity teaches. "
        "ChartIQ/TradingView provide charting. Sensibull, Streak and smallcase widgets are "
        "separate integrations. An API is a structured program interface, not trading skill.",
        "A kitchen can use a separate recipe book, scale and payment terminal without "
        "those being one appliance.",
        "Use existing Learn demos for technical tests, the book workbook for current "
        "fundamentals and the stonks-sniper-lab skill/JSON commands for agent experiments. "
        "Read tool-specific limitations and source receipts in docs/market-tools.md.",
        "No Kite Connect login, licensed feed, embedded third-party terminal, external "
        "account or copied brokerage branding. No credentials or real orders are requested.",
        MANUAL + "widgets/",
    ),
    ToolLesson(
        "News, events, circuits, IPOs and market calendar",
        "News and corporate actions can alter prices and adjustment history. Circuit bands "
        "can restrict trading. Holidays affect sessions; IPO applications allocate newly "
        "issued shares and are not ordinary historical buy signals.",
        "A shop closure or changed package size can explain a missing or changed price.",
        "Inspect actual dates and warnings in Watchlist and Explore data details. Use "
        "official Bulletin, circulars and holiday-calendar links on the Utilities source page "
        "for current notices. Fetching completed history works when markets are closed.",
        "No invented current news feed, corporate-action event calendar, IPO application, "
        "exchange calendar completeness or circuit-band inference from OHLCV. No assumed "
        "Friday/weekend fills and no claim that old manual holiday links are current.",
        MANUAL + "utilities/",
    ),
    ToolLesson(
        "Advanced orders and honest capability boundaries",
        "Iceberg splits a large instruction into legs; disclosed quantity limits visibility. "
        "Cover orders link an entry and protective instruction. These mechanisms manage "
        "execution details, not the business value or future profitability of the stock.",
        "Ordering supplies in batches may reduce disruption; it cannot make demand appear.",
        "Learn the order lifecycle and gap risks with the implemented opening-only orders. "
        "Use Simulate for existing close-signal algorithms, not this manual exercise's fills.",
        "Iceberg, cover orders, disclosed quantity, auction participation, kill switches "
        "and exchange freeze limits are lesson-only. Daily observations cannot qualify "
        "their execution behaviour; no fake simulator or hidden broker integration is supplied.",
        MANUAL + "orders/",
    ),
)
