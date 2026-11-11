from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import accumulate
from statistics import fmean, pstdev

from stonks_sniper.models import Candle

Series = list[float | None]


@dataclass(frozen=True)
class Study:
    targets: tuple[bool | None, ...]
    guides: tuple[tuple[str, Series], ...]


def ema(values: Sequence[float | None], period: int, *, wilder: bool = False) -> Series:
    result: Series = []
    seed: list[float] = []
    value = None
    alpha = 1 / period if wilder else 2 / (period + 1)
    for observation in values:
        if observation is None:
            seed.clear()
            value = None
        elif value is None:
            seed.append(observation)
            if len(seed) == period:
                value = fmean(seed)
        else:
            value += alpha * (observation - value)
        result.append(value)
    return result


def sma(values: Sequence[float | None], period: int) -> Series:
    result: Series = [None] * len(values)
    for index in range(period - 1, len(values)):
        window = values[index - period + 1 : index + 1]
        available = [value for value in window if value is not None]
        if len(available) == period:
            result[index] = fmean(available)
    return result


def true_ranges(candles: tuple[Candle, ...]) -> list[float]:
    return [
        max(bar.high, candles[index - 1].close) - min(bar.low, candles[index - 1].close)
        if index
        else bar.high - bar.low
        for index, bar in enumerate(candles)
    ]


def _difference(left: Sequence[float | None], right: Sequence[float | None]) -> Series:
    return [
        a - b if a is not None and b is not None else None for a, b in zip(left, right, strict=True)
    ]


def _thresholds(
    values: Series, buy: float = 0, sell: float = 0, *, reversion: bool = False
) -> tuple[bool | None, ...]:
    holding = False
    result: list[bool | None] = []
    for value in values:
        if value is None:
            result.append(None)
            continue
        enter = value <= buy if reversion else value > buy
        leave = value >= sell if reversion else value <= sell
        if enter:
            holding = True
        elif leave:
            holding = False
        result.append(holding)
    return tuple(result)


def _midpoints(candles: tuple[Candle, ...], period: int) -> Series:
    return [
        (
            max(bar.high for bar in candles[index - period + 1 : index + 1])
            + min(bar.low for bar in candles[index - period + 1 : index + 1])
        )
        / 2
        if index + 1 >= period
        else None
        for index in range(len(candles))
    ]


def _breakout(closes: list[float], upper: Series, middle: Series) -> tuple[bool | None, ...]:
    holding = False
    result: list[bool | None] = []
    for close, top, average in zip(closes, upper, middle, strict=True):
        if top is None or average is None:
            result.append(None)
            continue
        if close > top:
            holding = True
        elif close <= average:
            holding = False
        result.append(holding)
    return tuple(result)


def study(candles: tuple[Candle, ...], key: str) -> Study:
    """Compute each added rule and its replay guides from the same causal values."""
    closes = [bar.close for bar in candles]
    count = len(candles)
    zero: Series = [0.0] * count
    values: Series
    guides: tuple[tuple[str, Series], ...]
    buy = sell = 0.0
    reversion = False
    if key in {"stochastic", "williams"}:
        raw: Series = [None] * count
        for index in range(13, count):
            window = candles[index - 13 : index + 1]
            low, high = min(bar.low for bar in window), max(bar.high for bar in window)
            raw[index] = 100 * (closes[index] - low) / (high - low) if high > low else 50
        if key == "stochastic":
            values = sma(raw, 3)
            buy, sell, reversion = 20, 80, True
            guides = (
                ("Smoothed range score (%D)", values),
                ("Buy at 20 or below", [20.0] * count),
                ("Sell at 80 or above", [80.0] * count),
            )
        else:
            values = [value - 100 if value is not None else None for value in raw]
            buy = sell = -50
            guides = (("Williams %R", values), ("Halfway: -50", [-50.0] * count))
    elif key == "cci":
        typical = [(bar.high + bar.low + bar.close) / 3 for bar in candles]
        values = [None] * count
        for index in range(19, count):
            typical_window = typical[index - 19 : index + 1]
            typical_mean = fmean(typical_window)
            deviation = fmean(abs(value - typical_mean) for value in typical_window)
            values[index] = (
                (typical[index] - typical_mean) / (0.015 * deviation) if deviation else 0
            )
        buy = 100
        guides = (
            ("Distance from usual (CCI)", values),
            ("Buy above 100", [100.0] * count),
            ("Sell at zero or below", zero),
        )
    elif key == "roc":
        values = [
            100 * (close / closes[index - 12] - 1) if index >= 12 else None
            for index, close in enumerate(closes)
        ]
        guides = (("12-day percentage change (ROC)", values), ("No change", zero))
    elif key == "tsi":
        changes: Series = [None] + [b - a for a, b in zip(closes, closes[1:], strict=False)]
        if not count:
            changes = []
        numerator = ema(ema(changes, 25), 13)
        absolute = [abs(value) if value is not None else None for value in changes]
        denominator = ema(ema(absolute, 25), 13)
        values = [
            (100 * top / bottom if bottom else 0.0)
            if top is not None and bottom is not None
            else None
            for top, bottom in zip(numerator, denominator, strict=True)
        ]
        guides = (("Twice-smoothed strength (TSI)", values), ("Zero", zero))
    elif key == "adx":
        ranges: Series = [None, *true_ranges(candles)[1:]] if count else []
        positive: Series = [None] if count else []
        negative: Series = [None] if count else []
        for previous, bar in zip(candles, candles[1:], strict=False):
            up, down = bar.high - previous.high, previous.low - bar.low
            positive.append(up if up > down and up > 0 else 0)
            negative.append(down if down > up and down > 0 else 0)
        atr, plus, minus = (ema(series, 14, wilder=True) for series in (ranges, positive, negative))
        plus_di: Series = []
        minus_di: Series = []
        dx: Series = []
        for spread, up_average, down_average in zip(atr, plus, minus, strict=True):
            if spread is None or up_average is None or down_average is None:
                plus_di.append(None)
                minus_di.append(None)
                dx.append(None)
            else:
                plus_di.append(100 * up_average / spread if spread else 0)
                minus_di.append(100 * down_average / spread if spread else 0)
                total_movement = up_average + down_average
                dx.append(
                    100 * abs(up_average - down_average) / total_movement if total_movement else 0
                )
        strength = ema(dx, 14, wilder=True)
        values = [
            (up - down if power >= 25 else 0)
            if power is not None and up is not None and down is not None
            else None
            for power, up, down in zip(strength, plus_di, minus_di, strict=True)
        ]
        guides = (
            ("Trend strength (ADX)", strength),
            ("Up direction (+DI)", plus_di),
            ("Down direction (-DI)", minus_di),
            ("Strength gate: 25", [25.0] * count),
        )
    elif key == "aroon":
        upper: Series = [None] * count
        lower: Series = [None] * count
        for index in range(25, count):
            window = candles[index - 25 : index + 1]
            # Most recent tied extreme wins, with possible ages 0 through 25.
            high_at = max(range(26), key=lambda i: (window[i].high, i))
            low_at = min(range(26), key=lambda i: (window[i].low, -i))
            upper[index], lower[index] = high_at * 4.0, low_at * 4.0
        values = [
            (up - down if up >= 70 else 0) if up is not None and down is not None else None
            for up, down in zip(upper, lower, strict=True)
        ]
        guides = (
            ("Recency of high (Aroon Up)", upper),
            ("Recency of low (Aroon Down)", lower),
            ("Up must reach 70", [70.0] * count),
        )
    elif key == "ichimoku":
        conversion, base, span_b = (_midpoints(candles, period) for period in (9, 26, 52))
        raw_a = [
            (a + b) / 2 if a is not None and b is not None else None
            for a, b in zip(conversion, base, strict=True)
        ]
        cloud_a = [raw_a[i - 26] if i >= 26 else None for i in range(count)]
        cloud_b = [span_b[i - 26] if i >= 26 else None for i in range(count)]
        values = [
            float(close > max(a, b) and fast > slow)
            if a is not None and b is not None and fast is not None and slow is not None
            else None
            for close, a, b, fast, slow in zip(
                closes, cloud_a, cloud_b, conversion, base, strict=True
            )
        ]
        guides = (
            ("Close", list(closes)),
            ("9-day range middle", conversion),
            ("26-day range middle", base),
            ("Visible cloud A (26 days old)", cloud_a),
            ("Visible cloud B (26 days old)", cloud_b),
        )
    elif key in {"keltner", "bollinger-breakout"}:
        if key == "keltner":
            middle = ema(closes, 20)
            atr = ema(true_ranges(candles), 10, wilder=True)
            upper = [
                average + 2 * spread if average is not None and spread is not None else None
                for average, spread in zip(middle, atr, strict=True)
            ]
        else:
            middle = sma(closes, 20)
            upper = [
                average + 2 * pstdev(closes[index - 19 : index + 1])
                if average is not None
                else None
                for index, average in enumerate(middle)
            ]
        return Study(
            _breakout(closes, upper, middle),
            (
                ("Close", list(closes)),
                ("Upper band (buy above)", upper),
                ("Middle line (sell at or below)", middle),
            ),
        )
    elif key == "chandelier":
        atr = ema(true_ranges(candles), 22, wilder=True)
        average = sma(closes, 22)
        exit_line: Series = [None] * count
        result: list[bool | None] = []
        holding = False
        stop: float | None = None
        for index, (close, spread, mean) in enumerate(zip(closes, atr, average, strict=True)):
            if spread is None or mean is None:
                result.append(None)
                continue
            candidate = max(bar.high for bar in candles[index - 21 : index + 1]) - 3 * spread
            if holding:
                assert stop is not None
                stop = max(stop, candidate)
                exit_line[index] = stop
                if close <= stop:
                    holding, stop = False, None
            elif close > mean and close > candidate:
                holding, stop = True, candidate
                exit_line[index] = stop
            result.append(holding)
        return Study(
            tuple(result),
            (
                ("Close", list(closes)),
                ("22-day entry average", average),
                ("Ratcheted exit while owning", exit_line),
            ),
        )
    elif key == "obv":
        signed = [0.0] if count else []
        for previous, bar in zip(candles, candles[1:], strict=False):
            signed.append(
                bar.volume
                if bar.close > previous.close
                else -bar.volume
                if bar.close < previous.close
                else 0
            )
        balance: Series = list(accumulate(signed))
        average = ema(balance, 20)
        values = _difference(balance, average)
        guides = (("Volume balance (OBV)", balance), ("20-day smoothed balance", average))
    elif key in {"cmf", "chaikin"}:
        flow = [
            (2 * bar.close - bar.high - bar.low) / (bar.high - bar.low) * bar.volume
            if bar.high > bar.low
            else 0
            for bar in candles
        ]
        if key == "cmf":
            values = [None] * count
            for index in range(19, count):
                volume = sum(bar.volume for bar in candles[index - 19 : index + 1])
                values[index] = sum(flow[index - 19 : index + 1]) / volume if volume else 0
            guides = (("20-day close-location flow (CMF)", values), ("Zero", zero))
        else:
            distribution = list(accumulate(flow))
            values = _difference(ema(distribution, 3), ema(distribution, 10))
            guides = (("Change in volume flow (Chaikin)", values), ("Zero", zero))
    elif key == "mfi":
        typical = [(bar.high + bar.low + bar.close) / 3 for bar in candles]
        positive_flow = [0.0] * count
        negative_flow = [0.0] * count
        for index in range(1, count):
            flow_value = typical[index] * candles[index].volume
            if typical[index] > typical[index - 1]:
                positive_flow[index] = flow_value
            elif typical[index] < typical[index - 1]:
                negative_flow[index] = flow_value
        values = [None] * count
        for index in range(14, count):
            up = sum(positive_flow[index - 13 : index + 1])
            down = sum(negative_flow[index - 13 : index + 1])
            values[index] = 100 * up / (up + down) if up + down else 50
        buy, sell, reversion = 20, 80, True
        guides = (
            ("Price-and-volume score (MFI)", values),
            ("Buy at 20 or below", [20.0] * count),
            ("Sell at 80 or above", [80.0] * count),
        )
    elif key == "emv":
        raw_emv: Series = [None] if count else []
        for previous, bar in zip(candles, candles[1:], strict=False):
            distance = (bar.high + bar.low - previous.high - previous.low) / 2
            raw_emv.append(
                distance * (bar.high - bar.low) * 100_000_000 / bar.volume if bar.volume else 0
            )
        values = sma(raw_emv, 14)
        guides = (("Ease of movement (EMV)", values), ("Zero", zero))
    elif key in {"ultimate", "vortex"}:
        movement_ranges = true_ranges(candles)
        values = [None] * count
        if key == "ultimate":
            pressure = [0.0] * count
            for index in range(1, count):
                pressure[index] = closes[index] - min(candles[index].low, closes[index - 1])
            for index in range(28, count):
                ratios = []
                for period in (7, 14, 28):
                    spread = sum(movement_ranges[index - period + 1 : index + 1])
                    ratios.append(
                        sum(pressure[index - period + 1 : index + 1]) / spread if spread else 0.5
                    )
                values[index] = 100 * (4 * ratios[0] + 2 * ratios[1] + ratios[2]) / 7
            buy = sell = 50
            guides = (("Three-window pressure (Ultimate)", values), ("Halfway: 50", [50.0] * count))
        else:
            plus_vm = [0.0] * count
            minus_vm = [0.0] * count
            for index in range(1, count):
                plus_vm[index] = abs(candles[index].high - candles[index - 1].low)
                minus_vm[index] = abs(candles[index].low - candles[index - 1].high)
            plus_vi: Series = [None] * count
            minus_vi: Series = [None] * count
            for index in range(14, count):
                spread = sum(movement_ranges[index - 13 : index + 1])
                plus_vi[index] = sum(plus_vm[index - 13 : index + 1]) / spread if spread else 0
                minus_vi[index] = sum(minus_vm[index - 13 : index + 1]) / spread if spread else 0
            values = _difference(plus_vi, minus_vi)
            guides = (("Upward movement (+VI)", plus_vi), ("Downward movement (-VI)", minus_vi))
    elif key == "trix":
        triple = ema(ema(ema(closes, 15), 15), 15)
        values = [None] * count
        for index in range(1, count):
            current, previous_value = triple[index], triple[index - 1]
            if current is not None and previous_value is not None:
                values[index] = 100 * (current / previous_value - 1)
        guides = (("Triple-smoothed daily change (TRIX)", values), ("Zero", zero))
    elif key == "force":
        force: Series = [None] if count else []
        force.extend(
            (bar.close - previous.close) * bar.volume
            for previous, bar in zip(candles, candles[1:], strict=False)
        )
        values = ema(force, 13)
        guides = (("Price change times volume (Force)", values), ("Zero", zero))
    else:
        raise ValueError(f"No study is registered for {key!r}.")
    return Study(_thresholds(values, buy, sell, reversion=reversion), guides)
