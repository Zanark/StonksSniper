# All 27 strategies, explained

[App guide](guide.md) | [GIF tour](../README.md) | [Roadmap](../TODO/06_PATTERN_CATALOGUE.todo)

This is the complete reference for **every strategy currently implemented**:
the original seven and the 20 later additions. Each entry explains the idea in
plain English, the actual buy/sell/hold rules, calculations, minimum history,
an illustrative example, limitations and an educational source.

These are fixed-parameter, daily **long-or-cash teaching variants**, not
recommendations, profitability claims or every possible interpretation of an
indicator. The examples below use **made-up toy-shop numbers**, not market
observations, backtest results or forecasts.

## What buy, sell and hold mean here

Every strategy starts wanting **cash**, with no stock owned.

- **Buy:** switch the desired position from cash to owning the stock. A rule
  still saying buy tomorrow does not buy a second position.
- **Sell:** switch from owning to cash. If already in cash, remain there.
  Selling never opens a short position.
- **Retain:** leave the previous desired position unchanged. Between two
  thresholds, a rule can therefore retain **cash**, not necessarily stock.
- **Warmup:** collect enough completed observations to calculate a decision.
  Before that, the target is unavailable, not a secretly assumed buy.

A condition need not cross a line today: being above it on the **first eligible
close** can already request ownership. Entry/exit wording below describes the
desired position, not an order sent to a broker.

### A decision is not its execution price

All decisions use a **finished daily candle**. A change fills at the **next
available session's opening**, never the same close. For example, a Monday
buy decision with a Tuesday opening of 102 buys from that opening, not Monday's
close or an indicator value. A holiday simply delays the next available session.

The simulator invests all available practice cash, allowing fractional research
units. It applies adverse slippage and fees on both buys and sells:

```text
fee rate = fee_bps / 10,000
slippage rate = slippage_bps / 10,000
buy price = next opening * (1 + slippage rate)
bought units = cash / (buy price * (1 + fee rate))
sell price = next opening * (1 - slippage rate)
sale cash = units * sell price * (1 - fee rate)
```

One basis point is 0.01%. Defaults are 10 basis points of fees and 10 of slippage
per side; use the experiment's actual chosen settings. No strategy has an
intraday stop, guaranteed exit price, extra position-sizing formula or
profit-taking rule unless explicitly described below. An open final holding is
valued at the final close, **not automatically sold**; a final-close signal has
no execution without another opening.

The history is adjusted research data, not literal historical share purchases.
Each rule runs separately, not as one shared-cash portfolio. The buy-once
benchmark enters at the first possible opening after that rule's warmup, with
the same entry costs. Different warmups can therefore mean different comparison
start dates.

## Reading the numbers

`O`, `H`, `L`, `C` and `V` mean opening, highest, lowest, closing price and
reported volume. A **bar** is one completed observed trading session, not a
calendar day. All rules need the next session's opening for execution; the table
lists only inputs needed to calculate their signals.

`SMA_n(x)` is the average of the latest `n` values. Unless explicitly shifted,
rolling windows include today's finished observation. `EMA_n(x)` gives recent
values more weight: seed it with the first complete `n`-value simple average,
then update `old + 2/(n+1) * (new - old)`. Wilder smoothing instead uses `1/n`.
Nested averages each need their **own complete seed**; they do not start from
the first single observation.

`sigma_n` means population standard deviation: subtract the window mean from
each value, square the gaps, average those squares, then take the square root.
It measures historical spread, not a guaranteed price range.

**True range** is `max(H, prior C) - min(L, prior C)`, which includes overnight
gaps. For ATR-based rules, the first available bar contributes `H-L`;
`ATR_n` is its Wilder-smoothed average. ADX instead seeds from 14 actual
between-session changes, as its entry explains.

Numbers below are **minimum seeds**, not proof that a smoothed indicator has
settled. The app needs at least **warmup + 1 bars** to run a simulation with
a possible opening execution; that does not guarantee any trade will occur.
Zero-volume conventions are mathematical choices, not repairs for a missing
or unreliable data feed.

## Complete catalogue

Links jump to the full explanation. Keys are the stable identifiers used in
the source and export.

| # | Strategy | Key | First decision after | Signal inputs |
|---|---|---|---|---|
| 1 | [SMA trend (10 / 30)](#sma) | `sma` | 30 bars | C |
| 2 | [EMA trend (12 / 26)](#ema) | `ema` | 26 bars | C |
| 3 | [RSI reversion (14; 30 / 70)](#rsi) | `rsi` | 15 bars | C |
| 4 | [Donchian breakout (20)](#donchian) | `donchian` | 21 bars | H, L, C |
| 5 | [Bollinger reversion (20; 2 sigma)](#bollinger) | `bollinger` | 20 bars | C |
| 6 | [MACD signal trend (12 / 26 / 9)](#macd) | `macd` | 34 bars | C |
| 7 | [Body engulfing reversal](#engulfing) | `engulfing` | 2 bars | O, C |
| 8 | [Stochastic range reversion (14 / 3; 20 / 80)](#stochastic) | `stochastic` | 16 bars | H, L, C |
| 9 | [Williams %R range momentum (14; -50)](#williams) | `williams` | 14 bars | H, L, C |
| 10 | [CCI strength entry (20; 100 / 0)](#cci) | `cci` | 20 bars | H, L, C |
| 11 | [Rate-of-change momentum (12)](#roc) | `roc` | 13 bars | C |
| 12 | [True Strength Index trend (25 / 13)](#tsi) | `tsi` | 38 bars | C |
| 13 | [ADX directional-strength filter (14; 25)](#adx) | `adx` | 28 bars | H, L, C |
| 14 | [Aroon recent-high trend (25; 70)](#aroon) | `aroon` | 26 bars | H, L |
| 15 | [Ichimoku visible-cloud trend (9 / 26 / 52)](#ichimoku) | `ichimoku` | 78 bars | H, L, C |
| 16 | [Keltner channel breakout (20 / 10; 2 ATR)](#keltner) | `keltner` | 20 bars | H, L, C |
| 17 | [Bollinger strength breakout (20; 2 sigma)](#bollinger-breakout) | `bollinger-breakout` | 20 bars | C |
| 18 | [Chandelier ratcheted exit (22; 3 ATR)](#chandelier) | `chandelier` | 22 bars | H, L, C |
| 19 | [On-balance-volume trend (20)](#obv) | `obv` | 20 bars | C, V |
| 20 | [Chaikin Money Flow pressure (20)](#cmf) | `cmf` | 20 bars | H, L, C, V |
| 21 | [Money Flow Index reversion (14; 20 / 80)](#mfi) | `mfi` | 15 bars | H, L, C, V |
| 22 | [Chaikin flow momentum (3 / 10)](#chaikin) | `chaikin` | 10 bars | H, L, C, V |
| 23 | [Ease-of-movement trend (14)](#emv) | `emv` | 15 bars | H, L, V |
| 24 | [Ultimate Oscillator balance (7 / 14 / 28)](#ultimate) | `ultimate` | 29 bars | H, L, C |
| 25 | [Vortex directional crossover (14)](#vortex) | `vortex` | 15 bars | H, L, C |
| 26 | [TRIX smoothed-price momentum (15)](#trix) | `trix` | 44 bars | C |
| 27 | [Force Index price-volume trend (13)](#force) | `force` | 14 bars | C, V |

## The original seven

<a id="sma"></a>
### 1. SMA: follow the recent trend

**ELI15:** Compare the average price of a toy over 10 shop visits with its
30-visit average. If the short average is higher, recent prices have been
stronger. An average is a smoother notebook line, not tomorrow's price.

**Exact rules:** Buy/keep owning when `SMA10(C) > SMA30(C)`. Sell/stay in cash
when `SMA10(C) <= SMA30(C)`, including equality. There is no separate neutral
band and no requirement to witness a fresh crossover.

**Calculation and warmup:** Compute both ordinary averages including the
latest close. First decision after **30 bars**; earliest possible fill is
opening 31.

**Walkthrough:** Short average 110, long average 100 requests a buy next opening.
Later, 102 versus 100 retains ownership; 100 versus 100 requests a sale.
If the next opening is 103, the trade uses that opening plus costs, not 100.

**What can fail:** A flat, choppy market can repeatedly flip the comparison,
charging costs each time. The averages lag reversals. These exact periods
are a teaching variant, not universally best settings.

[Source: simple and exponential moving averages](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/moving-averages-simple-and-exponential).

<a id="ema"></a>
### 2. EMA: follow a more responsive trend

**ELI15:** Use two toy-price averages, but give recent shop visits more weight.
The shorter average reacts faster; faster is not the same as more accurate.

**Exact rules:** Buy/keep owning when `EMA12(C) > EMA26(C)`.
Sell/stay in cash when `EMA12(C) <= EMA26(C)`. Equality means cash.

**Calculation and warmup:** Use the complete-window EMA seeds and update
formula above, separately for 12 and 26 closes. First decision after **26 bars**;
the first possible fill is opening 27.

**Walkthrough:** Fast EMA 105 versus slow EMA 100 requests a buy. Fast 101
versus slow 100 retains ownership; fast 99 versus slow 100 requests a sale.
No trade executes at either EMA value.

**What can fail:** Extra responsiveness can produce more short-lived changes.
The rule still reacts to old prices, and another platform's initial seed can
produce different early signals. Minimum history is not fully settled history.

[Source: simple and exponential moving averages](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/moving-averages-simple-and-exponential).

<a id="rsi"></a>
### 3. RSI: try a bounce after weakness

**ELI15:** Keep separate notebooks of toy-price rises and falls. RSI compares
their smoothed sizes on a 0-to-100 scale. A low score says prices have been weak,
not that the toy is cheap or certain to rebound.

**Exact rules:** Buy at `RSI14 <= 30`; sell at `RSI14 >= 70`;
**retain cash or ownership** strictly between 30 and 70.

**Calculation and warmup:** For each close change, gain is `max(change, 0)`
and loss is `max(-change, 0)`. Seed their averages from 14 changes and update
with Wilder smoothing. `RSI = 100 - 100/(1 + averageGain/averageLoss)`.
Both averages zero gives 50; zero loss with positive gain gives 100.
First decision after **15 closes**, because 14 changes need 15 prices.

**Walkthrough:** RSI 28 requests a buy; 45 retains the existing position;
70 requests a sale. Starting in cash with RSI 45 does **not** buy.
A flat score of 50 also retains the previous target.

**What can fail:** Weakness can continue for a long time. A score of 28 is not
a 28% probability of rising, and these thresholds do not estimate fair value.

[Source: RSI](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/relative-strength-index-rsi).

<a id="donchian"></a>
### 4. Donchian: follow an escape from the old range

**ELI15:** Draw a box around the highest and lowest toy prices from the
previous 20 visits. A close above that old ceiling tests upward strength.

**Exact rules:** Buy when today's close is **strictly above** the highest
high of the preceding 20 bars. Sell when it is **strictly below** their lowest
low. Otherwise retain cash or ownership, including equality with either line.

**Calculation and warmup:** `upper = max(H[i-20:i])`;
`lower = min(L[i-20:i])`, using slice notation with the end excluded.
**Today's candle is excluded** from both boundaries. First decision after
**21 bars**: 20 prior observations plus today's close.

**Walkthrough:** Old upper 120 and lower 90, today's close 121: request a buy.
On a later day with newly calculated boundaries 125 and 95, close 95 retains
ownership, while close 94 requests a sale. The boundaries move every day.

**What can fail:** An apparent escape can reverse before the next opening.
Using today's high in its own breakout ceiling would change this rule.
There is no short entry or guaranteed intraday channel-stop fill.

[Source: price channels](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/price-channels).

<a id="bollinger"></a>
### 5. Bollinger reversion: try a return toward average

**ELI15:** Find the toy's usual recent price and how spread out those prices
have been. Buy an unusually low close, hoping for a return toward the average.
The band is a measurement, not a protective floor.

**Exact rules:** Buy when `C < lower`; sell when `C >= middle`.
Retain the previous target otherwise. Equality with the **lower** band does
not start a buy; equality with the **middle** does sell.

**Calculation and warmup:** `middle = SMA20(C)`;
`lower = middle - 2 * sigma20(C)`. Use population, not sample, deviation
of those same 20 closes, including today. First decision after **20 bars**.

**Walkthrough:** Mean 100 and deviation 5 make the lower band 90.
Close 89 requests a buy; 95 retains ownership; reaching that day's updated
mean requests a sale. Initially in cash at exactly 90 does not enter.

**What can fail:** A falling price can remain below its band and lose much
more. The mean moves too. This is the opposite entry premise to
[Bollinger strength breakout](#bollinger-breakout), not an extra confirmation.

[Source: Bollinger Bands](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/bollinger-bands).

<a id="macd"></a>
### 6. MACD: compare momentum with its own recent average

**ELI15:** Measure the gap between a faster and slower toy-price average,
then smooth that gap. The question is whether the gap is above its recent
average, not simply whether the toy's price rose today.

**Exact rules:** Buy/keep owning when `MACD > signal`;
sell/stay in cash when `MACD <= signal`. Equality means cash.
MACD does **not** need to be above zero.

**Calculation and warmup:** `MACD = EMA12(C) - EMA26(C)`;
`signal = EMA9(available MACD values)`. Every stage uses a complete simple-average
seed. First MACD value at bar 26; nine values produce the first decision at
**bar 34**, with earliest fill at opening 35.

**Walkthrough:** EMAs 108 and 100 give MACD 8. Signal 6 requests a buy.
Later MACD 4 versus signal 5 requests a sale. MACD -1 versus signal -2 would
also request ownership: the comparison, not the sign alone, controls this variant.

**What can fail:** Both lines lag price changes. Choppy crossings can cause
repeated costs, and alternative EMA seeds can change early results.
No divergence detector or additional histogram rule is implemented.

[Source: MACD](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/macd-moving-average-convergence-divergence-oscillator).

<a id="engulfing"></a>
### 7. Body engulfing: test a two-candle reversal shape

**ELI15:** Each daily toy-price card has an opening and closing price.
Its thick candle body joins them. This rule asks whether today's body covers
yesterday's body while changing direction; thin high/low wicks do not count.

**Exact rules:** Buy if yesterday fell (`prior C < prior O`), today rose
(`C > O`), `O <= prior C`, and `C >= prior O`. Sell for the mirror:
yesterday rose, today fell, `O >= prior C`, and `C <= prior O`.
Otherwise retain cash or ownership. Matching body edges are allowed;
equal-open/close bodies, called doji, are excluded.

**Calculation and warmup:** Compare two consecutive bodies only.
First decision after **2 bars**, earliest fill at opening 3.
There is no moving average, wick test, trend filter or volume confirmation.

**Walkthrough:** Yesterday opened 110 and closed 100; today opens 99 and
closes 111. Today's rising body contains the old falling body: request a buy.
For a sell example, an up body from 110 to 120 followed by a down body from
121 to 109 requests an exit. A nonmatching pair makes no change.

**What can fail:** Two shapes do not prove a reversal. With no opposite pattern,
the rule can hold indefinitely. Tiny revisions to adjusted prices can flip exact
boundary comparisons; export the observations to preserve the experiment.

[Source: candlestick pattern dictionary](https://chartschool.stockcharts.com/table-of-contents/chart-analysis/candlestick-charts/candlestick-pattern-dictionary).

## The 20 later additions

<a id="stochastic"></a>
### 8. Stochastic: try a bounce near the range floor

**ELI15:** Ask where a toy's close sits between its recent lowest and highest
prices, then average three range scores to reduce jumping.

**Exact rules:** Buy at `%D <= 20`; sell at `%D >= 80`; retain between.
This tests smoothed thresholds, **not a %K/%D crossover**.

**Calculation and warmup:** `%K = 100 * (C - lowest14) / (highest14 - lowest14)`;
`%D = SMA3(%K)`. Highest/lowest use H/L including today. Zero-width range gives
neutral %K 50. First decision after **16 bars**.

**Walkthrough:** A 90-to-110 range with close 92 gives %K 10.
Three available scores 10, 20 and 30 give %D 20: buy next opening.
Then 50 retains the position and 80 requests a sale.

**What can fail:** Low can stay low in a downtrend. Neither the score nor its
smoothing establishes a bargain or a reversal.

[Source: Stochastic](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochastic-oscillator-fast-slow-and-full).

<a id="williams"></a>
### 9. Williams %R: follow the upper half

**ELI15:** Measure how near the toy's final price is to its recent high.
Unlike the bounce rule, this variant prefers upper-half strength.

**Exact rules:** Buy/keep owning above -50; sell/stay in cash at -50 or below.

**Calculation and warmup:** `%R = -100 * (highest14 - C) / (highest14 - lowest14)`,
including today. Flat range gives -50, which requests cash here.
First decision after **14 bars**.

**Walkthrough:** In a 90-to-110 range, close 106 scores -20 and requests a buy.
Close 100 scores -50 and requests a sale. The scale runs from -100 to zero;
the minus sign is not a loss on the practice account.

**What can fail:** A falling stock can repeatedly cross its midpoint.
This equals **raw stochastic %K minus 100**, not independent evidence.
Our stochastic variant uses smoothing and a different reversion hypothesis.

[Source: Williams %R](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/williams-r).

<a id="cci"></a>
### 10. CCI: follow an unusually strong move

**ELI15:** Tomatoes at 103 are unusual if their recent typical price is 100
and their average distance from that mean is only 1.

**Exact rules:** Buy above 100; sell at zero or below; retain between.
At exactly 100, a cash position remains cash and an existing holding remains owned.

**Calculation and warmup:** `TP = (H + L + C)/3`;
`mean = SMA20(TP)`; `MAD = mean(abs(each TP - that same window mean))`;
`CCI = (TP - mean)/(0.015 * MAD)`. Zero deviation gives zero.
First decision after **20 bars**.

**Walkthrough:** TP 103, mean 100, MAD 1 give CCI 200: request a buy.
CCI 50 retains ownership; zero requests a sale.

**What can fail:** Unusual strength can be the final burst before a fall.
CCI is not a percentage, fair-value estimate or probability.

[Source: CCI](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/commodity-channel-index-cci).

<a id="roc"></a>
### 11. ROC: check whether price gained ground

**ELI15:** Compare a toy's price now with its price 12 shop visits earlier.

**Exact rules:** Buy/keep owning if ROC is positive;
sell/stay in cash at zero or below.

**Calculation and warmup:** `ROC = 100 * (C / C_12_sessions_ago - 1)`.
First decision after **13 closes**: 12 changes need 13 observations.

**Walkthrough:** From 100 to 106 is +6%, requesting a buy.
From 100 to 99 is -1%, requesting a sale; unchanged at 100 also requests cash.

**What can fail:** The old comparison price changes every day too.
A signal can flip because an old extreme leaves the comparison, without major
new movement. This return is historical, not a forecast.

[Source: rate of change](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/rate-of-change-roc).

<a id="tsi"></a>
### 12. TSI: smooth the tug of war twice

**ELI15:** Smooth daily toy-price gains and losses twice. Compare their net
direction with the overall size of those movements.

**Exact rules:** Buy/keep owning above zero; sell/stay in cash at zero or below.

**Calculation and warmup:** `change = C - prior C`;
`TSI = 100 * EMA13(EMA25(change)) / EMA13(EMA25(abs(change)))`.
Both first averages need 25 actual changes; both second averages need 13 seeded
values. Zero denominator gives zero. First decision after **38 bars**.

**Walkthrough:** Twice-smoothed signed change +2 and movement size 4 give
TSI +50: request a buy. Signed change -1 with size 4 gives -25: request a sale.

**What can fail:** Double smoothing delays reversals. The minimum seed is
not fully settled history, and a smooth line is not necessarily a good signal.

[Source: TSI](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/true-strength-index).

<a id="adx"></a>
### 13. ADX: demand upward direction and strength

**ELI15:** A tug of war can be strongly won by either side.
Check both the winning direction and the strength of the contest.

**Exact rules:** Buy/keep owning only when `+DI > -DI` **and** `ADX >= 25`.
Sell/stay in cash if either test fails. A directional tie requests cash.

**Calculation and warmup:** `up = H - prior H`; `down = prior L - L`.
Only the larger positive expansion becomes +DM or -DM; ties give both zero.
Wilder-average 14 actual changes of DM and true range:
`+DI = 100 * smoothed(+DM)/smoothed(TR)`, with the mirror for -DI.
`DX = 100 * abs(+DI - -DI)/(+DI + -DI)`; Wilder-average 14 DX values for ADX.
Zero denominators give zero. First decision after **28 bars**.

**Walkthrough:** +DI 30, -DI 12 and ADX 28 request a buy.
Reversing the directional scores requests a sale even if ADX is 40.
Keeping the upward lead but dropping strength to 24 also requests a sale.

**What can fail:** High ADX alone can describe a strong fall.
The reference warns roughly 150 bars may be needed for settling; the first
seeded decision is not equally mature.

[Source: ADX](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-directional-index-adx).

<a id="aroon"></a>
### 14. Aroon: ask which extreme happened recently

**ELI15:** A shop's high two visits ago is fresher than its low 20 visits ago.
Recency, not the size of the move, drives this score.

**Exact rules:** Buy/keep owning when `Up > Down` and `Up >= 70`;
sell/stay in cash otherwise.

**Calculation and warmup:** Inspect today plus 25 prior observations:
`Up = 100 * (25 - ageOfHigh)/25`, with the same formula for the low and Down.
The most recent tied extreme wins. Ages can be zero through 25, so the first
decision needs **26 bars**, not 25.

**Walkthrough:** High two sessions ago gives Up 92; low 20 ago gives Down 20:
request a buy. Up and Down both 100 request cash because Up is not greater.

**What can fail:** A tiny new high can still score 100. A large score does
not establish a powerful price move or independent confirmation of other trends.

[Source: Aroon](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/aroon).

<a id="ichimoku"></a>
### 15. Ichimoku: check price above an older cloud

**ELI15:** Use old toy-price notes to draw a cloud under today's price.
Moving a drawing forward does not reveal tomorrow's unwritten notebook page.

**Exact rules:** Buy/keep owning only if the close exceeds **both visible cloud
edges** and conversion exceeds base. Sell/stay in cash if any test fails,
including equality.

**Calculation and warmup:** Conversion/base are midpoints of the 9/26-bar
high-low ranges. Raw cloud A is their average; raw B is the 52-bar range
midpoint. The visible edges at observation `i` are raw A/B from **i - 26**.
No backward-drawn lagging-span test or backdated signal is used.
First complete decision after **78 bars**.

**Walkthrough:** Visible cloud 95 and 100, close 105, conversion 104 and base
102 request a buy. Close 100 fails the strict cloud test and requests cash;
conversion tying base also fails even if price remains above the cloud.

**What can fail:** This is a lagging, simplified cloud-trend variant,
not a forecast or every Ichimoku trading interpretation.

[Source: Ichimoku](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/ichimoku-cloud).

<a id="keltner"></a>
### 16. Keltner: follow a jump beyond normal swings

**ELI15:** Put a channel above the toy's smoothed price, allowing extra room
when normal daily movement, including gaps, becomes larger.

**Exact rules:** Buy when `C > upper`; sell when `C <= middle`;
retain cash or ownership between. Equality with upper does not start a buy.

**Calculation and warmup:** `middle = EMA20(C)`;
`upper = middle + 2 * Wilder ATR10`. First TR is H-L; ATR seeds with ten
complete ranges. First decision after **20 bars**.

**Walkthrough:** Middle 100 and ATR 3 give upper 106. Close 107 requests a buy;
104 retains an existing holding; 100 requests a sale.

**What can fail:** A jump can reverse before the next opening.
The channel is not a guaranteed fill price, and wider movement does not identify
direction by itself.

[Source: Keltner](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/keltner-channels)
and [ATR initialization](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-true-range-atr).

<a id="bollinger-breakout"></a>
### 17. Bollinger breakout: follow upper-band strength

**ELI15:** Instead of buying an unusually low toy price, try following a close
unusually far **above** its recent average.

**Exact rules:** Buy when `C > upper`; sell when `C <= middle`;
retain otherwise. Tying the upper band does not enter from cash.

**Calculation and warmup:** `middle = SMA20(C)`;
`upper = middle + 2 * sigma20(C)`, using population deviation of the same
20 closes. First decision after **20 bars**.

**Walkthrough:** Mean 100 and spread 4 give upper 108.
Close 109 requests a buy; 104 retains ownership; 100 requests a sale.

**What can fail:** A brief surge can immediately reverse. This is the opposite
entry premise to [lower-band reversion](#bollinger), not a vote from a different
source of information. No squeeze, W-bottom, divergence or normal-distribution
guarantee is implied.

[Source: Bollinger Bands](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/bollinger-bands).

<a id="chandelier"></a>
### 18. Chandelier: raise an exit floor while owning

**ELI15:** Hang a floor below the toy's recent high. Once owning, the floor
can rise but cannot be lowered to excuse a falling price.

**Exact rules:** From cash, buy only if `C > SMA22(C)` and `C > candidate`.
On entry set the active floor to candidate. While owning, first update
`floor = max(previous floor, candidate)`; sell if `C <= floor`, otherwise retain.
Reset after exit; there is no same-close re-entry or active floor while in cash.

**Calculation and warmup:** `candidate = highestHigh22 - 3 * Wilder ATR22`.
First TR is H-L. First decision after **22 bars**.
The reference's rolling line can fall; **the ratchet and SMA entry are app-specific
additions**, not the source's universal system.

**Walkthrough:** High 120 and ATR 4 give candidate 108. SMA 105 and close 110
request a buy. Candidate later 112 raises the floor to 112. A subsequent
candidate of 111 cannot lower it; close 111 requests a sale against floor 112.

**What can fail:** This is a close-confirmed, next-opening sale, **not an
intraday stop**. A floor of 112 does not guarantee a sale for 112; overnight
gaps can make the actual exit much worse.

[Source: Chandelier Exit](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/chandelier-exit).

<a id="obv"></a>
### 19. OBV: check whether busy days lean upward

**ELI15:** Add marbles for an up-price day's activity and remove them for
a down-price day's activity. Compare the running balance with its recent average.

**Exact rules:** Buy/keep owning if `OBV > EMA20(OBV)`;
sell/stay in cash otherwise, including equality.

**Calculation and warmup:** Start OBV at zero. Add today's volume on a higher
close, subtract it on a lower close, add zero on an unchanged close.
The first bar has no prior close and contributes zero.
First decision after **20 bars**.

**Walkthrough:** An up day with volume 1,000 adds 1,000; a down day with volume
400 subtracts 400. If the resulting OBV is 600 and its seeded EMA is 500,
request a buy. OBV equal to its EMA requests cash.

**What can fail:** One unusually busy day can dominate, regardless of the
price move's size. OBV is not money entering a company's bank account.
Reported volume quality matters.

[Source: OBV](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/on-balance-volume-obv).

<a id="cmf"></a>
### 20. CMF: check where busy days finish

**ELI15:** Give more importance to busy shop visits. Ask whether their
closing prices tend to sit near the top or bottom of each day's own range.

**Exact rules:** Buy/keep owning above zero; sell/stay in cash at zero or below.

**Calculation and warmup:** `multiplier = (2*C - H - L)/(H-L)`;
`CMF = sum20(multiplier * V)/sum20(V)`. Zero-range bars contribute zero;
a no-volume window scores zero by app convention, requesting cash here.
First decision after **20 bars**.

**Walkthrough:** Close 105 inside a 90-to-110 range gives multiplier +0.5.
If the full window's volume-weighted score is +0.5, request a buy.
A later window score of zero or -0.2 requests a sale.

**What can fail:** Yesterday's close could have been 120: a high finish inside
today's range can coexist with a major overnight loss.
Zero-volume neutrality is not proof of no buying or selling.

[Source: CMF](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-money-flow-cmf).

<a id="mfi"></a>
### 21. MFI: try a volume-backed bounce

**ELI15:** Keep two toy-shop jars for rising-price and falling-price activity.
This reversion rule buys when the rising jar has become relatively small.

**Exact rules:** Buy at `MFI <= 20`; sell at `MFI >= 80`; retain between.

**Calculation and warmup:** `TP = (H + L + C)/3`.
Assign `TP * V` to positive or negative flow according to the change in TP;
ties contribute neither. Over 14 actual changes,
`MFI = 100 * positive/(positive + negative)`.
Both zero gives neutral 50, which retains the previous target.
First decision after **15 bars**.

**Walkthrough:** Positive flow 1,000 and negative 9,000 give MFI 10: buy.
At 50 keep the previous target; at 80 sell.
Starting in cash at neutral 50 does not enter.

**What can fail:** Busy selling does not guarantee a rebound.
Zero or unreliable volume weakens this measure, and TP times volume is
a constructed indicator quantity, not verified cash moving into the business.

[Source: MFI](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/money-flow-index-mfi).

<a id="chaikin"></a>
### 22. Chaikin Oscillator: watch pressure speed up

**ELI15:** Keep a running activity balance based on where each day's price
finishes. Compare a fast and slow average of that balance.

**Exact rules:** Buy/keep owning when `EMA3(ADL) > EMA10(ADL)`;
sell/stay in cash on equality or when the fast average is lower.

**Calculation and warmup:** Use CMF's daily multiplier above.
`ADL = cumulative sum(multiplier * V)`, starting with the first contribution;
`oscillator = EMA3(ADL) - EMA10(ADL)`. Zero-range bars contribute zero.
First decision after **10 bars**.

**Walkthrough:** Fast balance average 1,200 and slow 1,000 give oscillator
+200: buy. Fast 900 and slow 1,000 give -100: sell.

**What can fail:** Improving pressure can coexist with falling prices.
This is a smoothed difference of a cumulative transformed volume line,
**not** CMF's rolling volume ratio. Overnight gaps and bad volume can mislead.

[Source: Chaikin Oscillator](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-oscillator).

<a id="emv"></a>
### 23. Ease of Movement: check whether price moves easily upward

**ELI15:** Ask how much the toy's daily price range moved compared with the
activity needed to move it. Quiet movement is not necessarily safe movement.

**Exact rules:** Buy/keep owning if `SMA14(daily EMV) > 0`;
sell/stay in cash at zero or below. One positive raw day alone is not the rule.

**Calculation and warmup:** `midpoint = (H+L)/2`;
`daily EMV = change(midpoint) * (H-L) * 100,000,000/V`.
This app assigns zero to zero-volume or zero-range days. Undefined zero-volume
division is not a measured zero from the reference formula.
First decision after **15 bars**, giving 14 midpoint changes.

**Walkthrough:** Midpoint rises by 2, range is 4 and volume is 100 million:
daily EMV is 8. If the 14-change average is +2, request a buy.
If that average later reaches zero, request a sale.

**What can fail:** Low volume magnifies the score. A quiet shop can be easy
to move and hard to sell into; this signal does not model liquidity or execution.

[Source: Ease of Movement](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ease-of-movement-emv).

<a id="ultimate"></a>
### 24. Ultimate Oscillator: blend three pressure windows

**ELI15:** Mix short, medium and longer notebook sections, giving the shortest
more weight. Ask whether the mixed pressure score is above halfway.

**Exact rules:** Buy/keep owning above 50; sell/stay in cash at 50 or below.
**This is an app midpoint teaching variant, not the original divergence system.**

**Calculation and warmup:** `BP = C - min(L, prior C)`;
`TR = max(H, prior C) - min(L, prior C)`.
For each 7/14/28-change window, `R = sum(BP)/sum(TR)`, neutral 0.5 when the
denominator is zero. `UO = 100 * (4*R7 + 2*R14 + R28)/7`.
First decision after **29 bars**.

**Walkthrough:** Ratios 0.60, 0.55 and 0.50 give about 57.14: request a buy.
All three at 0.40 give 40: request a sale. Flat neutral ratios give 50,
which requests cash rather than retaining ownership in this variant.

**What can fail:** Overlapping windows are not three independent witnesses.
The midpoint can repeatedly flip, and no divergence or extra confirmation
described by the indicator's author is detected.

[Source: Ultimate Oscillator](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ultimate-oscillator).

<a id="vortex"></a>
### 25. Vortex: compare upward and downward reach

**ELI15:** Draw one arrow from yesterday's low to today's high, and another
from yesterday's high to today's low. Compare their recent total lengths.

**Exact rules:** Buy/keep owning if `+VI > -VI`;
sell/stay in cash on a tie or when -VI is greater.

**Calculation and warmup:** `+VM = abs(H - prior L)`;
`-VM = abs(L - prior H)`. Divide each 14-change sum by the same true-range sum.
Zero denominator gives both zero, requesting cash.
First decision after **15 bars**.

**Walkthrough:** True-range sum 20, upward movement sum 26 and downward
sum 18 give +VI 1.3 and -VI 0.9: buy.
Later, both lines at 1.1 request a sale.

**What can fail:** Repeated crossings can create expensive whipsaws,
meaning quickly reversed decisions. There is no intraday confirmation,
short-selling rule or automatic profitability from the directional labels.

[Source: Vortex](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/vortex-indicator).

<a id="trix"></a>
### 26. TRIX: follow a heavily smoothed price

**ELI15:** Smooth a bumpy toy-price drawing three times, then ask whether the
final smoothed line is rising or falling.

**Exact rules:** Buy/keep owning for positive TRIX;
sell/stay in cash for zero or negative TRIX. No signal-line crossover is used.

**Calculation and warmup:** `triple = EMA15(EMA15(EMA15(C)))`;
`TRIX = 100 * (triple_today/triple_previous - 1)`.
Each stage needs its own 15-value seed. First third-stage value at bar 43;
first change and decision at **bar 44**.

**Walkthrough:** The final smoothed line moving from 100 to 100.2 gives
TRIX +0.2%, requesting a buy. A later flat or falling final line requests a sale.
These are changes in the smoothed line, not a claim that the actual stock
changed by that percentage.

**What can fail:** Triple smoothing can react very late to a reversal.
Smooth is not the same as timely, predictive or profitable.

[Source: TRIX](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/trix).

<a id="force"></a>
### 27. Force Index: weight price changes by activity

**ELI15:** A toy-price rise during a busy visit gets more weight than the same
rise during a quiet visit. Count the price move's size as well as its direction.

**Exact rules:** Buy/keep owning when `EMA13(daily force) > 0`;
sell/stay in cash at zero or below.

**Calculation and warmup:** `daily force = (C - prior C) * V`.
Seed EMA13 from 13 actual changes. First decision after **14 bars**.
A zero-volume day contributes zero but does not instantly erase an earlier
smoothed positive or negative reading.

**Walkthrough:** Price rise 2 with volume 1,000 gives raw force +2,000;
fall 1 with volume 500 gives -500. The decision uses the smoothed line:
EMA +300 requests a buy, while EMA -100 requests a sale.

**What can fail:** One exceptional price/volume day can dominate.
Unlike OBV, this weights movement size, but both still rely on reported
volume and past prices, not a measured forecast.

[Source: Force Index](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/force-index).

## How to explore a rule in the app

Select it in the strategy picker, open **Explain pattern**, then inspect
**See the rule** and step through **Play days**. Compare the decision session
with the following opening execution. These 27 rules also have in-app lessons
and metadata in JSON export; the export preserves the full experiment, not only
the currently visible replay prefix.

The exact fixed settings here describe current source. They are not a claim
that the older published v0.1.0 package contains all 27 strategies.

## Sources, overlap and limits

The linked ChartSchool pages are educational formula/interpretation references,
not original-author publications, endorsements of this application or evidence
for our combined trading rules. The 20-strategy expansion's references were
reviewed on 2026-11-12. This complete-documentation pass checked all 27 against
their actual implementation; it did not independently re-qualify market data
or reproduce a source's performance results.

Twenty-seven strategy choices are **not 27 independent signals**:
Williams/Stochastic share range information; SMA/EMA/MACD/TRIX/TSI reuse smoothing;
both Bollinger rules use the same bands with opposite hypotheses; CMF and the
Chaikin Oscillator share daily close-location flow. Volume-weighted indicators
also depend on the same reported volume.

There is no profitability ranking, optimized setting, guaranteed stop fill,
general divergence recognition or point-in-time market-data qualification.
Compare history windows, costs, entry dates, open holdings and source revisions
before comparing reported returns. Testing a rule on old prices does not prove
it will work on new prices.

Implementation references:
[catalogue and original seven targets](../src/stonks_sniper/patterns.py),
[20 added studies and their guides](../src/stonks_sniper/studies.py),
[execution and accounting](../src/stonks_sniper/engine.py),
[in-app lessons](../src/stonks_sniper/lessons.py).

Broader primary-source research, parameter schemas, SAR, VWAP, confirmed chart
structures, statistical pairs and multi-timeframe ideas remain in
[SS-06](../TODO/06_PATTERN_CATALOGUE.todo). Baskets and AI remain planned.
