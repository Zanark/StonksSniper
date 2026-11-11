"""Adapter fixtures do not establish live market-data qualification."""

from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace

import pandas as pd
import pytest
import yfinance as yf
from yfinance.exceptions import YFException

from stonks_sniper.models import DataError
from stonks_sniper.providers import INDIA, YahooDailyProvider


def stub(monkeypatch, *, currency="INR", exchange="NSI", duplicate=False, invalid=False):
    today = datetime.now(INDIA).date()
    sessions = [today - timedelta(days=2), today - timedelta(days=1), today]
    if duplicate:
        sessions[1] = sessions[0]
    frame = pd.DataFrame(
        {
            "Open": [100, 101, 102],
            "High": [103, 104, 105],
            "Low": [99, 100, 101],
            "Close": [102, float("nan") if invalid else 103, 104],
            "Volume": [1000] * 3,
        },
        index=pd.DatetimeIndex(sessions, tz="Asia/Kolkata"),
    )
    calls = []

    def history(**kwargs):
        calls.append(kwargs)
        return frame

    monkeypatch.setattr(
        yf,
        "Ticker",
        lambda _: SimpleNamespace(
            history=history, history_metadata={"currency": currency, "exchangeName": exchange}
        ),
    )
    return today, calls


def test_adapter_uses_explicit_adjustments_and_excludes_current_session(monkeypatch):
    today, calls = stub(monkeypatch)
    data = YahooDailyProvider().fetch("RELIANCE", "NSE", today - timedelta(days=5), today)
    assert len(data.candles) == 2
    assert data.candles[-1].session == today - timedelta(days=1)
    assert calls[0]["auto_adjust"] is True
    assert calls[0]["repair"] is False
    assert calls[0]["raise_errors"] is True
    assert data.currency == "INR"
    assert "unofficial" in data.source
    assert "adjusted" in data.price_basis
    assert data.fetched_at.tzinfo is not None


@pytest.mark.parametrize(
    "options",
    [
        {"currency": "USD"},
        {"exchange": "NYQ"},
        {"duplicate": True},
        {"invalid": True},
    ],
)
def test_ambiguous_or_malformed_provider_data_is_not_repaired(monkeypatch, options):
    today, _ = stub(monkeypatch, **options)
    with pytest.raises(DataError):
        YahooDailyProvider().fetch("RELIANCE", "NSE", today - timedelta(days=5), today)


def test_network_failure_has_no_market_data_fallback(monkeypatch):
    def fail(**_):
        raise YFException("Provider unavailable")

    monkeypatch.setattr(yf, "Ticker", lambda _: SimpleNamespace(history=fail))
    today = datetime.now(INDIA).date()
    with pytest.raises(DataError, match="Provider unavailable"):
        YahooDailyProvider().fetch("RELIANCE", "NSE", today - timedelta(days=5), today)


def test_current_day_only_response_is_explicitly_unusable(monkeypatch):
    today = datetime.now(INDIA).date()
    frame = pd.DataFrame(
        {"Open": [100], "High": [103], "Low": [99], "Close": [102], "Volume": [1000]},
        index=pd.DatetimeIndex([today], tz="Asia/Kolkata"),
    )
    monkeypatch.setattr(
        yf,
        "Ticker",
        lambda _: SimpleNamespace(
            history=lambda **_: frame,
            history_metadata={"currency": "INR", "exchangeName": "BSE"},
        ),
    )
    with pytest.raises(DataError, match="RELIANCE.BO.*Current-day"):
        YahooDailyProvider().fetch("RELIANCE", "BSE", today - timedelta(days=730), today)
