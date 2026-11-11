from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Lesson:
    title: str
    idea: str
    buy: str
    sell: str
    catch: str
    example: str
    words: str


LESSONS = {
    "sma": Lesson(
        "Follow the trend",
        "Compare a short price average with a longer one. An average smooths daily ups and downs.",
        "The 10-day average is above the 30-day average.",
        "The short average is no longer above the long average.",
        "A sideways market can make this idea buy and sell repeatedly.",
        "Suppose the last 10 closing prices average INR 110 and the last 30 average "
        "INR 100. The rule wants to own the stock. It buys at the next trading day's "
        "opening price, not at either average. If the short average later becomes "
        "INR 98 while the long one is INR 100, it sells at the next opening.",
        "SMA means simple moving average: add the chosen closing prices and divide "
        "by their count. A close is the day's final reported price. "
        "A trend is the general direction prices have been moving.",
    ),
    "ema": Lesson(
        "Follow a faster trend",
        "Like a moving average, but recent prices count more.",
        "The faster 12-day average is above the slower 26-day average.",
        "The faster average is no longer above the slower one.",
        "Reacting faster can also mean reacting to more short-lived changes.",
        "If the 12-day weighted average is INR 105 and the 26-day one is INR 100, "
        "the rule wants to own the stock. If the faster one later falls to INR 99 "
        "while the slower one is INR 100, it wants to sell. Neither average tells "
        "you tomorrow's actual price.",
        "EMA means exponential moving average: newer prices get more weight. "
        "This app starts each EMA with a complete ordinary average. Then it updates "
        "by adding 2 / (days + 1) times the gap between the latest close and the old "
        "average. That fraction is sometimes called alpha.",
    ),
    "rsi": Lesson(
        "Look for a bounce",
        "RSI is a 0-to-100 measure of recent price gains versus losses. It is not a forecast.",
        "RSI falls to 30 or below, after a run of weakness.",
        "RSI reaches 70 or above. Otherwise, keep the current position.",
        "A falling stock can keep falling. A low score does not make it cheap.",
        "An RSI of 28 asks the test to buy next opening. An RSI of 45 does nothing "
        "new: if it already owns the stock, it keeps it. At 72 it asks to sell. "
        "A score of 28 does not mean the stock has a 28% chance of rising.",
        "RSI means relative strength index. It compares smoothed recent gains with "
        "smoothed recent losses across 14 price changes. Wilder smoothing keeps "
        "13 parts of the old average and adds 1 part of the latest change, then "
        "divides by 14. 'Oversold' is a nickname for a low score, not proof of a bargain.",
    ),
    "donchian": Lesson(
        "Watch for a breakout",
        "Look for a price escaping the range of the previous 20 trading days.",
        "The closing price is above every high in the previous 20 days.",
        "The closing price is below every low in the previous 20 days.",
        "A breakout can quickly reverse. The current day is not part of the old range.",
        "Suppose the highest price of the previous 20 trading days was INR 120 and "
        "the lowest was INR 90. A close of INR 121 asks for a buy next opening. "
        "A later close below that day's newly calculated 20-day low asks for a sale.",
        "A breakout means moving beyond an earlier price range. The Donchian "
        "channel is simply the pair of lines marking that old high and low. "
        "A trading day means a day with a reported observation, not a calendar day.",
    ),
    "bollinger": Lesson(
        "Test a return to average",
        "A moving price band shows how far today's price is from its recent average.",
        "The close falls below the lower 20-day band.",
        "The close reaches the 20-day average. Otherwise, keep the current position.",
        "The bands are not a floor or ceiling. Prices can stay outside them.",
        "If the recent average is INR 100 and the lower band is INR 90, a close "
        "of INR 89 asks for a buy. A later close of INR 100 asks for a sale only "
        "if it reaches that day's newly calculated average. The average moves too.",
        "Bollinger bands are an average plus and minus a measure of how spread out "
        "prices have been. This version uses 20 closes and twice their population "
        "standard deviation. To find that spread: subtract the average from each "
        "price, square each gap, average those squares, and take the square root. "
        "'Mean reversion' is the idea of returning toward an average, not a promise.",
    ),
    "macd": Lesson(
        "Watch momentum change",
        "MACD compares two price averages. A signal line smooths that difference.",
        "MACD is above its signal line.",
        "MACD is no longer above its signal line.",
        "This reacts to price changes that have already happened, not tomorrow's news.",
        "If the 12-day EMA is INR 108 and the 26-day EMA is INR 100, MACD is 8. "
        "If its signal line is 6, the rule wants to own the stock. If MACD later "
        "becomes 4 while the signal is 5, it wants to sell next opening.",
        "Momentum means how strongly a price has recently been moving. MACD means "
        "moving average convergence/divergence: the 12-day EMA minus the 26-day EMA. "
        "An EMA is an average giving newer values more weight. The signal line is "
        "a 9-value EMA of MACD, not a prediction or a guaranteed buy instruction.",
    ),
    "engulfing": Lesson(
        "Read a candle reversal",
        "A candle body shows the gap between a day's opening and closing prices.",
        "An up-day body surrounds the previous down-day body.",
        "A down-day body surrounds the previous up-day body.",
        "A shape is not proof of a reversal. Tiny adjusted-price changes can flip this rule.",
        "Yesterday opens at INR 110 and closes at INR 100: a down-day body. Today "
        "opens at INR 99 and closes at INR 111: an up-day body covering the entire "
        "old body. That asks for a buy next opening. The mirror image asks for a sale. "
        "The thin high/low lines are not part of this body-only rule.",
        "A candle is one day's opening, highest, lowest and closing price drawn as "
        "a shape. Its thick body joins the opening and closing prices. The thin "
        "lines show the day's high and low. Engulfing means covering the earlier "
        "body. A doji has equal opening and closing prices; this rule excludes it. "
        "Matching body edges are allowed.",
    ),
    "stochastic": Lesson(
        "Try a bounce near the range floor",
        "Ask where the close sits inside the last 14 days' highest and lowest prices, "
        "then average three scores to reduce daily jumping.",
        "The smoothed range score is 20 or below.",
        "The score reaches 80 or above; keep the current position in between.",
        "A price near the bottom can stay there. This is not a cheapness detector.",
        "With a 90-to-110 range, a close of 92 scores 10. Three scores of 10, 20 "
        "and 30 average 20: buy next opening. At 50 keep owning; at 80 sell.",
        "%K is the raw 0-to-100 range position; %D is its three-value simple "
        "average. A completely flat range gets a neutral score of 50.",
    ),
    "williams": Lesson(
        "Follow the upper half of the range",
        "Measure how close the final price is to the recent high, rather than "
        "buying just because it has fallen.",
        "Williams %R is above -50.",
        "The score is -50 or lower.",
        "It is the same raw range information as stochastic, shifted down by 100. "
        "These two indicators are not independent witnesses.",
        "For a 90-to-110 range, a close of 106 gives -20: buy. A close of 100 "
        "gives -50: sell. Unlike the bounce rule, this rule prefers upper-half prices.",
        "%R goes from -100 at the range bottom to 0 at the top. "
        "A minus sign here is a scale choice, not a loss on your investment.",
    ),
    "cci": Lesson(
        "Follow an unusually strong move",
        "Compare a day's representative price with its usual level and usual "
        "distance from that level.",
        "CCI rises above 100.",
        "CCI reaches zero or below; keep owning between zero and 100 after entry.",
        "Unusual strength may be the last burst before a fall. The score is not a percentage.",
        "If typical price is 103, its 20-day mean is 100 and mean absolute gap "
        "is 1, CCI is 3 / 0.015 = 200: buy. At 50 keep owning; at zero sell.",
        "Typical price is the mean of high, low and close. Mean absolute deviation "
        "means average gap size, ignoring plus or minus. CCI scales that gap by 0.015.",
    ),
    "roc": Lesson(
        "Check whether price gained ground",
        "Compare today's close with the close 12 trading days earlier.",
        "The percentage change over those 12 days is positive.",
        "The change is zero or negative.",
        "The old price changes each day too. A comparison can flip without a dramatic new move.",
        "From 100 twelve sessions ago to 106 today is +6%: buy next opening. "
        "From 100 to 99 is -1%: sell. This is past movement, not a predicted gain.",
        "ROC means rate of change: divide today's price by the earlier price, "
        "subtract one, then multiply by 100. It needs 13 closes to compare 12 changes.",
    ),
    "tsi": Lesson(
        "Smooth out the tug of war",
        "Smooth daily gains and losses twice, then compare their net direction "
        "with the total amount of movement.",
        "True Strength Index is above zero.",
        "It is zero or below.",
        "Smoothing removes some noise but can hide a reversal until much later.",
        "If twice-smoothed signed changes are +2 and twice-smoothed absolute "
        "changes are 4, TSI is +50: buy. If the numerator becomes -1, sell.",
        "Signed change keeps the plus or minus. Absolute change ignores the sign. "
        "Both pass through 25-value then 13-value EMAs. A flat denominator gives zero.",
    ),
    "adx": Lesson(
        "Follow a strong upward direction",
        "Check both which direction is winning and whether that direction "
        "looks strong enough to follow.",
        "The up-direction score exceeds the down score, and ADX is at least 25.",
        "Either condition stops being true.",
        "A high ADX alone can describe a strong fall. Seeded scores can take "
        "roughly 150 observations to settle; the first usable value is not fully settled.",
        "Up score 30, down score 12 and strength 28 means buy. Up 12 versus "
        "down 30 means sell even if strength is 40. Strength 24 also means cash.",
        "+DI and -DI compare expansions of highs and lows relative to true range. "
        "ADX smooths their percentage separation using Wilder's 14-change recipe.",
    ),
    "aroon": Lesson(
        "Ask which extreme happened recently",
        "A recent high supports an upward trend; a recent low argues against it.",
        "Aroon Up exceeds Aroon Down and Up is at least 70.",
        "Either condition fails.",
        "One tiny new high can produce a high score. Recent does not necessarily mean powerful.",
        "A high two sessions ago scores 92; a low 20 sessions ago scores 20: "
        "buy. If both extremes are recent and tied at 100, this rule stays in cash.",
        "Aroon measures the age of an extreme, not its price. We inspect today "
        "plus 25 earlier observations; the newest equal high or low wins a tie.",
    ),
    "ichimoku": Lesson(
        "Check price above an older cloud",
        "Compare price with a pair of earlier range measurements drawn at today's "
        "position, while checking the short range is above the longer one.",
        "The close is above both visible cloud lines and the 9-day midpoint "
        "is above the 26-day midpoint.",
        "Any of those conditions fails.",
        "A cloud drawn ahead is not future knowledge. This version deliberately "
        "uses only calculations made 26 observations earlier for today's visible cloud.",
        "Visible cloud edges 95 and 100, close 105, short midpoint 104 and long "
        "midpoint 102 mean buy. A close of 100 fails the strict above-cloud test.",
        "A range midpoint is halfway between its highest high and lowest low. "
        "The cloud combines 9-, 26- and 52-day ranges with a 26-day drawing shift. "
        "No backward-drawn confirmation is used; 78 finished bars are required.",
    ),
    "keltner": Lesson(
        "Follow a jump beyond normal swings",
        "A moving channel expands when daily movement, including overnight jumps, grows.",
        "The close is above the upper Keltner channel.",
        "The close reaches the middle line or falls below it; otherwise keep owning.",
        "A jump can reverse before the next opening. "
        "A channel edge is not a guaranteed sale price.",
        "With middle 100 and average true range 3, the upper line is 106. "
        "Close 107 means buy. Close 104 keeps an existing holding; close 100 sells.",
        "The middle is EMA20. The upper line adds twice Wilder ATR10. "
        "ATR is average true range: a gap-aware measure of typical movement, not direction.",
    ),
    "bollinger-breakout": Lesson(
        "Follow strength above the price band",
        "Treat an unusually high close as possible strength, instead of buying "
        "an unusually low close as our original Bollinger rule does.",
        "The close is above the upper 20-day Bollinger band.",
        "It reaches the 20-day average or falls below it.",
        "The same bands support opposite hypotheses. Neither hypothesis becomes "
        "reliable just because the indicator is popular.",
        "Average 100 and population spread 4 give an upper band of 108. "
        "Close 109 buys; close 105 keeps an existing holding; close 100 sells.",
        "The upper band is the mean of 20 closes plus twice their population "
        "standard deviation. This is not a squeeze detector or a probability guarantee.",
    ),
    "chandelier": Lesson(
        "Raise the exit floor while owning",
        "Enter above the average, then lift a trailing exit level as the "
        "high-minus-normal-swings calculation rises.",
        "From cash, close is above its 22-day average and above the candidate exit level.",
        "The finished close reaches the active exit level or falls below it.",
        "The source's basic line can fall; our extra ratchet never lowers it during "
        "a holding. An overnight gap can still make the actual sale much worse.",
        "Highest high 120 and ATR 4 give candidate 108. Close 115 above average "
        "110 buys. A later candidate 112 lifts the exit to 112; candidate 107 "
        "cannot lower it. Close 111 triggers a next-opening sale, not a fill at 112.",
        "A ratchet moves only upward here. The candidate uses a rolling 22-day "
        "high minus three ATR22. After exit, reset the level; do not re-enter on that same close.",
    ),
    "obv": Lesson(
        "Check whether busy days lean upward",
        "Keep a running balance of volume on up-close days minus volume on down-close days.",
        "The on-balance-volume line is above its 20-day EMA.",
        "It is equal to or below that average.",
        "Volume counts reported trading, not money arriving in a company's bank account.",
        "An up-close day with volume 1,000 adds 1,000. A down-close day with "
        "volume 400 subtracts 400. If the balance is 600 and its EMA is 500, buy; "
        "at balance 450 versus EMA 500, sell.",
        "OBV means on-balance volume. It starts at zero; an unchanged close "
        "adds nothing. Unlike Force Index, it ignores how large the price change was.",
    ),
    "cmf": Lesson(
        "Check where busy days finish",
        "Days finishing near their high add upward pressure; days near their low "
        "add downward pressure, weighted by reported volume.",
        "The 20-day Chaikin Money Flow score is above zero.",
        "The score reaches zero or turns negative.",
        "Finishing near the daily high can still happen after a big overnight fall. "
        "No-volume windows are neutral by convention, not measured evidence.",
        "High 110, low 90 and close 105 give a location score of +0.5. "
        "Across 20 days, weighted flow +5,000 divided by volume 10,000 is +0.5: "
        "buy. A zero or negative total score sells.",
        "CMF divides summed close-location times volume by summed volume. "
        "A flat high-low day contributes zero; a zero-volume window gets score zero.",
    ),
    "mfi": Lesson(
        "Try a bounce after volume-backed weakness",
        "Compare typical-price-times-volume on rising-price days with falling-price days.",
        "Money Flow Index is 20 or below.",
        "It is 80 or above; keep the current position in between.",
        "A busy fall may continue. This score is not a count of buyers versus sellers.",
        "If the last 14 changes have positive flow 1,000 and negative flow "
        "9,000, MFI is 10: buy. Equal flows score 50, keeping an existing holding. "
        "Positive flow 9,000 versus negative 1,000 scores 90: sell.",
        "Typical price is (high + low + close) / 3. MFI is 100 times positive "
        "flow divided by total positive and negative flow. No flow gives neutral 50.",
    ),
    "chaikin": Lesson(
        "Watch volume pressure speed up",
        "Build a running close-location-and-volume balance, then compare "
        "a faster and a slower average of it.",
        "The three-day EMA of that balance is above its ten-day EMA.",
        "The faster average is no longer above the slower one.",
        "This transforms volume twice. It can turn upward even while price falls.",
        "If the balance's fast average is 1,200 and slow average is 1,000, "
        "the oscillator is +200: buy. Fast 900 versus slow 1,000 gives -100: sell.",
        "ADL is the running sum of volume times the day's close-location multiplier. "
        "Chaikin Oscillator subtracts EMA10 from EMA3 of ADL. A zero range contributes zero.",
    ),
    "emv": Lesson(
        "Check whether price moves easily upward",
        "Look for range midpoints rising with a wide range and relatively little volume.",
        "The 14-change average Ease of Movement score is above zero.",
        "The average is zero or below.",
        "Low-volume moves can be fragile, not safe. This app explicitly assigns "
        "zero contribution to zero-volume days rather than dividing by zero.",
        "Midpoint rises by 2, daily range is 4 and volume is 100 million: "
        "daily EMV is 8. If its 14-change mean is +3, buy; at zero or -3, sell.",
        "A midpoint is halfway between high and low. EMV multiplies midpoint "
        "change by the daily range and divides by volume scaled to 100 million. "
        "Flat ranges also contribute zero.",
    ),
    "ultimate": Lesson(
        "Blend short and longer price pressure",
        "Combine how strongly days finish across three windows, giving the shortest "
        "window the most weight.",
        "The Ultimate Oscillator is above 50.",
        "It is 50 or below.",
        "This is a simple halfway-line version, not the original multi-step "
        "divergence strategy. The three windows overlap.",
        "If the 7-, 14- and 28-change pressure ratios are 0.7, 0.6 and 0.5, "
        "the weighted score is 100 * (2.8 + 1.2 + 0.5) / 7, about 64.3: buy. "
        "A score of exactly 50 sells.",
        "Buying pressure is close minus the lower of today's low and yesterday's "
        "close. Divide summed pressure by summed true range for each window; "
        "combine with weights 4, 2 and 1. A zero-range window gets neutral ratio 0.5.",
    ),
    "vortex": Lesson(
        "Compare upward and downward reach",
        "Compare today's high with yesterday's low, and today's low with yesterday's high.",
        "The 14-change upward Vortex line exceeds the downward line.",
        "The upward line is equal to or below the downward line.",
        "Sideways movement can make the lines swap places repeatedly and rack up fees.",
        "If upward reach totals 42, downward reach totals 28 and true range "
        "totals 35, the lines are 1.2 and 0.8: buy. A tie means sell or stay in cash.",
        "+VI and -VI divide sums of absolute cross-day distances by the same "
        "14-change true-range sum. Zero total range makes both zero.",
    ),
    "trix": Lesson(
        "Follow a heavily smoothed price",
        "Smooth closing prices three times, then ask whether the resulting line "
        "rose or fell since yesterday.",
        "The triple-smoothed line's one-day percentage change is positive.",
        "Its change is zero or negative.",
        "A very smooth line can be very late. A clean-looking chart is not proof of good returns.",
        "A triple-smoothed value going from 100 to 100.2 gives TRIX +0.2%: "
        "buy. Going from 100 to 99.9 gives -0.1%: sell.",
        "TRIX uses three EMA15 stages, each needing a full seed window. "
        "The first usable change requires 44 closes; it is not raw price's 15-day return.",
    ),
    "force": Lesson(
        "Measure the push behind a price move",
        "Multiply each daily price change by its volume, then smooth the result.",
        "The 13-change EMA of Force Index is above zero.",
        "It is zero or below.",
        "One unusually busy or large move can dominate. A zero-volume day does not "
        "erase the existing average immediately.",
        "A rise of 2 with volume 1,000 gives force +2,000. A fall of 1 with "
        "volume 500 gives -500. A smoothed reading +300 buys; -100 sells.",
        "Force is price change times reported volume, not physical force. "
        "Unlike OBV, a larger price change matters more even with the same volume.",
    ),
}
