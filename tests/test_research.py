"""Synthetic arithmetic fixtures only; none are shipped as application market data."""

from __future__ import annotations

import math
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta

import pytest

from stonks_sniper.engine import Assumptions, simulate
from stonks_sniper.models import Candle, DataError, MarketData
from stonks_sniper.patterns import PATTERNS, ema, targets, wilder_rsi
from stonks_sniper.providers import yahoo_symbol


def observations(count: int = 100) -> MarketData:
    candles = tuple(
        Candle(
            date(2024, 1, 1) + timedelta(days=index),
            100 + index * 0.1 + math.sin(index / 4) * 10,
            103 + index * 0.1 + math.sin(index / 4) * 10,
            97 + index * 0.1 + math.sin(index / 4) * 10,
            101 + index * 0.1 + math.sin(index / 4) * 10,
            1000,
        )
        for index in range(count)
    )
    return MarketData(
        "TEST.NS",
        "NSE",
        candles,
        datetime.now(UTC),
        "Synthetic unit-test fixture only",
        "Test arithmetic",
    )


@pytest.mark.parametrize("pattern", PATTERNS, ids=lambda pattern: pattern.key)
def test_future_observations_cannot_change_past_signals_or_equity(pattern):
    data = observations()
    full_targets = targets(data.candles, pattern)
    full = simulate(data, pattern)
    for length in sorted({pattern.minimum_bars + 1, 85, 95}):
        prefix = replace(data, candles=data.candles[:length])
        assert targets(prefix.candles, pattern) == full_targets[:length]
        result = simulate(prefix, pattern)
        assert result.equity == full.equity[:length]
        assert result.benchmark == full.benchmark[:length]
        assert result.trades == tuple(
            trade for trade in full.trades if trade.fill_session <= prefix.candles[-1].session
        )


def test_close_signal_waits_until_next_open_and_costs_are_charged(monkeypatch):
    data = observations(4)
    monkeypatch.setattr("stonks_sniper.engine.targets", lambda *_: (None, True, False, True))
    result = simulate(
        data, next(p for p in PATTERNS if p.key == "engulfing"), Assumptions(1000, 100, 100)
    )
    buy, sell = result.trades
    assert buy.signal_session == data.candles[1].session
    assert buy.fill_session == data.candles[2].session
    assert buy.price == pytest.approx(data.candles[2].open * 1.01)
    assert buy.units == pytest.approx(1000 / (buy.price * 1.01))
    assert buy.fee == pytest.approx(buy.units * buy.price * 0.01)
    assert sell.signal_session == data.candles[2].session
    assert sell.fill_session == data.candles[3].session
    assert sell.price == pytest.approx(data.candles[3].open * 0.99)
    assert result.equity[-1] == pytest.approx(buy.units * sell.price * 0.99)
    assert result.open_units == 0
    # The final True target has no future candle at which to execute.
    assert len(result.trades) == 2


def test_final_position_is_marked_not_silently_liquidated(monkeypatch):
    data = observations(4)
    monkeypatch.setattr("stonks_sniper.engine.targets", lambda *_: (None, True, True, False))
    result = simulate(
        data, next(p for p in PATTERNS if p.key == "engulfing"), Assumptions(1000, 0, 0)
    )
    assert len(result.trades) == 1
    assert result.open_units > 0
    assert result.equity[-1] == pytest.approx(result.open_units * data.candles[-1].close)


def test_channel_excludes_current_bar():
    bars = [Candle(date(2024, 1, 1) + timedelta(days=i), 100, 101, 99, 100, 5) for i in range(20)]
    bars.append(Candle(date(2024, 1, 21), 100, 110, 99, 109, 5))
    assert targets(tuple(bars), PATTERNS[3])[-1] is True


def test_wilder_seed_and_flat_price_edges():
    assert wilder_rsi([10.0] * 16)[14:] == [50, 50]
    assert wilder_rsi([float(i + 1) for i in range(16)])[14:] == [100, 100]
    assert wilder_rsi([float(20 - i) for i in range(16)])[14:] == [0, 0]
    assert ema([1, 2, 3, 6], 3) == [None, None, 2, 4]


@pytest.mark.parametrize("price", [0, -1, float("nan"), float("inf")])
def test_invalid_market_prices_are_rejected(price):
    with pytest.raises(DataError):
        Candle(date(2024, 1, 1), price, 3, 1, 2, 0)


def test_bad_bounds_duplicate_sessions_and_naive_fetch_time_are_rejected():
    with pytest.raises(DataError, match="bounds"):
        Candle(date(2024, 1, 1), 10, 9, 8, 10, 1)
    data = observations()
    with pytest.raises(DataError, match="unique"):
        replace(data, candles=(data.candles[0], data.candles[0]))
    with pytest.raises(DataError, match="timezone"):
        replace(data, fetched_at=datetime(2024, 1, 1))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"initial_cash": 0},
        {"initial_cash": float("nan")},
        {"fee_bps": -1},
        {"slippage_bps": 10000},
    ],
)
def test_invalid_cost_assumptions_fail(kwargs):
    with pytest.raises(ValueError):
        Assumptions(**kwargs)


def test_insufficient_history_is_an_error_not_an_empty_success():
    with pytest.raises(ValueError, match="31 completed"):
        simulate(observations(30), PATTERNS[0])


def test_indian_ticker_resolution_and_exchange_mismatch():
    assert yahoo_symbol(" reliance ", "NSE") == "RELIANCE.NS"
    assert yahoo_symbol("RELIANCE", "BSE") == "RELIANCE.BO"
    assert yahoo_symbol("M&M", "NSE") == "M&M.NS"
    with pytest.raises(DataError, match="disagree"):
        yahoo_symbol("RELIANCE.NS", "BSE")
