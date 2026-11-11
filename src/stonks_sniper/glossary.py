from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape

from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QCursor, QDesktopServices
from PySide6.QtWidgets import QTextBrowser, QToolTip

from stonks_sniper.theme import ACCENT, WARM


@dataclass(frozen=True)
class Term:
    title: str
    meaning: str
    example: str
    aliases: tuple[str, ...] = ()


TERMS = {
    "stock": Term(
        "Stock / share",
        "A share is a small piece of ownership in a company. 'Stock' refers to those "
        "ownership pieces. Its market price can change as buyers and sellers agree on new prices.",
        "Imagine a toy shop divided into 100 ownership pieces. Owning one piece means "
        "owning 1% of the shop, not owning one toy. Someone may offer more or less "
        "for your piece tomorrow.",
        ("share", "shares", "stocks"),
    ),
    "exchange": Term(
        "Stock exchange",
        "An organized place where people buy and sell company shares.",
        "Think of a vegetable market with trading rules. NSE and BSE are two Indian "
        "stock exchanges, like two different organized marketplaces.",
        ("market", "stock market", "NSE", "BSE"),
    ),
    "symbol": Term(
        "Stock symbol",
        "A short name used to find a particular company's stock on a data service or exchange.",
        "A toy shop might label a box 'RED-CAR' so you can find the right toy. "
        "RELIANCE is a stock's short label; it is not its price.",
        ("ticker", "stock ticker"),
    ),
    "inr": Term(
        "INR",
        "The currency code for Indian rupees. An amount marked INR is measured in rupees.",
        "If a bag of potatoes costs INR 40, it costs 40 Indian rupees. "
        "A practice balance of INR 1,000 is 1,000 pretend rupees, not 1,000 shares.",
        ("rupee", "rupees", "currency"),
    ),
    "price": Term(
        "Price",
        "The amount of money paid for one unit of something. A stock price can change.",
        "A tomato costs INR 5 this morning and INR 7 later. Its price changed; "
        "that does not tell you what it will cost tomorrow.",
        ("prices",),
    ),
    "history": Term(
        "Price history",
        "Recorded prices from earlier days. This tool uses reported real observations, "
        "not invented market moves.",
        "A notebook listing what onions actually cost each day is history. "
        "Making up tomorrow's onion price is not history.",
        ("observation", "observations", "historical data", "daily data", "market data"),
    ),
    "session": Term(
        "Trading day",
        "A day represented by a completed market observation. "
        "Closed-market days are not trading days.",
        "If the vegetable stall shuts on Sunday, its next selling day after Saturday "
        "may be Monday. The next trading day need not be tomorrow's calendar date.",
        ("session", "sessions", "bar", "bars", "trading days"),
    ),
    "open": Term(
        "Opening price",
        "The reported price at the beginning of a trading day.",
        "The first recorded sale of a toy car today is INR 100. That is its opening "
        "price for this example, even if later cars sell for a different amount.",
        ("open", "opening", "next opening"),
    ),
    "close": Term(
        "Closing price",
        "The reported price at the end of a trading day. "
        "This tool reads the finished day before making its decision.",
        "A potato stall's final recorded price today is INR 30 per bag. That is today's "
        "close in this example. You cannot know it at breakfast.",
        ("close", "closes", "closing", "daily close"),
    ),
    "high-low": Term(
        "Day's high and low",
        "The highest and lowest reported prices during one trading day.",
        "A toy sold for INR 90, then INR 110, then INR 100. Its high was INR 110 "
        "and its low was INR 90, even though its final price was INR 100.",
        ("high", "low", "day high", "day low", "highs", "lows"),
    ),
    "candle": Term(
        "Price candle",
        "A drawing of one day's opening, highest, lowest and closing prices. The thick "
        "body joins open and close; thin lines extend to the high and low.",
        "A toy opens at INR 10, reaches INR 14, dips to INR 9 and closes at INR 12. "
        "Draw a thick body from 10 to 12 and thin lines reaching 9 and 14.",
        ("candlestick", "candles", "candlesticks", "body", "OHLC"),
    ),
    "volume": Term(
        "Trading volume",
        "How many units were traded during a period, not how much the price rose.",
        "A stall sells 200 tomatoes today and 50 tomorrow. Today's sales volume was "
        "larger, even if tomorrow's tomatoes were more expensive.",
    ),
    "adjusted": Term(
        "Adjusted price",
        "An old price rescaled to account for events such as share splits and cash "
        "payments to owners. It is not necessarily the actual cash price paid on that old day.",
        "A toy shop replaces every large token with two small tokens. Comparing "
        "one old large token with one new small token would mislead you. Rescaling "
        "helps compare them, but does not change what you actually paid earlier.",
        ("adjusted", "adjusted prices", "price basis", "adjustment", "adjusted OHLC"),
    ),
    "split": Term(
        "Share split",
        "A company divides each existing share into more shares. "
        "The division alone does not make the owner richer.",
        "Cut one pizza into eight slices instead of four. You have more slices, "
        "but still the same pizza. A split is similar for ownership pieces.",
        ("splits",),
    ),
    "dividend": Term(
        "Dividend",
        "Money a company pays to its shareholders. It is not a guaranteed payment.",
        "A toy shop gives some of its earned cash to the people who own pieces of "
        "the shop. That cash payment is like a dividend, not a free extra toy.",
        ("dividends",),
    ),
    "units": Term(
        "Adjusted test units",
        "The quantities used by this test with adjusted prices. They can be fractions "
        "and are not a literal count of real shares you could have bought.",
        "A recipe can use 1.5 cups even when a shop sells whole packets. "
        "Likewise, a test quantity is a calculation unit, not a real shop order.",
        ("unit", "test units", "research units", "fractional", "fractional adjusted units"),
    ),
    "pattern": Term(
        "Pattern / trading idea",
        "A repeatable rule for deciding when to own a stock and when to keep cash. "
        "Seeing a pattern does not prove that the next move will follow it.",
        "You notice tomatoes often become cheaper after a busy market day. "
        "You can write a rule and test old prices, but a shortage could break the pattern.",
        ("patterns", "strategy", "strategies", "trading rule"),
    ),
    "simulation": Term(
        "Practice test / simulation",
        "Calculate what an exact rule would have done on the loaded history, using "
        "pretend money and stated costs. No real order is placed.",
        "Replay a notebook of real potato prices using play money. "
        "You can count pretend purchases without buying a single potato.",
        ("simulate", "backtest", "backtesting", "experiment"),
    ),
    "capital": Term(
        "Starting money",
        "The practice money available at the start of the test.",
        "You begin a toy-shop game with INR 1,000 in play money. That INR 1,000 "
        "is your starting amount; it is not money earned by the game.",
        ("capital", "initial cash", "initial money"),
    ),
    "cash": Term(
        "Cash",
        "Money not currently invested in the stock. This test does not pay interest on it.",
        "You keep INR 100 in your pocket instead of buying a toy. "
        "If the toy's price falls, your pocket still holds INR 100.",
    ),
    "buy": Term(
        "Buy",
        "Exchange available money for ownership units. This test uses its available "
        "cash, including the cost of the purchase.",
        "Spend play money to get toy-shop tokens. If each token becomes more valuable, "
        "your holding is worth more; if it becomes cheaper, your holding is worth less.",
        ("entry", "enter", "buying"),
    ),
    "sell": Term(
        "Sell",
        "Exchange the units already owned for cash, minus the chosen costs.",
        "Return the toy-shop tokens you own in exchange for play money. "
        "A later price rise does not benefit tokens you have already sold.",
        ("exit", "selling", "liquidate"),
    ),
    "long": Term(
        "Owning stock / long",
        "Owning units that gain value when the stock price rises and lose value when it falls.",
        "You own a toy worth INR 100. If buyers now offer INR 120, your toy is worth "
        "more. If they offer INR 80, it is worth less. 'Long' describes that ownership.",
        ("position", "holdings", "exposure", "holding"),
    ),
    "signal": Term(
        "Rule decision / signal",
        "What the rule wants to own after reading a finished day. It is not yet a completed trade.",
        "After the vegetable stall closes, you decide to buy potatoes next time it "
        "opens. The decision tonight is not a potato purchase tonight.",
        ("target", "targets", "signals", "decision"),
    ),
    "fill": Term(
        "Simulated trade / fill",
        "The point at which the test actually carries out a needed buy or sell, "
        "at the next available opening price with the chosen costs.",
        "You decide tonight to buy a toy. Tomorrow the shop opens at INR 110, not "
        "tonight's INR 100. The purchase at 110 is the trade, not the earlier decision.",
        ("fills", "execution", "trade", "trades"),
    ),
    "fee": Term(
        "Trading fee",
        "A cost charged on a purchase or sale. This tool uses a simple percentage model, "
        "not every real tax or charge.",
        "A toy marketplace charges a small service fee each time you buy or sell. "
        "Even if the toy's price stays unchanged, those fees can reduce your money.",
        ("fees", "brokerage", "trading costs"),
    ),
    "slippage": Term(
        "A worse trading price / slippage",
        "The test makes buying a little more expensive and selling a little cheaper "
        "than the reported opening price.",
        "The vegetable board says INR 100 a bag, but you end up paying INR 101. "
        "That extra INR 1 illustrates a worse purchase price. This model always "
        "makes the price less favourable, never magically better.",
        ("adverse slippage", "worse price", "price disadvantage"),
    ),
    "bps": Term(
        "Basis points / bps",
        "A small percentage unit: 100 basis points is 1%; 10 is 0.1%. "
        "The main controls instead describe cost per INR 10,000.",
        "A toy order of INR 10,000 with a 10-basis-point fee costs about INR 10 "
        "in fees. It does not cost 10% or INR 1,000.",
        ("basis point", "basis points", "bps/side"),
    ),
    "equity": Term(
        "Money now / equity",
        "Cash plus the current value of any units still owned. It is not all cash "
        "and does not include an uncharged future selling cost.",
        "You have INR 40 in your pocket and a toy currently worth INR 60. "
        "Together they are worth INR 100, even though only INR 40 is cash.",
        ("marked equity", "research equity", "money now"),
    ),
    "return": Term(
        "Gain or loss / return",
        "The percentage change from starting money to the test's current total value, "
        "including the chosen costs already charged.",
        "Start a toy game with INR 100. If cash plus toys is now worth INR 110, "
        "the gain is 10%. At INR 90, the loss is 10%.",
        ("returns", "gain", "loss", "profit", "return_pct"),
    ),
    "drawdown": Term(
        "Fall from an earlier high / drawdown",
        "How far the test's value fell below an earlier peak. 'Biggest fall' is "
        "the largest such drop so far, not the total loss since the start.",
        "Your toy collection rises from INR 100 to INR 150, then falls to INR 120. "
        "It is 20% below its 150 peak, even though it is still worth more than the starting 100.",
        ("max drawdown", "maximum drawdown", "biggest fall", "peak", "drawdowns"),
    ),
    "benchmark": Term(
        "Reference test / benchmark",
        "A simple comparison: buy once after the chosen idea has enough history, "
        "then keep holding. It uses the same starting money and entry costs.",
        "Compare two toy games: one repeatedly buys and sells; the other buys once "
        "and waits. If they start on different days, that alone can change the result.",
        ("buy and hold", "buy & hold", "buy once & hold", "reference line"),
    ),
    "warmup": Term(
        "Getting enough history / warmup",
        "The earlier observations a rule needs before it can calculate its first "
        "decision. A further day is needed before that decision can become a trade.",
        "You cannot average 10 days of potato prices after seeing only 3 days. "
        "Wait until the notebook has 10 entries before using that rule.",
        ("initialization", "seed", "seeded"),
    ),
    "lookback": Term(
        "Days looked back / lookback",
        "How many earlier observations a calculation uses. This tool counts reported trading days.",
        "To compare today's tomato price with the previous 20 selling days, "
        "look at 20 earlier notebook entries, not the next 20 entries.",
        ("window", "period"),
    ),
    "average": Term(
        "Average",
        "Add a group of numbers, then divide by how many numbers there are.",
        "Three toy prices are INR 10, INR 20 and INR 30. "
        "Their average is (10 + 20 + 30) / 3 = INR 20.",
        ("mean", "moving average", "averages"),
    ),
    "percent": Term(
        "Percentage / %",
        "A way to describe an amount out of 100. To find a percentage change, "
        "divide the change by the starting amount and multiply by 100.",
        "A toy rises from INR 50 to INR 60. The increase is 10 out of the starting "
        "50: 10 / 50 x 100 = 20%. It did not rise by only 10%.",
        ("percentage", "percent", "percentage change"),
    ),
    "fraction": Term(
        "Fraction",
        "Part of a whole. A decimal such as 0.5 can also describe a fraction: one half.",
        "Half a pizza is 1 / 2 of a pizza, or 0.5 pizzas. In a calculation you "
        "can own 1.5 units, just as a recipe can use one and a half cups.",
        ("fractions", "decimal"),
    ),
    "weight": Term(
        "Weight in an average",
        "How much influence one value has in a calculation. More weight means "
        "that value has a bigger effect on the answer, not that it is physically heavier.",
        "Give today's toy price two votes and yesterday's price one vote. "
        "Today's price now has more influence on the average.",
        ("weight", "weighted", "weights", "smoothing", "smoothed"),
    ),
    "square": Term(
        "Squaring a number",
        "Multiply a number by itself. "
        "A negative number multiplied by itself also becomes positive.",
        "A square tray has 3 rows with 3 toy blocks in each: 3 x 3 = 9 blocks. "
        "Likewise, squaring a price gap of -3 gives (-3) x (-3) = 9.",
        ("square", "squares", "squared", "squaring"),
    ),
    "square-root": Term(
        "Square root",
        "The nonnegative number that, multiplied by itself, gives the original "
        "nonnegative number. It reverses squaring.",
        "Nine toy blocks form a square with 3 blocks on each side. "
        "The square root of 9 is 3 because 3 x 3 = 9.",
        ("square root",),
    ),
    "interest": Term(
        "Interest",
        "Money paid for saving or lending money, or charged for borrowing it. "
        "This test adds no interest to unused cash.",
        "A pretend savings box starts with INR 100 and earns INR 2 for waiting. "
        "That extra INR 2 is interest. This app's unused play money stays at 100 instead.",
    ),
    "chart": Term(
        "Reading a chart",
        "A picture of numbers. Here, dates run left to right and the measured "
        "value runs bottom to top. Read the title and labels to know what is being measured.",
        "Write Monday's potato price of INR 20 and Tuesday's INR 25 on a graph. "
        "Tuesday sits farther right and higher up. "
        "A connecting line does not tell you Wednesday's price.",
        ("graph", "chart", "charts", "graphs", "axis", "axes"),
    ),
    "parameter": Term(
        "Rule setting / parameter",
        "A chosen number or option that changes how a rule works. Choosing a "
        "setting after seeing the answer can make an old test look misleadingly good.",
        "A toy-price rule can average 10 days or 20 days. The chosen day count "
        "is a setting. Picking whichever count won yesterday does not prove it will win tomorrow.",
        ("parameter", "parameters", "configuration"),
    ),
    "trend": Term(
        "Trend",
        "The general direction prices have recently been moving, "
        "not a promise about what happens next.",
        "Onion prices of INR 20, 22, 24 and 26 suggest a rising direction. "
        "A fresh truckload could still make tomorrow's price fall.",
        ("trending",),
    ),
    "sideways": Term(
        "Sideways market",
        "Prices moving up and down without a clear sustained direction.",
        "A toy alternates between INR 99 and INR 101 for weeks. A rule that keeps "
        "switching between buying and selling may pay fees without getting far.",
        ("whipsaw", "whipsaws"),
    ),
    "sma": Term(
        "Follow the trend / SMA",
        "Compare ordinary averages of the last 10 and 30 closes. Own stock when "
        "the 10-day average is higher; otherwise keep cash.",
        "If toy prices average INR 110 over 10 days and INR 100 over 30 days, "
        "the rule asks to own the toy. If the short average later drops below "
        "the long one, it asks to sell next opening. An average is not a sale price.",
        ("simple moving average", "SMA trend", "follow the trend"),
    ),
    "ema": Term(
        "Follow a faster trend / EMA",
        "Compare 12-day and 26-day averages that give newer prices more weight. "
        "Own stock while the faster average is higher; otherwise keep cash.",
        "A toy's recent prices change sharply. Giving newer prices more weight "
        "makes the short average react faster, like paying more attention to "
        "today's shop label than last month's label. Faster can also mean more false starts.",
        ("exponential moving average", "EMA trend", "weighted average", "follow a faster trend"),
    ),
    "alpha": Term(
        "Average update weight / alpha",
        "The fraction of the latest price-to-average gap added to an EMA. "
        "This app uses 2 divided by the number of days plus 1.",
        "Your old toy-price average is INR 10 and today's price is INR 15. "
        "With weight 0.2, add 0.2 x (15 - 10) = INR 1, making the new average INR 11.",
    ),
    "rsi": Term(
        "Look for a bounce / RSI",
        "A 0-to-100 score comparing smoothed recent gains with losses. This version "
        "buys at 30 or below, sells at 70 or above, and keeps its position between them.",
        "After toy prices keep falling, the score might reach 28. The rule buys "
        "next opening, hoping for a bounce. A toy being discounted can still be "
        "discounted further. 28 is not a 28% chance of success.",
        ("relative strength index", "oversold", "overbought", "look for a bounce", "Wilder RSI"),
    ),
    "donchian": Term(
        "Watch for a breakout / Donchian",
        "Buy if today's close is above every high in the previous 20 days. "
        "Sell if it is below every low in those previous days.",
        "Toy prices stayed between INR 90 and INR 120 for 20 selling days. "
        "A close at INR 121 breaks above the old range. "
        "The test asks to buy next opening, but the toy can still fall afterwards.",
        ("Donchian channel", "price channel", "watch for a breakout"),
    ),
    "breakout": Term(
        "Breakout",
        "A price moving beyond a previous range. The escape can last or quickly fail.",
        "Potatoes have sold between INR 20 and INR 30. A price of INR 31 is above "
        "that old range. It does not guarantee INR 32 tomorrow.",
        ("breakouts",),
    ),
    "bollinger": Term(
        "Test a return to average / Bollinger",
        "Bands measure how far price is from its recent average. This version "
        "buys below the lower 20-day band and sells at the 20-day average.",
        "Toy prices average INR 100 and the lower band is INR 90. "
        "A close at 89 asks for a buy. Reaching that day's moving average "
        "later asks for a sale. The band is not a floor under the toy's price.",
        ("Bollinger bands", "bollinger reversion", "test a return to average", "lower band"),
    ),
    "spread": Term(
        "Price spread around an average / standard deviation",
        "A measure of how far values typically sit from their average. The population "
        "version squares each gap, averages those squares and takes the square root.",
        "Toy prices 9, 10 and 11 sit close to their average of 10. "
        "Prices 1, 10 and 19 have the same average but much more spread. "
        "Bands built from the second group would be wider.",
        ("standard deviation", "population standard deviation", "sigma", "volatility", "spread"),
    ),
    "reversion": Term(
        "Return toward average / mean reversion",
        "The idea that a price unusually far from its recent average may move back "
        "toward it. It may not happen, and the average itself can change.",
        "A toy usually costs about INR 100 and is suddenly discounted to INR 80. "
        "It might return toward 100, or become permanently cheaper because nobody wants it.",
        ("mean reversion", "reversion", "bounce"),
    ),
    "momentum": Term(
        "Momentum",
        "A description of how strongly a price has recently been changing. "
        "It is not a force that must keep pushing the price in the same direction.",
        "Toy prices rise 100, 105, 110, 115. The rise has been steady. "
        "Then a new toy arrives and buyers may suddenly stop paying more for the old one.",
    ),
    "macd": Term(
        "Watch momentum change / MACD",
        "Subtract the 26-day weighted average from the 12-day one. Compare that "
        "difference with its own 9-value weighted average, called the signal line. "
        "Own stock when the difference is above that line; otherwise keep cash.",
        "A toy's fast average is 108 and its slow average is 100, so the difference "
        "is 8. If its smoothed comparison is 6, the rule wants to own the toy. "
        "If the difference becomes 4 while the comparison is 5, it asks to sell.",
        (
            "moving average convergence divergence",
            "signal line",
            "MACD signal trend",
            "watch momentum change",
        ),
    ),
    "engulfing": Term(
        "Read a candle reversal / engulfing",
        "An up-day body covering the previous down-day body asks for a buy. "
        "The opposite asks for a sale. Equal body edges count; unchanged-price bodies do not.",
        "Yesterday a toy opened at 110 and closed at 100. Today it opens at 99 "
        "and closes at 111, covering the old 100-to-110 body. "
        "The test asks to buy next opening. That shape does not guarantee a rising price.",
        ("engulfing reversal", "body engulfing", "reversal", "read a candle reversal"),
    ),
    "doji": Term(
        "Unchanged candle body / doji",
        "Here, a day whose opening and closing prices are exactly equal. "
        "This app's engulfing rule excludes it.",
        "A toy starts at INR 100, visits 95 and 105, then ends at 100. "
        "Its opening and closing match even though the price moved during the day.",
    ),
    "gap": Term(
        "Overnight price gap",
        "A difference between a day's close and the next available day's open.",
        "The toy shop closes with a price of INR 100. Overnight, the last box "
        "sells out elsewhere, and the shop reopens at INR 120. "
        "You cannot assume you could buy at 100.",
        ("gaps", "overnight gap"),
    ),
    "replay": Term(
        "Travel through time / replay",
        "Show only the prices, trades and results up to the selected historical day. "
        "The full downloaded history is still kept for saving the complete test.",
        "Cover the later pages of your potato-price notebook. Work with only "
        "what was written by that day, instead of using tomorrow's answer.",
        ("cursor", "travel through time", "play days"),
    ),
    "provider": Term(
        "Data source / provider",
        "The service supplying the observations. Yahoo access here is unofficial "
        "and may fail or revise earlier adjusted values.",
        "A notebook copied from a vegetable price board has a source. "
        "If the board is corrected later, a fresh copy may differ from your old notebook.",
        ("provenance", "source", "Yahoo", "Yahoo Finance", "unofficial"),
    ),
    "quote": Term(
        "Live quote",
        "A recently reported market price. "
        "This tool currently uses daily history, not live quotes.",
        "Yesterday's written potato price is not the price a seller is offering "
        "right now. This app shows the notebook, not a live stall-price screen.",
        ("quotes", "live", "live quotes", "end-of-day"),
    ),
    "json": Term(
        "Saved results / JSON",
        "A structured text file containing the full observations, rules, settings "
        "and results. It saves the complete test, not only the visible replay day.",
        "Instead of photographing one page of a toy-game scoreboard, save the "
        "whole notebook with its starting rules, purchases and scores.",
        ("export", "save results"),
    ),
    "portfolio": Term(
        "Basket / portfolio",
        "A group of investments sharing your money. "
        "Multi-stock baskets are planned, not implemented here yet.",
        "Split a play-money budget between toy cars, blocks and dolls rather than "
        "spending everything on cars. Different prices then affect the combined collection.",
        ("basket", "baskets", "allocation", "allocations"),
    ),
    "rebalance": Term(
        "Rebalance",
        "Change how the shared money is divided between holdings. This is a future basket feature.",
        "You want half your toy budget in cars and half in blocks. If cars rise "
        "in value, sell some cars and buy blocks to restore the halves, paying any costs.",
        ("rebalancing",),
    ),
    "ai": Term(
        "AI-proposed idea",
        "A rule suggested by a computer model, not proof of a useful strategy. "
        "No AI model is connected to this app today.",
        "A computer suggests buying toy cars after three price drops. "
        "That is an idea to test, not a promise that toy cars will become more valuable.",
        ("artificial intelligence", "hypothesis", "hypotheses"),
    ),
    "holdout": Term(
        "Untouched test history / holdout",
        "History kept out of the rule-building process and used later to check the chosen rule.",
        "Use one potato-price notebook to invent a rule. Seal a second notebook "
        "until the rule is fixed, then check it there. "
        "Do not keep changing the rule to fit the sealed notebook.",
        ("out-of-sample", "holdouts"),
    ),
    "walk-forward": Term(
        "Repeated later-period check / walk-forward",
        "Build a rule using one earlier period, test the next period, then move "
        "forward and repeat. It does not guarantee future success.",
        "Use January's toy prices to choose a rule and test February. "
        "Then use information available by February to choose the next rule and test March.",
        ("walk-forward tests", "walk forward"),
    ),
    "overfit": Term(
        "Fitting old luck / overfitting",
        "Tuning a rule so closely to old examples that it may not work on new ones.",
        "Try 1,000 silly toy-price rules and keep the luckiest. Its old score "
        "may look wonderful even if it cannot help with next week's prices.",
        ("multiple testing", "data snooping", "data-snooping", "overfitting"),
    ),
    "leverage": Term(
        "Borrowing to enlarge a position / leverage",
        "Using borrowed money to buy more than your own cash allows. This app does not do it.",
        "You have INR 100 but borrow another INR 100 to buy toys. "
        "A price fall now hits a larger holding, while the borrowed money still has to be repaid.",
        ("borrowing",),
    ),
    "short": Term(
        "Short selling",
        "Selling borrowed units in the hope of buying them back cheaper later. "
        "This app never does this; it only sells what it already owns.",
        "Borrow a toy, sell it for INR 100 and hope to buy it back for INR 80 "
        "before returning it. If it instead costs INR 150, you face a loss.",
        ("short", "shorts", "short selling"),
    ),
    "tax": Term(
        "Taxes and charges",
        "Extra charges that can apply to real trading. This app's simple cost "
        "settings are not a complete Indian tax and brokerage calculation.",
        "The sticker price of a toy might not include delivery and service charges. "
        "A practice estimate that misses those charges can look better than the real purchase.",
        ("taxes", "GST", "STT", "stamp duty", "broker"),
    ),
    "point-in-time": Term(
        "What was actually known then",
        "Historical prices downloaded today can contain later corrections or "
        "adjustments. Using only earlier rows does not prove "
        "those exact values were available then.",
        "Your toy-price notebook is corrected in December. Reading its January "
        "page now does not prove the corrected number was written there in January.",
        ("point-in-time", "look-ahead", "lookahead", "future leak"),
    ),
    "survivorship": Term(
        "Missing failed companies / survivorship bias",
        "A test can look too good if it includes only companies that still exist "
        "and leaves out companies that failed or stopped trading.",
        "Judge a toy-shop street using only shops still open today. "
        "Ignoring the shops that closed can make the street look safer than it was.",
        ("survivorship bias", "delisted", "delistings"),
    ),
}


def search_terms(query: str) -> list[str]:
    needle = query.strip().casefold()
    matches = [
        key
        for key, term in TERMS.items()
        if not needle
        or any(needle in word.casefold() for word in (key, term.title, *term.aliases))
        or needle in term.meaning.casefold()
    ]
    return sorted(
        matches,
        key=lambda key: (
            0
            if needle
            in (
                key.casefold(),
                TERMS[key].title.casefold(),
                *(alias.casefold() for alias in TERMS[key].aliases),
            )
            else 1,
            TERMS[key].title.casefold(),
        ),
    )


def term_html(key: str) -> str:
    term = TERMS[key]
    return (
        f'<h2 style="color:{WARM}">{escape(term.title)}</h2>'
        f"<p>{explain(term.meaning)}</p>"
        f'<h3 style="color:{ACCENT}">Imagine this</h3>'
        f"<p>{explain(term.example)}</p>"
    )


def tooltip(key: str) -> str:
    return f'<table width="370"><tr><td>{term_html(key)}</td></tr></table>'


_ALIASES = {
    alias.casefold(): key
    for key, term in TERMS.items()
    for alias in (key, term.title, *term.aliases)
}
_WORDS = re.compile(
    r"(?<!\w)("
    + "|".join(re.escape(word) for word in sorted(_ALIASES, key=len, reverse=True))
    + r")(?!\w)",
    re.IGNORECASE,
)


def explain(text: str) -> str:
    """Link known vocabulary without interpreting user/provider text as HTML."""
    parts = []
    previous = 0
    for match in _WORDS.finditer(text):
        parts.append(escape(text[previous : match.start()]))
        key = _ALIASES[match.group().casefold()]
        parts.append(
            f'<a style="color:{ACCENT};text-decoration:none" href="term:{key}">'
            f"{escape(match.group())}</a>"
        )
        previous = match.end()
    parts.append(escape(text[previous:]))
    return "".join(parts)


class HelpBrowser(QTextBrowser):
    term_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setOpenLinks(False)
        self.setOpenExternalLinks(False)
        self.highlighted.connect(self.show_term)
        self.anchorClicked.connect(self.follow_link)
        self.setAccessibleDescription(
            "Highlighted words have simple explanations and everyday examples. "
            "Hover for help; activate a link to open its dictionary entry."
        )

    def show_term(self, url: QUrl) -> None:
        key = url.path()
        if url.scheme() == "term" and key in TERMS:
            QToolTip.showText(QCursor.pos(), tooltip(key), self)
        else:
            QToolTip.hideText()

    def follow_link(self, url: QUrl) -> None:
        key = url.path()
        if url.scheme() == "term" and key in TERMS:
            self.term_selected.emit(key)
        elif url.scheme() in {"https", "http"}:
            QDesktopServices.openUrl(url)
