from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean, pstdev

from stonks_sniper.models import Candle
from stonks_sniper.studies import ema as ema
from stonks_sniper.studies import study

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
    Pattern(
        "stochastic",
        "Stochastic range reversion (14 / 3; 20 / 80)",
        16,
        "Fast %K = 100 * (close - 14-day low) / (14-day high - low), including today. "
        "%D = SMA(3) of %K. Enter at %D <= 20; exit at %D >= 80; retain between. "
        "A zero-width range has neutral %K = 50.",
        "Weakness can persist. This smoothed threshold variant is not a divergence detector.",
        f"{INDICATORS}/stochastic-oscillator-fast-slow-and-full",
    ),
    Pattern(
        "williams",
        "Williams %R range momentum (14; -50)",
        14,
        "%R = -100 * (14-day high - close) / (14-day high - low), including today. "
        "Hold long above -50; otherwise cash. A zero-width range is neutral -50.",
        "Equivalent to unsmoothed stochastic %K minus 100, not independent evidence. "
        "Unlike our Stochastic reversion rule, this follows upper-half strength.",
        f"{INDICATORS}/williams-r",
    ),
    Pattern(
        "cci",
        "CCI strength entry (20; 100 / 0)",
        20,
        "Typical price = (high + low + close) / 3. CCI = (typical - SMA20) / "
        "(0.015 * mean absolute deviation of the same 20 typical prices). "
        "Enter above 100; exit at or below 0; retain between. Zero deviation gives CCI 0.",
        "A large move can reverse immediately. CCI is not a percentage or a fair-value estimate.",
        f"{INDICATORS}/commodity-channel-index-cci",
    ),
    Pattern(
        "roc",
        "Rate-of-change momentum (12)",
        13,
        "ROC = 100 * (close / close 12 sessions earlier - 1). Hold long above 0; otherwise cash.",
        "One old comparison price dropping out can flip the decision without important new news.",
        f"{INDICATORS}/rate-of-change-roc",
    ),
    Pattern(
        "tsi",
        "True Strength Index trend (25 / 13)",
        38,
        "TSI = 100 * EMA13(EMA25(close change)) / EMA13(EMA25(abs(close change))). "
        "Each EMA starts with its first complete-window simple average; the first "
        "change requires two closes. Zero denominator gives neutral TSI 0. "
        "Hold long above 0; otherwise cash.",
        "Double smoothing delays reversals. Minimum seed history is not fully settled history.",
        f"{INDICATORS}/true-strength-index",
    ),
    Pattern(
        "adx",
        "ADX directional-strength filter (14; 25)",
        28,
        "+DM uses positive high expansion only when it exceeds low expansion; -DM is "
        "the mirror image. Ties give both zero. Wilder-average 14 changes and true "
        "ranges for +DI/-DI. DX = 100 * abs(+DI - -DI) / (+DI + -DI); Wilder-average "
        "14 DX values for ADX. Zero denominators give zero. Hold long only when "
        "+DI > -DI and ADX >= 25; otherwise cash.",
        "ADX measures strength, not direction. Early seeded values can differ from "
        "longer histories; roughly 150 bars may be needed for settling.",
        f"{INDICATORS}/average-directional-index-adx",
    ),
    Pattern(
        "aroon",
        "Aroon recent-high trend (25; 70)",
        26,
        "Use 26 observations for extreme ages 0..25. Aroon Up/Down = "
        "100 * (25 - age of highest high / lowest low) / 25. Most recent tied "
        "extreme wins. Hold long if Up > Down and Up >= 70; otherwise cash.",
        "A fresh tiny high can score strongly; the indicator measures recency, not move size.",
        f"{INDICATORS}/aroon",
    ),
    Pattern(
        "ichimoku",
        "Ichimoku visible-cloud trend (9 / 26 / 52)",
        78,
        "Conversion/base are midpoints of 9/26-day high-low ranges. Raw cloud A is "
        "their mean; raw B is the 52-day range midpoint. The visible cloud at i uses "
        "raw A/B computed at i-26. Hold long when close exceeds both visible "
        "boundaries and conversion > base; otherwise cash. No lagging-span test.",
        "The cloud's drawing shift is not a forecast. This variant needs 78 completed "
        "bars and does not backdate decisions onto a lagging line.",
        f"{OVERLAYS}/ichimoku-cloud",
    ),
    Pattern(
        "keltner",
        "Keltner channel breakout (20 / 10; 2 ATR)",
        20,
        "Middle = EMA20(close); upper = middle + 2 * Wilder ATR10. "
        "True range includes gaps; first TR is high-low; ATR seeds with a full average. "
        "Enter when close > upper; exit when close <= middle; retain otherwise.",
        "Large gaps may reverse and next-open fills can be far from the channel.",
        f"{OVERLAYS}/keltner-channels",
    ),
    Pattern(
        "bollinger-breakout",
        "Bollinger strength breakout (20; 2 sigma)",
        20,
        "Upper = SMA20(close) + 2 population standard deviations of those 20 closes. "
        "Enter above the upper band; exit at or below SMA20; retain otherwise.",
        "Opposite entry idea to our lower-band reversion rule; neither is guaranteed. "
        "No squeeze, W-bottom or divergence detection is implied.",
        f"{OVERLAYS}/bollinger-bands",
    ),
    Pattern(
        "chandelier",
        "Chandelier ratcheted exit (22; 3 ATR)",
        22,
        "Candidate exit = highest high of latest 22 bars - 3 * Wilder ATR22; first "
        "TR is high-low. Enter from cash when close > SMA22 and close > candidate. "
        "While long, exit level = max(previous exit level, today's candidate). "
        "Exit at close <= level; reset after exit, with no same-close re-entry.",
        "The source's rolling exit can fall; this app adds a ratchet and SMA entry. "
        "This is a close-confirmed next-open sale, not an intraday stop or guaranteed price.",
        f"{OVERLAYS}/chandelier-exit",
    ),
    Pattern(
        "obv",
        "On-balance-volume trend (20)",
        20,
        "OBV starts at 0. Add today's volume on a higher close; subtract on a lower "
        "close; add zero on equal closes. Hold long if OBV > EMA20(OBV); otherwise cash.",
        "One unusual volume day can dominate. Reported volume quality matters; "
        "OBV does not measure actual money entering a company.",
        f"{INDICATORS}/on-balance-volume-obv",
    ),
    Pattern(
        "cmf",
        "Chaikin Money Flow pressure (20)",
        20,
        "Multiplier = (2 * close - high - low) / (high - low), zero for a zero range. "
        "CMF = sum(multiplier * volume, 20) / sum(volume, 20), zero if no volume. "
        "Hold long above 0; otherwise cash.",
        "Close location can hide an overnight price drop. Zero-volume windows are "
        "neutral by app convention, not proof of no buying or selling.",
        f"{INDICATORS}/chaikin-money-flow-cmf",
    ),
    Pattern(
        "mfi",
        "Money Flow Index reversion (14; 20 / 80)",
        15,
        "Typical = (high + low + close) / 3. Assign typical * volume to positive/"
        "negative flow when typical rises/falls; equal typical contributes neither. "
        "Over 14 changes, MFI = 100 * positive / (positive + negative), neutral "
        "50 if both zero. Enter at <= 20; exit at >= 80; retain between.",
        "Volume-weighted weakness can persist. Zero or unreliable volume weakens this measure.",
        f"{INDICATORS}/money-flow-index-mfi",
    ),
    Pattern(
        "chaikin",
        "Chaikin flow momentum (3 / 10)",
        10,
        "ADL is the running sum of volume * (2 * close - high - low) / (high - low), "
        "with zero contribution for zero range. Oscillator = EMA3(ADL) - EMA10(ADL). "
        "Hold long above 0; otherwise cash.",
        "This is an indicator of a transformed volume line, not price itself. "
        "Bad volume or ignored overnight gaps can mislead.",
        f"{INDICATORS}/chaikin-oscillator",
    ),
    Pattern(
        "emv",
        "Ease-of-movement trend (14)",
        15,
        "Daily EMV = change in (high + low) / 2, multiplied by (high - low) "
        "* 100,000,000 / volume. This app assigns zero on zero-volume or "
        "zero-range days. Hold long when SMA14(EMV) > 0; otherwise cash.",
        "Low volume magnifies the score; easy movement is not safe movement. "
        "Zero-volume neutrality is an explicit app convention, not a valid measured ratio.",
        f"{INDICATORS}/ease-of-movement-emv",
    ),
    Pattern(
        "ultimate",
        "Ultimate Oscillator balance (7 / 14 / 28)",
        29,
        "BP = close - min(low, prior close); TR = max(high, prior close) - "
        "min(low, prior close). For 7/14/28 changes, R = sum(BP)/sum(TR), "
        "neutral 0.5 if TR sum is zero. UO = 100 * (4*R7 + 2*R14 + R28)/7. "
        "Hold long above 50; otherwise cash.",
        "A centerline teaching variant, not Williams' full divergence strategy. "
        "Three windows are not three independent confirmations.",
        f"{INDICATORS}/ultimate-oscillator",
    ),
    Pattern(
        "vortex",
        "Vortex directional crossover (14)",
        15,
        "+VM = abs(high - prior low); -VM = abs(low - prior high). "
        "Each VI = 14-change sum(VM) / sum(true range), zero for zero range sum. "
        "Hold long when +VI > -VI; otherwise cash.",
        "Repeated crossings can produce costly whipsaws. No intraday or short-selling rule.",
        f"{INDICATORS}/vortex-indicator",
    ),
    Pattern(
        "trix",
        "TRIX smoothed-price momentum (15)",
        44,
        "Apply three consecutive EMA15 smoothings to closes, each seeded from "
        "its first 15 available values. TRIX is the one-day percentage change "
        "of the third EMA. Hold long above 0; otherwise cash.",
        "Triple smoothing filters small moves but can react very late to a reversal.",
        f"{INDICATORS}/trix",
    ),
    Pattern(
        "force",
        "Force Index price-volume trend (13)",
        14,
        "Daily force = (close - prior close) * today's volume. Smooth 13 changes "
        "with an SMA-seeded EMA13. Hold long above 0; otherwise cash.",
        "Large price/volume outliers dominate. A zero-volume day contributes zero "
        "but does not instantly erase an earlier smoothed reading.",
        f"{INDICATORS}/force-index",
    ),
)


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
    if pattern.key not in {"sma", "ema", "rsi", "donchian", "bollinger", "macd", "engulfing"}:
        return study(candles, pattern.key).targets
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
