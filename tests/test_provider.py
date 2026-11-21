"""Adapter fixtures do not establish live market-data qualification."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from types import SimpleNamespace

import pandas as pd
import pytest
import yfinance as yf
from yfinance.exceptions import YFException

from stonks_sniper import providers
from stonks_sniper.models import DataError
from stonks_sniper.providers import INDIA, YahooDailyProvider


def stub(
    monkeypatch, *, currency="INR", exchange="NSI", duplicate=False, invalid=False, missing_rows=()
):
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
        dtype=float,
    )
    for row in missing_rows:
        frame.loc[frame.index[row], ["Open", "High", "Low", "Close"]] = float("nan")
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


@pytest.mark.parametrize("missing_row", [0, 1])
def test_missing_adjusted_prices_are_excluded_with_dated_warning(monkeypatch, caplog, missing_row):
    today, _ = stub(monkeypatch, missing_rows=(missing_row,))
    data = YahooDailyProvider().fetch("HDFCBANK", "NSE", today - timedelta(days=5), today)
    missing_session = today - timedelta(days=2 - missing_row)
    assert len(data.candles) == 1
    assert missing_session not in {bar.session for bar in data.candles}
    warning = next(warning for warning in data.warnings if "missing OHLC" in warning)
    assert str(missing_session) in warning
    assert "not filled" in warning
    assert warning in caplog.text


def test_no_usable_prices_after_exclusions_is_still_an_error(monkeypatch):
    today, _ = stub(monkeypatch, missing_rows=(0, 1))
    with pytest.raises(DataError, match="HDFCBANK.NS.*missing OHLC"):
        YahooDailyProvider().fetch("HDFCBANK", "NSE", today - timedelta(days=5), today)


@pytest.mark.parametrize(
    "now,sessions,expected",
    [
        ("2026-11-21T19:00:00", ["2026-11-19", "2026-11-20"], "2026-11-20"),
        ("2026-11-22T10:00:00", ["2026-11-19", "2026-11-20"], "2026-11-20"),
        ("2026-01-26T14:00:00", ["2026-01-22", "2026-01-23"], "2026-01-23"),
        ("2026-11-20T20:00:00", ["2026-11-19", "2026-11-20"], "2026-11-19"),
        # A supplied special Sunday session is kept; no weekday guessing/filtering.
        ("2026-11-23T10:00:00", ["2026-11-20", "2026-11-22"], "2026-11-22"),
    ],
)
def test_closed_market_requests_return_actual_completed_sessions(
    monkeypatch, now, sessions, expected
):
    fixed = datetime.fromisoformat(now).replace(tzinfo=INDIA)

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed

    monkeypatch.setattr(providers, "datetime", Clock)
    frame = pd.DataFrame(
        {
            "Open": [100, 101],
            "High": [103, 104],
            "Low": [99, 100],
            "Close": [102, 103],
            "Volume": [1000, 1001],
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
            history=history, history_metadata={"currency": "INR", "exchangeName": "NSI"}
        ),
    )
    data = YahooDailyProvider().fetch(
        "ICICIBANK", "NSE", fixed.date() - timedelta(days=10), fixed.date()
    )
    assert data.symbol == "ICICIBANK.NS"
    assert data.candles[-1].session == date.fromisoformat(expected)
    assert data.candles[-1].close == (103 if expected == sessions[-1] else 102)
    assert {str(bar.session) for bar in data.candles}.issubset(sessions)
    assert data.fetched_at == fixed
    assert calls[0]["end"] == (fixed.date() + timedelta(days=1)).isoformat()
    assert any("Fetching does not require an open market" in note for note in data.warnings)
