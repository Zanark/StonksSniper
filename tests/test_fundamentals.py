from __future__ import annotations

from datetime import date, datetime
from types import SimpleNamespace

import pandas as pd
import pytest
import yfinance as yf
from yfinance.exceptions import YFException

from stonks_sniper import fundamentals
from stonks_sniper.fundamentals import YahooFundamentalsProvider
from stonks_sniper.models import DataError
from stonks_sniper.providers import INDIA


def fixture_provider(monkeypatch, *, currency="INR", missing=False, bank=False):
    fixed = datetime(2026, 11, 21, 20, tzinfo=INDIA)

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed

    monkeypatch.setattr(fundamentals, "datetime", Clock)
    calls = []
    history = pd.DataFrame(
        {"Close": [139, 140]},
        index=pd.DatetimeIndex(["2026-11-19", "2026-11-20"], tz="Asia/Kolkata"),
    )
    balance = pd.DataFrame(
        {
            pd.Timestamp("2026-03-31"): {
                "CurrentAssets": 10_000_000_000,
                "CurrentLiabilities": 3_000_000_000,
                "TotalLiabilitiesNetMinorityInterest": 6_000_000_000,
                "OrdinarySharesNumber": 100_000_000,
                "TotalDebt": 2_000_000_000,
                "LongTermDebt": 1_000_000_000,
            }
        }
    )
    income = pd.DataFrame(
        {
            pd.Timestamp(f"{year}-03-31"): {"DilutedEPS": eps, "TotalRevenue": 20_000_000_000}
            for year, eps in ((2026, 12), (2025, 10), (2024, 8))
        }
    )
    info = {
        "financialCurrency": currency,
        "trailingEps": 11,
        "bookValue": 90,
        "sector": "Financial Services" if bank else "Industrials",
    }

    def fetch_history(**kwargs):
        calls.append(kwargs)
        return history

    ticker = SimpleNamespace(
        history=fetch_history,
        history_metadata={"currency": "INR", "exchangeName": "NSI"},
        get_info=lambda: info,
        get_balance_sheet=lambda **_: pd.DataFrame() if missing else balance,
        get_income_stmt=lambda **_: pd.DataFrame() if missing else income,
    )
    monkeypatch.setattr(yf, "Ticker", lambda _: ticker)
    return ticker, calls, info, history


def test_current_snapshot_has_completed_unadjusted_price_and_dated_separate_period_inputs(
    monkeypatch,
):
    _, calls, _, _ = fixture_provider(monkeypatch)
    result = YahooFundamentalsProvider().fetch("ICICIBANK", "NSE")
    values = {item.key: item.value for item in result.values}
    assert result.symbol == "ICICIBANK.NS" and result.price_session == date(2026, 11, 20)
    assert calls[0]["auto_adjust"] is False and calls[0]["repair"] is False
    assert values["price"] == 140
    assert [values[f"eps{i}"] for i in (1, 2, 3)] == [12, 10, 8]
    assert values["ttm_eps"] == 11
    assert values["assets"] == 1000 and values["shares"] == 10 and values["sales"] == 2000
    assert values["liabilities"] == 600
    assert not {"preferred", "positive_years", "dividend_years", "dividend"} & values.keys()
    assert "2026-03-31" in next(item.source for item in result.values if item.key == "assets")
    assert any("NOT the date" in note for note in result.warnings)


@pytest.mark.parametrize("currency", ["USD", None])
def test_foreign_or_unknown_statement_currency_cannot_be_mixed_with_inr(monkeypatch, currency):
    fixture_provider(monkeypatch, currency=currency)
    result = YahooFundamentalsProvider().fetch("ICICIBANK", "NSE")
    assert [item.key for item in result.values] == ["price"]
    assert any("No financial amounts" in note for note in result.warnings)


def test_missing_statements_remain_explicitly_unknown_and_bank_warning_is_preserved(monkeypatch):
    fixture_provider(monkeypatch, missing=True, bank=True)
    result = YahooFundamentalsProvider().fetch("ICICIBANK", "NSE")
    assert {item.key for item in result.values} == {"price", "ttm_eps", "book"}
    assert any("no annual balance" in note for note in result.warnings)
    assert any("no annual income" in note for note in result.warnings)
    assert any(
        "industrial current-ratio/net-net screens do not apply" in note for note in result.warnings
    )


@pytest.mark.parametrize("invalid", ["exchange", "quote", "naive", "network"])
def test_bad_fundamental_quotes_and_network_errors_are_not_replaced(monkeypatch, invalid):
    ticker, _, _, frame = fixture_provider(monkeypatch)
    if invalid == "exchange":
        ticker.history_metadata["exchangeName"] = "NYQ"
    elif invalid == "quote":
        frame["Close"] = float("nan")
    elif invalid == "naive":
        frame.index = frame.index.tz_localize(None)
    else:

        def fail(**_):
            raise YFException("Explicit reference outage")

        ticker.history = fail
    with pytest.raises(DataError):
        YahooFundamentalsProvider().fetch("ICICIBANK", "NSE")
