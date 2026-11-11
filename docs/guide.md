# Understand StonksSniper

[Back to the GIF tour](../README.md) | [Run the app](getting-started.md)

**Learn a stock-market idea. Understand every word. Try it with practice money.**

StonksSniper is a local Windows learning app with actual Indian stock history,
seven explained buy/sell rules and a compact DeepSeaFoam interface. No previous
market knowledge is assumed.

## Start without the jargon

A **share** is a small piece of ownership in a business. Imagine a toy shop split
into 100 ownership tickets: one ticket represents one small piece of that shop.
A **pattern** is a rule to test, not a promise. Imagine buying toy cars after
their price starts rising, then checking whether that rule actually helped.

**Explain pattern** teaches when a rule buys, when it sells, what can go wrong
and an example using toys, vegetables or household items. Hover a highlighted
word for its meaning and example; click it for **Dictionary**. Keyboard users
can focus the explanation, press Tab to highlight a link and Return to open it.
Search accepts names or abbreviations and reports missing explanations rather
than inventing them.

## Read the charts

**Stock price** shows what happened to the price. A candle is one day's four
prices: opening, highest, lowest and closing. Imagine a tomato stall writing its
first, highest, lowest and last price on one daily card.

**Your money** compares following the rule with buying once and waiting.
**Falls from high** shows how far practice money dropped from its earlier best.
Imagine your toy collection once being worth 100 tokens and later 80: that is
a fall of 20 tokens, even if you originally paid only 50.

**See the rule** exposes the actual measurements behind its decisions.
**Play days** reveals history in order without revealing future trades.
The drawing window changes only what is shown, never the underlying experiment.

## Actual history, clear boundaries

The initial connection uses free, unofficial Yahoo completed daily history:
**not live prices**. No API token is required. Unavailable data produces an
explicit error, never made-up observations.

Older prices are rescaled for changes to shares and payments to owners. These
research quantities are not literal historical share purchases. Later downloads
can revise older values. The **Data** panel preserves source and timing.

Decisions use a finished day; practice trades happen at the next available
opening price with chosen costs. No broker or real-money trading is connected.
Seven rules work today. Additional patterns, baskets of stocks and AI-proposed
ideas remain planned, not implemented.

## About the moving pictures

The logo is original decorative artwork: the reticle darts across a rectangular
chart, settles on the center candle and fires a visible bullet. After the impact,
the picture cuts to a circle with a transparent outside. The still logo keeps the
reticle centered; turning off **Animations** shows that still in the app header.
Its candles are **not market observations or a recommendation**.

The five GUI GIFs are actual native-window captures using downloaded RELIANCE.NS
history, not dashboard mockups. Price/money/rule demos advance the actual replay
cursor through the final 60 completed sessions; lesson/dictionary demos navigate
authored content. Frames are sampled and encoded into loops, not real-time
screen recordings. [Capture dates, source and actions](images/gif-captures.json).
The app's own motion switch does not control GitHub's GIF playback.

The app keeps its square-cornered DeepSeaFoam theme. Gold-and-green artwork is
for README navigation and the shared circular brand, not a silent app recolor.

## Go deeper

- [Exact product, simulator and architecture](product-and-architecture.md)
- [Data providers and qualification gaps](data-providers.md)
- [Design and explanation contract](ui-design.md)
- [Development, media reproduction and verification](development.md)
- [Numbered roadmap](../TODO/00_INDEX.todo)
- [GitHub Project](https://github.com/users/Zanark/projects/14)

For education and simulation only; not investment advice or a guarantee of results.
