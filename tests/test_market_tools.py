from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, date, datetime

import pytest

from stonks_sniper.market_tools import (
    PaperAccount,
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


def bar(day: int, opening: float = 100, close: float | None = None) -> Candle:
    close = opening if close is None else close
    return Candle(
        date(2024, 1, day), opening, max(opening, close) + 10, min(opening, close) - 10, close, 1000
    )


def history() -> MarketData:
    return MarketData(
        "ICICIBANK.NS",
        "NSE",
        (bar(2), bar(3, 110), bar(4, 90), bar(5, 120)),
        datetime(2024, 1, 6, tzinfo=UTC),
        "ARITHMETIC TEST FIXTURE",
        "Test adjusted units",
        ("Not actual market data",),
    )


def account(capital=10000, fee=0, slip=0):
    result = PaperAccount(capital, fee, slip)
    result.advance(bar(2))
    return result


def test_aggregation_uses_iso_week_boundaries_and_partial_months():
    candles = tuple(
        Candle(day, price, price + 2, price - 2, price + 1, 10)
        for day, price in (
            (date(2020, 12, 31), 100),
            (date(2021, 1, 1), 110),
            (date(2021, 1, 4), 120),
        )
    )
    weekly = grouped_bars(candles, "Weekly")
    assert weekly[0] == Candle(date(2021, 1, 1), 100, 112, 98, 111, 20)
    assert weekly[1].session == date(2021, 1, 4)
    monthly = grouped_bars(candles, "Monthly")
    assert monthly[1] == Candle(date(2021, 1, 4), 110, 122, 108, 121, 20)
    assert grouped_bars(candles, "Daily") is candles
    with pytest.raises(DataError):
        grouped_bars(candles, "Intraday")


def test_comparison_intersects_dates_without_forward_fill():
    a = (bar(2, 100), bar(3, 150), bar(4, 200))
    b = (bar(2, 50), bar(4, 75), bar(5, 200))
    assert comparison(a, b) == ((date(2024, 1, 2), 100, 100), (date(2024, 1, 4), 200, 150))
    with pytest.raises(DataError, match="two"):
        comparison(a[:1], b)


def test_alert_is_crossing_not_repeated_level_or_first_bar():
    candles = tuple(bar(i + 1, value) for i, value in enumerate((110, 120, 90, 100, 105, 99)))
    assert crossings(candles, 100, "Cross above") == (date(2024, 1, 4),)
    assert crossings(candles, 100, "Cross below") == (
        date(2024, 1, 3),
        date(2024, 1, 6),
    )
    assert crossings(candles[:3], 100, "Cross above") == ()


def test_market_fills_later_open_not_signal_close_and_allocates_entry_cost():
    a = account(fee=100, slip=100)
    a.submit(date(2024, 1, 2), "Buy", "Market", 10)
    assert a.cash == 10000 and a.orders[0].status == "Pending"
    a.advance(bar(3, 100, 150))
    assert a.orders[0].price == 101
    assert a.orders[0].fee == pytest.approx(10.1)
    assert a.cost == pytest.approx(1020.1)
    a.submit(date(2024, 1, 3), "Sell", "Market", 4)
    a.advance(bar(4, 120))
    assert a.units == 6
    assert a.orders[1].price == pytest.approx(118.8)
    assert a.realised == pytest.approx(4 * 118.8 * 0.99 - 1020.1 * 0.4)
    assert a.cost == pytest.approx(1020.1 * 0.6)
    assert a.cash + a.units * 120 - a.capital == pytest.approx(a.realised + 720 - a.cost)
    assert "unrealised" in a.summary(120)


@pytest.mark.parametrize(
    "side,opening,limit,expected",
    [
        ("Buy", 90, 100, 99),
        ("Buy", 99, 100, 100),
        ("Sell", 110, 100, 100),
        ("Sell", 120, 100, 108),
    ],
)
def test_limit_never_breaks_limit_under_adverse_slippage(side, opening, limit, expected):
    a = account(slip=1000)
    if side == "Sell":
        a.submit(date(2024, 1, 2), "Buy", "Market", 1)
        a.advance(bar(3))
    a.submit(a.last_session, side, "Limit", 1, limit=limit)
    a.advance(bar(4, opening))
    assert a.orders[-1].price == pytest.approx(expected)


def test_intraday_touch_does_not_invent_fill_and_local_validity_expires():
    a = account()
    a.submit(a.last_session, "Buy", "Limit", 1, limit=95)
    a.advance(Candle(date(2024, 1, 3), 100, 120, 80, 110, 1000))
    assert a.orders[0].status == "Expired"
    assert a.units == 0


def test_stop_gap_risk_and_persistent_activated_stop_limit():
    a = account()
    a.submit(a.last_session, "Buy", "Stop market", 1, trigger=105)
    a.advance(bar(3, 130))
    assert a.orders[0].price == 130
    a.submit(
        a.last_session, "Sell", "Stop limit", 1, limit=115, trigger=120, validity="Until cancelled"
    )
    a.advance(bar(4, 100))
    assert a.orders[1].activated and a.orders[1].status == "Pending"
    a.advance(bar(5, 118))
    assert a.orders[1].status == "Filled" and a.orders[1].price == 118


def test_rejections_sequence_cancellation_and_strict_clock():
    a = account(capital=100)
    a.submit(a.last_session, "Buy", "Market", 2)
    a.submit(a.last_session, "Sell", "Market", 1)
    a.submit(a.last_session, "Buy", "Market", 1)
    a.submit(a.last_session, "Buy", "Market", 1)
    a.cancel(4)
    a.advance(bar(3, 100))
    assert [o.status for o in a.orders] == ["Rejected", "Rejected", "Filled", "Cancelled"]
    assert "cash" in a.orders[0].message and "units" in a.orders[1].message
    with pytest.raises(DataError, match="pending"):
        a.cancel(1)
    with pytest.raises(DataError, match="strictly later"):
        a.advance(bar(3))
    with pytest.raises(DataError, match="currently revealed"):
        a.submit(date(2024, 1, 2), "Buy", "Market", 1)


@pytest.mark.parametrize(
    "kind,limit,trigger",
    [
        ("Market", 100, None),
        ("Limit", None, None),
        ("Stop market", None, None),
        ("Stop limit", 99, 100),
    ],
)
def test_invalid_order_inputs_leave_ledger_untouched(kind, limit, trigger):
    a = account()
    with pytest.raises(DataError):
        a.submit(a.last_session, "Buy", kind, 1, limit, trigger)
    assert not a.orders


def test_risk_quantity_includes_two_sided_costs_and_affordability():
    sized = position_size(10000, 1, 100, 95, 110, 0, 0)
    assert sized.units == 20 and sized.planned_loss == 100 and sized.cash_needed == 2000
    assert sized.reward_risk == 2 and sized.break_even == 100
    priced = position_size(10000, 1, 100, 95, 110, 100, 100)
    expected_paid = 100 * 1.01 * 1.01
    expected_loss = expected_paid - 95 * 0.99 * 0.99
    assert priced.units == int(100 / expected_loss)
    assert priced.break_even == pytest.approx(expected_paid / 0.99 / 0.99)
    assert position_size(50, 1, 100, 95, 110).units == 0


@pytest.mark.parametrize(
    "run",
    [
        lambda: position_size(10000, 101, 100, 95, 110),
        lambda: position_size(10000, 1, 100, 105, 110),
        lambda: position_size(10000, 1, 100, 95, 110, 10000),
        lambda: allocation(100, (float("nan"),)),
        lambda: allocation(100, (60, 50)),
        lambda: PaperAccount(float("inf")),
        lambda: option_payoff("Long call", 100, -1, 1, 100),
        lambda: option_payoff("Short call", 100, 5, 1, 100),
        lambda: depth_summary(((101, 1),), ((100, 1),)),
    ],
)
def test_invalid_manual_scenarios_fail_explicitly(run):
    with pytest.raises(DataError):
        run()


def test_allocation_depth_and_bought_option_arithmetic():
    assert allocation(10000, (40, 30, 20)) == (4000, 3000, 2000)
    assert depth_summary(((98, 10), (99, 10)), ((102, 10), (101, 10))) == (99, 101, 2)
    assert option_payoff("Long call", 100, 5, 50, 110) == 250
    assert option_payoff("Long call", 100, 5, 50, 80) == -250
    assert option_payoff("Long put", 100, 5, 50, 80) == 750
    assert option_payoff("Long put", 100, 5, 50, 110) == -250


def test_watchlist_roundtrip_and_reject_malformed_or_ambiguous_values(tmp_path):
    entries = (("ICICIBANK.NS", "NSE"), ("TCS.BO", "BSE"))
    filename = tmp_path / "list.json"
    filename.write_text(json.dumps(watchlist_document(entries)), encoding="utf-8")
    assert load_watchlist(filename) == entries
    for bad in (
        {"schema": True, "instruments": []},
        {"schema": 1, "instruments": [{"symbol": "TCS", "exchange": "BAD"}]},
        {"schema": 1, "instruments": [1]},
    ):
        filename.write_text(json.dumps(bad), encoding="utf-8")
        with pytest.raises(DataError):
            load_watchlist(filename)
    with pytest.raises(DataError, match="unique"):
        watchlist_document((entries[0], entries[0]))
    with pytest.raises(DataError, match="agree"):
        watchlist_document((("TCS.BO", "NSE"),))
    filename.write_text('{"schema": 1, "schema": 1, "instruments": []}', encoding="utf-8")
    with pytest.raises(DataError, match="Duplicate"):
        load_watchlist(filename)


def test_quote_is_prefix_safe_with_provenance_and_unknown_previous():
    data = history()
    text = quote_text(data, data.candles[0].session)
    assert "Unknown" in text and "ARITHMETIC TEST FIXTURE" in text
    assert "2024-01-05" not in text
    assert "No previous" not in quote_text(replace(data, candles=data.candles[:2]))
