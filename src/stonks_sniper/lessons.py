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
}
