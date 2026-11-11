"""Opt-in real network checks; never substitute fixtures for provider failures."""

from __future__ import annotations

import math
import os
from datetime import datetime, timedelta

import pytest
import yfinance as yf

from stonks_sniper.engine import simulate
from stonks_sniper.patterns import PATTERNS
from stonks_sniper.providers import INDIA, YahooDailyProvider

pytestmark = pytest.mark.skipif(
    os.environ.get("STONKS_LIVE_TESTS") != "1", reason="Explicit live-provider opt-in required"
)


@pytest.mark.parametrize(
    ("symbol", "exchange"), [("HDFCBANK", "NSE"), ("RELIANCE", "NSE"), ("TCS", "BSE")]
)
def test_actual_history_runs_every_strategy(symbol, exchange, tmp_path):
    yf.set_tz_cache_location(str(tmp_path / "yfinance-cache"))
    today = datetime.now(INDIA).date()
    data = YahooDailyProvider().fetch(symbol, exchange, today - timedelta(days=730), today)
    assert data.exchange == exchange
    assert data.currency == "INR"
    assert data.candles[-1].session < today
    assert len(data.candles) > max(pattern.minimum_bars for pattern in PATTERNS)
    for pattern in PATTERNS:
        result = simulate(data, pattern)
        assert len(result.equity) == len(data.candles)
        assert all(math.isfinite(value) and value >= 0 for value in result.equity)
        assert all(trade.signal_session < trade.fill_session for trade in result.trades)
