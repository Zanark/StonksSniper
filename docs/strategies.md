# Twenty more ideas to test

[App guide](guide.md) | [GIF tour](../README.md)

**27 usable rules: the original seven plus these 20.** Each new rule is in the
strategy picker, Explain pattern, Dictionary, See the rule chart and JSON export.
The app explains the idea, buy, sell, risk and numbers separately. These are
experiments with practice money, not recommendations or evidence of profitability.

## Read this first

- Every decision uses a finished daily candle. A position change fills at the
  **next available opening**, with fees and adverse slippage. No shorts.
- Warmup counts below mean completed observations before the first decision;
  one extra observation is needed for its first possible trade. Holidays do
  not count. A minimum seed is not proof that a smoothed value has settled.
- All rolling windows include today unless explicitly shifted. EMA seeds use a
  full simple average, then weight new values by `2 / (period + 1)`. Wilder
  averages use `1 / period`. These choices can differ from another platform.
- Keep owning between entry and exit boundaries only where stated. A buy
  condition does not buy another position every day.
- Volume-based ideas require meaningful reported volume. Zero-volume handling
  is an explicit numerical convention, not a way to repair a missing feed.
- ChartSchool pages linked below were read for formulas and interpretation on
  **2026-11-12**. They are educational references, not original-author publications,
  endorsements of this app or sources for our particular combined trading rules.
  Explanations here are original; no source performance claims were imported.

| # | New teaching variant | First decision after |
|---|---|---|
| 1 | Stochastic range reversion (14 / 3; 20 / 80) | 16 bars |
| 2 | Williams %R upper-half momentum (14) | 14 bars |
| 3 | CCI strength entry (20; 100 / 0) | 20 bars |
| 4 | Rate of change (12) | 13 bars |
| 5 | True Strength Index (25 / 13) | 38 bars |
| 6 | ADX with upward direction (14; 25) | 28 bars |
| 7 | Aroon recent-high filter (25; 70) | 26 bars |
| 8 | Ichimoku visible-cloud trend (9 / 26 / 52; shift 26) | 78 bars |
| 9 | Keltner breakout (EMA20; 2 ATR10) | 20 bars |
| 10 | Bollinger upper-band breakout (20; 2 population deviations) | 20 bars |
| 11 | Chandelier ratcheted exit (22; 3 ATR) | 22 bars |
| 12 | On-balance-volume versus EMA20 | 20 bars |
| 13 | Chaikin Money Flow (20) | 20 bars |
| 14 | Money Flow Index reversion (14; 20 / 80) | 15 bars |
| 15 | Chaikin Oscillator (3 / 10) | 10 bars |
| 16 | Ease of Movement (14) | 15 bars |
| 17 | Ultimate Oscillator midpoint (7 / 14 / 28) | 29 bars |
| 18 | Vortex directional crossover (14) | 15 bars |
| 19 | TRIX (15) | 44 bars |
| 20 | Force Index (13) | 14 bars |

## 1. Stochastic: try a bounce near the range floor

Imagine toy prices ranged from 90 to 110 tokens. A close of 92 is only 10% of
the way from bottom to top. Average three such range scores: buy at **20 or
below**, sell at **80 or above**, retain between. Low can remain low.

`%K = 100 * (close - lowest14) / (highest14 - lowest14)`;
`%D = SMA3(%K)`. Our score is %D, not a crossover. A zero-width range gives
neutral %K 50.
[Source: Stochastic](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochastic-oscillator-fast-slow-and-full).

## 2. Williams %R: follow the upper half

The same toy range with price 106 scores -20 on a scale from -100 to zero.
Buy **above -50**, sell **at -50 or below**. Unlike the bounce rule, this
follows strength. A falling stock can cross that midpoint repeatedly.

`%R = -100 * (highest14 - close) / (highest14 - lowest14)`.
Flat range gives -50. **This equals raw stochastic %K minus 100**: not a second
independent signal. Our smoothed stochastic rule has a different trade hypothesis.
[Source: Williams %R](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/williams-r).

## 3. CCI: follow an unusually strong move

Tomatoes usually cost close to 100. A price of 103 is unusual when their normal
gap is only 1. This rule buys CCI **above 100**, sells **at zero or below**,
and retains between. An unusual rise can still be about to reverse.

Typical price `TP = (high + low + close) / 3`.
`CCI = (TP - SMA20(TP)) / (0.015 * mean(abs(TP - that same mean), 20))`.
Zero deviation gives zero. CCI is not a percentage or business valuation.
[Source: CCI](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/commodity-channel-index-cci).

## 4. ROC: check whether price gained ground

A toy going from 100 to 106 over 12 shop visits gained 6%. Buy when that
12-change return is **positive**, sell when **zero or negative**. The earlier
comparison price changes daily too, which can create misleading flips.

`ROC = 100 * (close / close12ago - 1)`.
[Source: Rate of Change](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/rate-of-change-roc).

## 5. TSI: smooth the tug of war twice

Think of daily toy-budget gains and losses. If twice-smoothed signed change
is +2 and twice-smoothed movement size is 4, strength is +50. Buy **above zero**,
sell **at zero or below**. Smoothing can make a reversal arrive late.

`TSI = 100 * EMA13(EMA25(change)) / EMA13(EMA25(abs(change)))`.
Both first averages need 25 actual changes; both second averages need 13 seeded
values. Zero denominator gives zero.
[Source: TSI](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/true-strength-index).

## 6. ADX: demand upward direction and strength

A tug of war can be strongly won by either side. Buy only if **+DI > -DI and
ADX >= 25**; sell otherwise. High strength alone can describe a strong fall.

Compare positive expansion of highs with positive expansion of lows. Only the
larger positive component becomes directional movement; ties contribute neither.
Wilder-average 14 real changes and true ranges, then form +DI/-DI.
`DX = 100 * abs(+DI - -DI) / (+DI + -DI)`; Wilder-average 14 DX values for ADX.
Zero denominators give zero. This app's first value is at bar 28; the reference
warns that roughly 150 bars may be needed for settling.
[Source: ADX](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-directional-index-adx).

## 7. Aroon: ask which extreme happened recently

A shop's high two visits ago is fresher than its low 20 visits ago. Buy when
**Up > Down and Up >= 70**, sell otherwise. A tiny new high can still score 100.

Inspect today plus 25 prior observations: `Up = 100 * (25 - ageOfHigh) / 25`,
with the same formula for the low. Most recent tied extreme wins. This explicitly
uses 26 observations to allow ages zero through 25.
[Source: Aroon](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/aroon).

## 8. Ichimoku: check price above an older cloud

Use old toy-price notes to build a cloud, never tomorrow's unwritten page.
Buy if **close exceeds both visible cloud edges and conversion > base**;
sell if any test fails. A cloud shifted on a drawing is not a forecast.

Conversion/base are midpoints of the 9/26-day high-low ranges. Raw cloud A is
their average; raw B is the 52-day range midpoint. The visible edges at observation
`i` are raw A/B from **i - 26**. No backward-drawn lagging-span test is used;
no signal is backdated. First complete visible cloud: bar 78.
[Source: Ichimoku](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/ichimoku-cloud).

## 9. Keltner: follow a jump beyond normal swings

If a stall's usual-price line is 100 and its typical movement is 3, the upper
channel is 106. Buy **above the upper channel**, sell **at the middle or below**,
retain between. Tomorrow's opening can reverse or gap far past the line.

Middle `= EMA20(close)`; upper `= middle + 2 * Wilder ATR10`.
True range is the largest of high-low and the absolute distances from prior close
to today's high/low. First TR is high-low; the ATR seeds with ten complete ranges.
[Source: Keltner](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/keltner-channels)
and [ATR seed](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-true-range-atr).

## 10. Bollinger breakout: follow upper-band strength

If average toy price is 100 and its population spread is 4, the upper band is
108. Buy **above 108**, sell **at the moving average or below**, retain between.
This tests the opposite premise to the original lower-band reversion rule.

Upper `= SMA20(close) + 2 * populationStandardDeviation20(close)`.
No squeeze, chart-shape confirmation or normal-distribution guarantee is implied.
[Source: Bollinger Bands](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/bollinger-bands).

## 11. Chandelier: raise an exit floor while owning

Highest toy price 120 minus three normal swings of 4 gives a candidate floor
108. Buy from cash when **close > SMA22 and close > candidate**. While owning,
raise the floor when its candidate rises; never lower it. Sell when **close is
at the active floor or below**. Reset after exit, without same-close re-entry.

Candidate `= highestHigh22 - 3 * Wilder ATR22`. **The reference's rolling line
can fall. The ratchet and SMA entry are app-specific additions.** This is a
finished-close decision followed by next-open execution, not an intraday stop:
a floor of 112 does not guarantee a sale for 112.
[Source: Chandelier Exit](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/chandelier-exit).

## 12. OBV: check whether busy days lean upward

Add 1,000 marbles for an up-price day with volume 1,000; remove 400 for a
down-price day with volume 400. Buy if that balance **exceeds EMA20 of itself**;
sell otherwise. One busy day can dominate, regardless of the size of its price change.

OBV starts at zero; an unchanged close contributes zero. It is not money
entering a company's bank account.
[Source: OBV](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/on-balance-volume-obv).

## 13. CMF: check where busy days finish

A tomato stall closes at 105 inside a 90-to-110 daily range: location +0.5.
Weight such locations by volume over 20 days. Buy CMF **above zero**, sell
**at zero or below**. Yesterday's close could still have been 120.

Multiplier `= (2*close - high - low) / (high - low)`.
`CMF = sum20(multiplier * volume) / sum20(volume)`.
Zero-range days contribute zero; no-volume windows score zero by convention.
[Source: CMF](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-money-flow-cmf).

## 14. MFI: try a volume-backed bounce

Keep two toy-shop jars for rising-price and falling-price weighted activity.
Positive flow 1,000 versus negative 9,000 gives score 10. Buy at **20 or below**,
sell at **80 or above**, retain between. Busy selling does not guarantee a rebound.

Assign `TP * volume` to the positive or negative jar according to the change in
typical price; ties contribute neither. For 14 actual changes,
`MFI = 100 * positive / (positive + negative)`. Both zero gives 50: neutral,
which retains an existing position, not an automatic sale.
[Source: MFI](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/money-flow-index-mfi).

## 15. Chaikin Oscillator: watch pressure speed up

Compare a faster and slower average of the toy shop's running pressure balance.
Buy if **EMA3(ADL) > EMA10(ADL)**; sell otherwise. Improving pressure can coexist
with falling prices.

ADL is the running sum of CMF's daily multiplier times volume, starting from
the first contribution. Oscillator `= EMA3(ADL) - EMA10(ADL)`.
Zero-range days contribute zero. This is not CMF's rolling volume ratio.
[Source: Chaikin Oscillator](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-oscillator).

## 16. Ease of Movement: check whether price moves easily upward

A toy-price midpoint rising by 2 with range 4 and volume 100 million produces
daily score 8. Buy if its **14-change mean > 0**; sell otherwise. A quiet
shop can be easy to move and hard to sell into.

`EMV = change((high+low)/2) * (high-low) * 100000000 / volume`.
**App convention:** zero-volume or zero-range days contribute zero. Undefined
zero-volume division is not treated as a measured value from the source formula.
[Source: EMV](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ease-of-movement-emv).

## 17. Ultimate Oscillator: blend three pressure windows

Mix short, medium and longer notebook sections, weighting the shortest most.
Buy **above 50**, sell **at 50 or below**. Overlapping pages do not provide three
independent confirmations.

`BP = close - min(low, priorClose)`; `TR = max(high, priorClose) - min(low, priorClose)`.
For each 7/14/28-change window take `R = sum(BP)/sum(TR)`, using neutral 0.5 if
the denominator is zero. `UO = 100 * (4*R7 + 2*R14 + R28)/7`.
**This is a midpoint teaching variant, not the original divergence system.**
[Source: Ultimate Oscillator](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ultimate-oscillator).

## 18. Vortex: compare upward and downward reach

Draw arrows between yesterday's low and today's high, and yesterday's high
and today's low. Buy if **+VI > -VI**, sell on a tie or when -VI wins.
Repeated line crossings can make fees expensive.

`+VM = abs(high - priorLow)`; `-VM = abs(low - priorHigh)`.
Divide each 14-change sum by the same true-range sum. Zero denominator gives
both zero. No shorts or intraday confirmation.
[Source: Vortex](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/vortex-indicator).

## 19. TRIX: follow a heavily smoothed price

Smooth a bumpy toy-price drawing three times, then compare today with yesterday.
A final line rising from 100 to 100.2 changes +0.2%. Buy **positive change**,
sell **zero or negative change**. Smooth does not mean timely or profitable.

Apply EMA15 three times, then take the third line's one-day percentage change.
Each stage requires a complete seed: first third-stage value at bar 43,
first change at bar 44.
[Source: TRIX](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/trix).

## 20. Force Index: measure price change with volume

A toy price rising by 2 with volume 1,000 produces force +2,000. Falling by
1 with volume 500 gives -500. Buy when **EMA13(force) > 0**; sell otherwise.
One exceptional day can dominate.

`force = (close - priorClose) * volume`. Unlike OBV it weights the size,
not just the sign, of price movement. A zero-volume contribution does not
instantly erase a previously positive or negative smoothed reading.
[Source: Force Index](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/force-index).

## What this expansion does not establish

These are 20 additional trading variants, not 20 unrelated mathematical signals.
Williams/Stochastic, both Bollinger uses, and the Chaikin volume family overlap.
No profitability ranking, optimized settings, divergence recognition, guaranteed
stop fills or point-in-time market-data qualification is claimed. Different
warmups start experiments and benchmarks on different days; compare those
boundaries before comparing outcomes.

The original seven remain unchanged. Broader catalogue research, SAR, VWAP,
confirmed chart structures, statistical pairs and multi-timeframe ideas remain
in [SS-06](../TODO/06_PATTERN_CATALOGUE.todo); baskets and AI remain planned.
