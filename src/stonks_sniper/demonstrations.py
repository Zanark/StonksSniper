"""Causal teaching measurements and explicitly bounded real-history exercises."""

from __future__ import annotations

from html import escape
from statistics import fmean, pstdev

from stonks_sniper.engine import Result
from stonks_sniper.graham import BOOK_LESSONS, equal_money, real_return
from stonks_sniper.lessons import LESSONS
from stonks_sniper.models import Candle, MarketData
from stonks_sniper.patterns import ema, wilder_rsi
from stonks_sniper.studies import Series, study

HISTORY_CHAPTERS = {2, 3, 5, 8}
REFERENCE_CHAPTERS = {7, 11, 12, 13, 14, 15, 20}


def rule_guides(bars: tuple[Candle, ...], key: str) -> tuple[tuple[str, Series], ...]:
    closes = [bar.close for bar in bars]
    count = len(bars)
    if key == "sma":
        return tuple(
            (
                f"{period}-day average",
                [
                    fmean(closes[i - period + 1 : i + 1]) if i + 1 >= period else None
                    for i in range(count)
                ],
            )
            for period in (10, 30)
        )
    if key in ("ema", "macd"):
        fast, slow = ema(closes, 12), ema(closes, 26)
        if key == "ema":
            return ("12-day weighted average", fast), ("26-day weighted average", slow)
        difference = [
            a - b for a, b in zip(fast, slow, strict=True) if a is not None and b is not None
        ]
        return (
            ("Fast minus slow (MACD)", [None] * min(25, count) + difference),
            ("Smoothed difference", [None] * min(25, count) + ema(difference, 9)),
        )
    if key == "rsi":
        return (
            ("Recent gains vs losses (RSI)", wilder_rsi(closes)),
            ("Buy at 30 or below", [30.0] * count),
            ("Sell at 70 or above", [70.0] * count),
        )
    if key == "donchian":
        return (
            ("Close", list(closes)),
            (
                "Old 20-day high",
                [
                    max(bar.high for bar in bars[i - 20 : i]) if i >= 20 else None
                    for i in range(count)
                ],
            ),
            (
                "Old 20-day low",
                [
                    min(bar.low for bar in bars[i - 20 : i]) if i >= 20 else None
                    for i in range(count)
                ],
            ),
        )
    if key == "bollinger":
        return (
            ("Close", list(closes)),
            (
                "20-day average (sell)",
                [fmean(closes[i - 19 : i + 1]) if i >= 19 else None for i in range(count)],
            ),
            (
                "Lower band (buy below)",
                [
                    fmean(closes[i - 19 : i + 1]) - 2 * pstdev(closes[i - 19 : i + 1])
                    if i >= 19
                    else None
                    for i in range(count)
                ],
            ),
        )
    if key == "engulfing":
        return (
            ("Open", [bar.open for bar in bars]),
            ("Close", list(closes)),
            ("Previous open", [None] + [bar.open for bar in bars[:-1]] if bars else []),
            ("Previous close", [None] + closes[:-1] if bars else []),
        )
    return study(bars, key).guides


def decision_html(data: MarketData, result: Result, count: int) -> str:
    if not 1 <= count <= len(data.candles):
        raise ValueError("Choose a revealed day inside the demo history.")
    bars = data.candles[:count]
    bar = bars[-1]
    pattern = result.pattern
    lesson = LESSONS[pattern.key]
    target = result.targets[count - 1]
    trades = [trade for trade in result.trades if trade.fill_session <= bar.session]
    holding = bool(trades and trades[-1].side == "BUY")
    if target is None:
        action = "Warmup: not enough completed observations for an actionable decision."
    elif target == holding:
        action = (
            "Keep owning the stock; no extra buy."
            if target
            else "Keep cash; there is nothing to sell."
        )
    else:
        action = (
            f"{'BUY' if target else 'SELL'} requested for the next available opening, "
            "not this closing price. It is not a filled trade yet."
        )
    values = "".join(
        f"<li>{escape(name)}: "
        + ("not ready" if observations[-1] is None else f"{observations[-1]:,.6f}")
        + "</li>"
        for name, observations in rule_guides(bars, pattern.key)
    )
    fills = "".join(
        f"<p>{trade.side} filled today at INR {trade.price:,.6f}; "
        f"decision was {trade.signal_session}; fee INR {trade.fee:,.2f}.</p>"
        for trade in trades
        if trade.fill_session == bar.session
    )
    return (
        f"<h2>{bar.session}: read the actual measurements</h2>"
        f"<p>Open {bar.open:,.6f}; high {bar.high:,.6f}; low {bar.low:,.6f}; "
        f"close {bar.close:,.6f}; volume {bar.volume:,.0f}.</p><ul>{values}</ul>"
        f"<p><b>{escape(action)}</b></p>{fills}"
        f"<p>Buy condition: {escape(lesson.buy)}<br>Sell condition: {escape(lesson.sell)}</p>"
        "<p>Between thresholds, stateful rules retain their earlier target. "
        "A target is not a new order every day. The last signal in a range may never fill.</p>"
        f"<p>What can go wrong: {escape(lesson.catch)}</p>"
        f"<h3>Captured data</h3><p>{escape(data.symbol)} / {escape(data.exchange)} / "
        f"{escape(data.source)}; fetched {data.fetched_at.isoformat()}.<br>"
        f"Basis: {escape(data.price_basis)}.</p>"
        "<p>Past application is not proof of reliable profits. No winning interval was "
        "searched for. Next signal/trade navigation inspects this recorded history, "
        "not a live forecast. Costs and a same-start buy-and-hold comparison are shown.</p>"
    )


def monthly_purchases(bars: tuple[Candle, ...]) -> tuple[Candle, ...]:
    selected: list[Candle] = []
    for bar in bars:
        if not selected or (bar.session.year, bar.session.month) != (
            selected[-1].session.year,
            selected[-1].session.month,
        ):
            selected.append(bar)
    return tuple(selected)


def book_history_html(
    data: MarketData, count: int, chapter: int, amount: float, annual_inflation: float
) -> str:
    if chapter not in HISTORY_CHAPTERS or not 1 <= count <= len(data.candles):
        raise ValueError("Choose a supported chapter and a revealed day inside the history.")
    bars = data.candles[:count]
    lesson = BOOK_LESSONS[chapter - 1]
    nominal = (bars[-1].close / bars[0].close - 1) * 100
    peak = bars[0].close
    drawdown = 0.0
    for bar in bars:
        peak = max(peak, bar.close)
        drawdown = max(drawdown, (1 - bar.close / peak) * 100)
    html = (
        f"<h2>Chapter {chapter}: {escape(lesson.title)}</h2>"
        f"<p>{escape(data.symbol)}: {bars[0].session} to {bars[-1].session}. "
        "Only revealed observations are included.</p>"
        f"<p>Close-to-close adjusted change: {nominal:+.4f}%. "
        f"Worst close-to-close fall from an earlier high: {drawdown:.4f}%.</p>"
    )
    if chapter == 2:
        if not -99 <= annual_inflation <= 100:
            raise ValueError("Assumed annual inflation must be between -99% and 100%.")
        years = (bars[-1].session - bars[0].session).days / 365.25
        period_inflation = ((1 + annual_inflation / 100) ** years - 1) * 100
        real = real_return(nominal, period_inflation)
        html += (
            f"<h3>Purchasing-power exercise</h3><p>USER ASSUMPTION, not measured CPI: "
            f"{annual_inflation:g}% constant annual inflation, compounded over "
            f"{years:.6f} years = {period_inflation:.4f}% for this interval.</p>"
            f"<p>Real change = (1 + {nominal:.6f}/100) / "
            f"(1 + {period_inflation:.6f}/100) - 1 = {real:+.4f}%.</p>"
        )
    elif chapter == 5:
        purchases = monthly_purchases(bars)
        units, average = equal_money(amount, tuple(bar.open for bar in purchases))
        cost = amount * len(purchases)
        value = units * bars[-1].close
        html += (
            "<h3>Equal-money purchases on the actual observations</h3>"
            f"<p>Add INR {amount:,.2f} on the first available session of each observed "
            "month, including the first partial month. Buy at that session's adjusted open. "
            "No fabricated calendar dates or price-based entry selection.</p>"
            f"<p>Contributed INR {cost:,.2f}; {units:.6f} adjusted units; "
            f"average cost INR {average:,.6f}. Value now INR {value:,.2f}; "
            f"marked gain/loss INR {value - cost:+,.2f} "
            f"({(value / cost - 1) * 100:+.4f}% of contributions, NOT annualised or "
            "money-weighted return).</p><ul>"
            + "".join(
                f"<li>{bar.session}: INR {amount:,.2f} / {bar.open:,.6f} "
                f"= {amount / bar.open:.6f} units.</li>"
                for bar in purchases
            )
            + "</ul><p>Teaching simplification: no fees, slippage, tax or real-share rounding. "
            "One stock is NOT a diversified portfolio; regular purchases can lose money.</p>"
        )
    else:
        html += (
            "<p>This shows changing market offers and historical falls, NOT a buy/sell "
            "algorithm. A falling quote does not prove a bargain, and this chart cannot "
            "determine business value, permanent loss or future returns.</p>"
        )
    return html + (
        f"<p>{escape(lesson.caution)}</p><h3>Data and limits</h3>"
        f"<p>{escape(data.source)}; fetched {data.fetched_at.isoformat()}. "
        f"{escape(data.price_basis)}. Adjusted research units, not historical cash shares. "
        "No second dividend credit. Price changes above exclude trading costs/taxes.</p>"
        + "".join(f"<p>{escape(warning)}</p>" for warning in data.warnings)
    )
