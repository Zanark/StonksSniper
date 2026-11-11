from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date

from stonks_sniper.models import MarketData
from stonks_sniper.patterns import Pattern, targets


@dataclass(frozen=True)
class Assumptions:
    initial_cash: float = 100_000
    fee_bps: float = 10
    slippage_bps: float = 10

    def __post_init__(self) -> None:
        if not math.isfinite(self.initial_cash) or self.initial_cash <= 0:
            raise ValueError("Initial capital must be finite and positive.")
        for value in (self.fee_bps, self.slippage_bps):
            if not math.isfinite(value) or not 0 <= value < 10_000:
                raise ValueError("Fee and slippage must be finite and in [0, 10000) bps.")


@dataclass(frozen=True)
class Trade:
    signal_session: date
    fill_session: date
    side: str
    price: float
    units: float
    fee: float
    cash_after: float


@dataclass(frozen=True)
class Result:
    pattern: Pattern
    assumptions: Assumptions
    targets: tuple[bool | None, ...]
    trades: tuple[Trade, ...]
    equity: tuple[float, ...]
    benchmark: tuple[float, ...]
    max_drawdown_pct: float
    open_units: float

    @property
    def return_pct(self) -> float:
        return (self.equity[-1] / self.assumptions.initial_cash - 1) * 100

    @property
    def benchmark_return_pct(self) -> float:
        return (self.benchmark[-1] / self.assumptions.initial_cash - 1) * 100


DEFAULT_ASSUMPTIONS = Assumptions()


def simulate(
    data: MarketData, pattern: Pattern, assumptions: Assumptions = DEFAULT_ASSUMPTIONS
) -> Result:
    if len(data.candles) < pattern.minimum_bars + 1:
        raise ValueError(
            f"{pattern.name} needs at least {pattern.minimum_bars + 1} completed bars "
            "including one next-session execution bar."
        )
    desired = targets(data.candles, pattern)
    cash = assumptions.initial_cash
    units = 0.0
    fee_rate = assumptions.fee_bps / 10_000
    slip = assumptions.slippage_bps / 10_000
    trades: list[Trade] = []
    equity: list[float] = []
    benchmark: list[float] = []
    benchmark_units = 0.0
    peak = cash
    drawdown = 0.0
    for index, candle in enumerate(data.candles):
        previous_target = desired[index - 1] if index else None
        if previous_target is not None:
            if previous_target and units == 0:
                price = candle.open * (1 + slip)
                units = cash / (price * (1 + fee_rate))
                fee = units * price * fee_rate
                cash = 0.0
                trades.append(
                    Trade(
                        data.candles[index - 1].session,
                        candle.session,
                        "BUY",
                        price,
                        units,
                        fee,
                        cash,
                    )
                )
            elif not previous_target and units > 0:
                price = candle.open * (1 - slip)
                fee = units * price * fee_rate
                cash = units * price - fee
                trades.append(
                    Trade(
                        data.candles[index - 1].session,
                        candle.session,
                        "SELL",
                        price,
                        units,
                        fee,
                        cash,
                    )
                )
                units = 0.0
        if index == pattern.minimum_bars:
            benchmark_units = assumptions.initial_cash / (candle.open * (1 + slip) * (1 + fee_rate))
        benchmark.append(
            benchmark_units * candle.close if benchmark_units else assumptions.initial_cash
        )
        value = cash + units * candle.close
        equity.append(value)
        peak = max(peak, value)
        drawdown = max(drawdown, (peak - value) / peak * 100)
    return Result(
        pattern,
        assumptions,
        desired,
        tuple(trades),
        tuple(equity),
        tuple(benchmark),
        drawdown,
        units,
    )
