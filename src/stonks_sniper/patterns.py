from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean, pstdev

from stonks_sniper.models import Candle

CHARTS = "https://chartschool.stockcharts.com/table-of-contents"
OVERLAYS = f"{CHARTS}/technical-indicators-and-overlays/technical-overlays"
INDICATORS = f"{CHARTS}/technical-indicators-and-overlays/technical-indicators"


@dataclass(frozen=True)
class Pattern:
    key: str
    name: str
    minimum_bars: int
    rules: str
    limitations: str
    source: str


PATTERNS = (
    Pattern(
        "sma",
        "SMA trend (10 / 30)",
        30,
        "At each close, hold long when the last 10 closes average above the last 30; "
        "otherwise hold cash. First actionable target occurs after 30 bars.",
        "A teaching variant, not a universal rule. Sideways markets can cause repeated losses.",
        f"{OVERLAYS}/moving-averages-simple-and-exponential",
    ),
    Pattern(
        "ema",
        "EMA trend (12 / 26)",
        26,
        "Hold long when EMA(12) exceeds EMA(26), otherwise cash. EMAs are seeded with "
        "their first complete simple average, then use alpha = 2 / (period + 1).",
        "Initialization and lookback affect early signals; trend filters lag reversals.",
        f"{OVERLAYS}/moving-averages-simple-and-exponential",
    ),
    Pattern(
        "rsi",
        "RSI reversion (14; 30 / 70)",
        15,
        "Wilder RSI(14): enter long at RSI <= 30, exit at RSI >= 70; retain the "
        "current target between thresholds. Flat prices produce neutral RSI 50.",
        "Oversold can remain oversold. The thresholds define this variant, not a prediction.",
        f"{INDICATORS}/relative-strength-index-rsi",
    ),
    Pattern(
        "donchian",
        "Donchian breakout (20)",
        21,
        "Enter above the previous 20 session highs; exit below the previous 20 "
        "session lows. The current candle is excluded from channel construction.",
        "Whipsaws and overnight gaps matter. No short selling or intraday stop inference.",
        f"{OVERLAYS}/price-channels",
    ),
    Pattern(
        "bollinger",
        "Bollinger reversion (20; 2 sigma)",
        20,
        "Enter when close is below SMA(20) minus 2 population standard deviations; "
        "exit when close reaches SMA(20). Retain target otherwise.",
        "Bands are not guaranteed price bounds. Sharp downtrends can defeat mean reversion.",
        f"{OVERLAYS}/bollinger-bands",
    ),
    Pattern(
        "macd",
        "MACD signal trend (12 / 26 / 9)",
        34,
        "MACD = EMA(12) - EMA(26). Hold long above its EMA(9) signal line; "
        "otherwise cash. Each EMA uses a complete-window simple-average seed.",
        "A lagging trend variant; different platforms may initialize EMAs differently.",
        f"{INDICATORS}/macd-moving-average-convergence-divergence-oscillator",
    ),
    Pattern(
        "engulfing",
        "Body engulfing reversal",
        2,
        "After a red body, a green body enclosing the previous body enters long; "
        "the inverse exits. Equal body boundaries are allowed, doji bodies excluded.",
        "Body-only teaching variant: no trend/volume confirmation; may hold indefinitely. "
        "Exact boundary comparisons are sensitive to small adjusted-price revisions; "
        "export the run to preserve its inputs. A candle shape alone is not a "
        "complete validated strategy.",
        f"{CHARTS}/chart-analysis/candlestick-charts/candlestick-pattern-dictionary",
    ),
)


def ema(values: list[float], period: int) -> list[float | None]:
    result: list[float | None] = [None] * len(values)
    if len(values) < period:
        return result
    value = fmean(values[:period])
    result[period - 1] = value
    alpha = 2 / (period + 1)
    for index in range(period, len(values)):
        value += alpha * (values[index] - value)
        result[index] = value
    return result


def wilder_rsi(values: list[float], period: int = 14) -> list[float | None]:
    result: list[float | None] = [None] * len(values)
    if len(values) <= period:
        return result
    changes = [right - left for left, right in zip(values, values[1:], strict=False)]
    gain = fmean(max(change, 0) for change in changes[:period])
    loss = fmean(max(-change, 0) for change in changes[:period])
    for index in range(period, len(values)):
        if index > period:
            gain = (gain * (period - 1) + max(changes[index - 1], 0)) / period
            loss = (loss * (period - 1) + max(-changes[index - 1], 0)) / period
        result[index] = (
            50.0 if gain == loss == 0 else 100.0 if loss == 0 else 100 - 100 / (1 + gain / loss)
        )
    return result


def targets(candles: tuple[Candle, ...], pattern: Pattern) -> tuple[bool | None, ...]:
    if pattern not in PATTERNS:
        raise ValueError("Select a registered pattern.")
    closes = [candle.close for candle in candles]
    fast = ema(closes, 12) if pattern.key in {"ema", "macd"} else []
    slow = ema(closes, 26) if pattern.key in {"ema", "macd"} else []
    rsi = wilder_rsi(closes) if pattern.key == "rsi" else []
    macd = [
        short - long
        for short, long in zip(fast, slow, strict=True)
        if short is not None and long is not None
    ]
    signal = ema(macd, 9) if pattern.key == "macd" else []
    result: list[bool | None] = []
    holding = False
    for index, candle in enumerate(candles):
        if index + 1 < pattern.minimum_bars:
            result.append(None)
            continue
        close = candle.close
        if pattern.key == "sma":
            holding = fmean(closes[index - 9 : index + 1]) > fmean(closes[index - 29 : index + 1])
        elif pattern.key == "ema":
            short, long = fast[index], slow[index]
            assert short is not None and long is not None
            holding = short > long
        elif pattern.key == "rsi":
            value = rsi[index]
            assert value is not None
            if value <= 30:
                holding = True
            elif value >= 70:
                holding = False
        elif pattern.key == "donchian":
            prior = candles[index - 20 : index]
            if close > max(bar.high for bar in prior):
                holding = True
            elif close < min(bar.low for bar in prior):
                holding = False
        elif pattern.key == "bollinger":
            window = closes[index - 19 : index + 1]
            middle = fmean(window)
            if close < middle - 2 * pstdev(window):
                holding = True
            elif close >= middle:
                holding = False
        elif pattern.key == "macd":
            signal_value = signal[index - 25]
            assert signal_value is not None
            holding = macd[index - 25] > signal_value
        elif pattern.key == "engulfing":
            prior_bar = candles[index - 1]
            if (
                prior_bar.close < prior_bar.open
                and close > candle.open
                and candle.open <= prior_bar.close
                and close >= prior_bar.open
            ):
                holding = True
            elif (
                prior_bar.close > prior_bar.open
                and close < candle.open
                and candle.open >= prior_bar.close
                and close <= prior_bar.open
            ):
                holding = False
        result.append(holding)
    return tuple(result)
