from __future__ import annotations

import json
import math
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from statistics import fmean
from typing import Literal

from stonks_sniper.models import Candle, DataError, MarketData
from stonks_sniper.providers import yahoo_symbol

Side = Literal["Buy", "Sell"]
OrderType = Literal["Market", "Limit", "Stop market", "Stop limit"]
Validity = Literal["Next opening", "Until cancelled"]


def positive(name: str, *values: float) -> None:
    if not all(
        type(value) in (float, int) and math.isfinite(value) and 0 < value <= 1e15
        for value in values
    ):
        raise DataError(f"{name} must be finite, positive and at most 1e15.")


def basis_points(name: str, value: float) -> None:
    if not math.isfinite(value) or not 0 <= value < 10000:
        raise DataError(f"{name} must be finite, from 0 to less than 10,000 bps.")


def grouped_bars(candles: tuple[Candle, ...], timeframe: str) -> tuple[Candle, ...]:
    if timeframe == "Daily":
        return candles
    if timeframe not in ("Weekly", "Monthly"):
        raise DataError("Choose Daily, Weekly or Monthly.")
    groups: list[list[Candle]] = []
    previous: tuple[int, int] | None = None
    for bar in candles:
        iso = bar.session.isocalendar()
        key = (
            (iso.year, iso.week) if timeframe == "Weekly" else (bar.session.year, bar.session.month)
        )
        if key != previous:
            groups.append([])
        groups[-1].append(bar)
        previous = key
    return tuple(
        Candle(
            group[-1].session,
            group[0].open,
            max(b.high for b in group),
            min(b.low for b in group),
            group[-1].close,
            sum(b.volume for b in group),
        )
        for group in groups
    )


def comparison(
    left: tuple[Candle, ...], right: tuple[Candle, ...]
) -> tuple[tuple[date, float, float], ...]:
    a = {bar.session: bar.close for bar in left}
    b = {bar.session: bar.close for bar in right}
    dates = sorted(a.keys() & b.keys())
    if len(dates) < 2:
        raise DataError("Comparison needs at least two exactly shared sessions.")
    return tuple((day, 100 * a[day] / a[dates[0]], 100 * b[day] / b[dates[0]]) for day in dates)


def crossings(candles: tuple[Candle, ...], level: float, direction: str) -> tuple[date, ...]:
    positive("Alert level", level)
    if direction not in ("Cross above", "Cross below"):
        raise DataError("Choose Cross above or Cross below.")
    return tuple(
        current.session
        for previous, current in zip(candles, candles[1:], strict=False)
        if (
            previous.close < level <= current.close
            if direction == "Cross above"
            else previous.close > level >= current.close
        )
    )


@dataclass(frozen=True)
class Sizing:
    units: int
    risk_budget: float
    planned_loss: float
    cash_needed: float
    reward_risk: float
    break_even: float


def position_size(
    capital: float,
    risk_percent: float,
    entry: float,
    stop: float,
    target: float,
    fee_bps: float = 10,
    slippage_bps: float = 10,
) -> Sizing:
    positive(
        "Capital, risk percentage and price assumptions", capital, risk_percent, entry, stop, target
    )
    if risk_percent > 100 or not stop < entry < target:
        raise DataError("Long-only plan needs risk <= 100% and stop < entry < target.")
    basis_points("Fee", fee_bps)
    basis_points("Slippage", slippage_bps)
    fee, slip = fee_bps / 10000, slippage_bps / 10000
    paid = entry * (1 + slip) * (1 + fee)
    received_stop = stop * (1 - slip) * (1 - fee)
    received_target = target * (1 - slip) * (1 - fee)
    risk = paid - received_stop
    budget = capital * risk_percent / 100
    units = math.floor(min(capital / paid, budget / risk))
    return Sizing(
        units,
        budget,
        units * risk,
        units * paid,
        (received_target - paid) / risk,
        paid / ((1 - slip) * (1 - fee)),
    )


def allocation(capital: float, weights: tuple[float, ...]) -> tuple[float, ...]:
    positive("Capital", capital)
    if not weights or not all(math.isfinite(w) and w >= 0 for w in weights):
        raise DataError("Use finite nonnegative percentage weights.")
    if sum(weights) > 100 + 1e-10:
        raise DataError("Weights cannot exceed 100%; no borrowing is simulated.")
    return tuple(capital * w / 100 for w in weights)


def option_payoff(kind: str, strike: float, premium: float, units: int, settlement: float) -> float:
    positive("Strike and settlement", strike, settlement)
    if not math.isfinite(premium) or premium < 0 or type(units) is not int or units < 1:
        raise DataError("Premium must be nonnegative and units a positive integer.")
    if kind not in ("Long call", "Long put"):
        raise DataError("Only bought calls and puts are modelled.")
    intrinsic = max(0, settlement - strike) if kind == "Long call" else max(0, strike - settlement)
    return units * (intrinsic - premium)


def depth_summary(
    bids: tuple[tuple[float, float], ...], asks: tuple[tuple[float, float], ...]
) -> tuple[float, float, float]:
    if not bids or not asks:
        raise DataError("Enter both bids and asks.")
    for price, quantity in (*bids, *asks):
        positive("Depth prices and quantities", price, quantity)
    best_bid, best_ask = max(p for p, _ in bids), min(p for p, _ in asks)
    if best_bid >= best_ask:
        raise DataError("Use an uncrossed scenario: best bid must be below best ask.")
    return best_bid, best_ask, best_ask - best_bid


def quote_text(data: MarketData, through: date | None = None) -> str:
    candles = tuple(b for b in data.candles if through is None or b.session <= through)
    if not candles:
        return f"{data.symbol} / {data.exchange}: no observations revealed yet."
    bar = candles[-1]
    change = (
        f"{bar.close - candles[-2].close:+.2f} / {100 * (bar.close / candles[-2].close - 1):+.2f}%"
        if len(candles) > 1
        else "Unknown: no previous observation"
    )
    sma20 = f"{fmean(b.close for b in candles[-20:]):,.2f}" if len(candles) >= 20 else "Not ready"
    return (
        f"{data.symbol} / {data.exchange} | completed {bar.session}\n"
        f"Adjusted close INR {bar.close:,.2f} | change {change}\n"
        f"O {bar.open:,.2f}  H {bar.high:,.2f}  L {bar.low:,.2f}  "
        f"C {bar.close:,.2f} | reported volume {bar.volume:,.0f}\n"
        f"20-observation SMA {sma20}\n"
        f"{data.source} | fetched {data.fetched_at.isoformat()}\n"
        f"{data.price_basis}\n" + "\n".join(data.warnings)
    )


@dataclass(frozen=True)
class PaperOrder:
    number: int
    submitted: date
    side: Side
    kind: OrderType
    units: float
    limit: float | None = None
    trigger: float | None = None
    validity: Validity = "Next opening"
    status: str = "Pending"
    activated: bool = False
    price: float | None = None
    fee: float = 0
    message: str = "Waiting for a later observed opening."
    updated: date | None = None


class PaperAccount:
    """Single-instrument opening-only exercise, separate from algorithm accounting."""

    def __init__(self, capital: float, fee_bps: float = 10, slippage_bps: float = 10) -> None:
        positive("Capital", capital)
        basis_points("Fee", fee_bps)
        basis_points("Slippage", slippage_bps)
        self.capital = self.cash = capital
        self.fee_bps, self.slippage_bps = fee_bps, slippage_bps
        self.units = self.cost = self.realised = self.fees = 0.0
        self.orders: list[PaperOrder] = []
        self.last_session: date | None = None

    def submit(
        self,
        submitted: date,
        side: Side,
        kind: OrderType,
        units: float,
        limit: float | None = None,
        trigger: float | None = None,
        validity: Validity = "Next opening",
    ) -> PaperOrder:
        positive("Order units", units)
        if self.last_session is None or submitted != self.last_session:
            raise DataError("Submit only at the account's currently revealed completed session.")
        if (
            side not in ("Buy", "Sell")
            or kind not in ("Market", "Limit", "Stop market", "Stop limit")
            or validity not in ("Next opening", "Until cancelled")
        ):
            raise DataError("Unsupported order side, type or validity.")
        needs_limit = kind in ("Limit", "Stop limit")
        needs_trigger = kind in ("Stop market", "Stop limit")
        if needs_limit != (limit is not None) or needs_trigger != (trigger is not None):
            raise DataError("Supply exactly the limit/trigger fields required by this order type.")
        if limit is not None:
            positive("Limit", limit)
        if trigger is not None:
            positive("Trigger", trigger)
        if kind == "Stop limit" and limit is not None and trigger is not None:
            if (side == "Buy" and limit < trigger) or (side == "Sell" and limit > trigger):
                raise DataError("Buy stop limit >= trigger; sell stop limit <= trigger.")
        order = PaperOrder(
            len(self.orders) + 1,
            submitted,
            side,
            kind,
            units,
            limit,
            trigger,
            validity,
            updated=submitted,
        )
        self.orders.append(order)
        return order

    def cancel(self, number: int) -> None:
        if type(number) is not int or not 1 <= number <= len(self.orders):
            raise DataError("Choose an existing order number.")
        order = self.orders[number - 1]
        if order.status != "Pending":
            raise DataError("Only pending orders can be cancelled.")
        self.orders[number - 1] = replace(
            order,
            status="Cancelled",
            message="Cancelled locally before a later opening.",
            updated=self.last_session,
        )

    def advance(self, bar: Candle) -> None:
        if self.last_session is not None and bar.session <= self.last_session:
            raise DataError("Paper clock must advance to a strictly later observation.")
        self.last_session = bar.session
        for index, order in enumerate(self.orders):
            if order.status != "Pending" or bar.session <= order.submitted:
                continue
            buy = order.side == "Buy"
            activated = (
                order.activated
                or order.trigger is None
                or (bar.open >= order.trigger if buy else bar.open <= order.trigger)
            )
            marketable = activated and (
                order.limit is None or (bar.open <= order.limit if buy else bar.open >= order.limit)
            )
            if not marketable:
                expired = order.validity == "Next opening"
                self.orders[index] = replace(
                    order,
                    activated=activated,
                    status="Expired" if expired else "Pending",
                    message=(
                        "Not executable at this opening; no intraday fill assumed."
                        + (" Local validity ended." if expired else "")
                    ),
                    updated=bar.session,
                )
                continue
            slip = self.slippage_bps / 10000
            price = bar.open * (1 + slip if buy else 1 - slip)
            if order.limit is not None:
                price = min(price, order.limit) if buy else max(price, order.limit)
            value = order.units * price
            fee = value * self.fee_bps / 10000
            rejection = ""
            if buy and value + fee > self.cash:
                rejection = "Insufficient cash at this opening; no partial fill."
            elif not buy and order.units > self.units:
                rejection = "Insufficient owned units; shorts are unavailable."
            if rejection:
                self.orders[index] = replace(
                    order,
                    status="Rejected",
                    message=rejection,
                    activated=activated,
                    updated=bar.session,
                )
                continue
            if buy:
                self.cash -= value + fee
                self.cost += value + fee
                self.units += order.units
            else:
                removed_cost = self.cost * order.units / self.units
                self.cash += value - fee
                self.realised += value - fee - removed_cost
                self.cost -= removed_cost
                self.units -= order.units
            self.fees += fee
            self.orders[index] = replace(
                order,
                status="Filled",
                activated=activated,
                price=price,
                fee=fee,
                message=f"Opening-only assumed full fill on {bar.session}; no queue/depth model.",
                updated=bar.session,
            )

    def summary(self, close: float) -> str:
        positive("Mark price", close)
        value = self.units * close
        total = self.cash + value
        return (
            f"Cash INR {self.cash:,.2f} | adjusted research units {self.units:,.4f} | "
            f"cost including entry fees INR {self.cost:,.2f}\n"
            f"Realised P&L INR {self.realised:+,.2f} | "
            f"unrealised P&L INR {value - self.cost:+,.2f} | fees INR {self.fees:,.2f}\n"
            f"Marked account INR {total:,.2f} | P&L INR {total - self.capital:+,.2f} "
            f"({100 * (total / self.capital - 1):+.2f}%). No forced final sale."
        )


def watchlist_document(entries: tuple[tuple[str, str], ...]) -> dict[str, object]:
    if len(entries) > 50 or len(set(entries)) != len(entries):
        raise DataError("A local watchlist supports at most 50 unique instruments.")
    for symbol, exchange in entries:
        if yahoo_symbol(symbol, exchange) != symbol:
            raise DataError(
                "Use a canonical uppercase ticker with .NS/.BO suffix and NSE/BSE exchange."
            )
    return {
        "schema": 1,
        "instruments": [{"symbol": symbol, "exchange": exchange} for symbol, exchange in entries],
    }


def load_watchlist(path: Path) -> tuple[tuple[str, str], ...]:
    if path.stat().st_size > 32768:
        raise DataError("Watchlist exceeds 32 KiB.")

    def unique_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
        fields: dict[str, object] = {}
        for key, value in pairs:
            if key in fields:
                raise DataError(f"Duplicate watchlist field: {key}")
            fields[key] = value
        return fields

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_fields)
    if not isinstance(value, dict) or set(value) != {"schema", "instruments"}:
        raise DataError("Expected watchlist schema and instruments only.")
    if type(value["schema"]) is not int or value["schema"] != 1:
        raise DataError("Unsupported watchlist schema.")
    items = value["instruments"]
    if not isinstance(items, list):
        raise DataError("Instruments must be a list.")
    entries: list[tuple[str, str]] = []
    for item in items:
        if (
            not isinstance(item, dict)
            or set(item) != {"symbol", "exchange"}
            or not isinstance(item["symbol"], str)
            or not isinstance(item["exchange"], str)
        ):
            raise DataError("Each instrument needs exactly symbol and exchange strings.")
        entries.append((item["symbol"], item["exchange"]))
    result = tuple(entries)
    watchlist_document(result)
    return result
