# Understand StonksSniper

[Back to the GIF tour](../README.md) | [Run the app](getting-started.md)

**Learn a stock-market idea. Understand every word. Try it with practice money.**

StonksSniper is a local Windows learning app with actual Indian stock history,
27 explained buy/sell rules and a compact DeepSeaFoam interface. No previous
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

## Simulate your own dates

In the latest source, **Simulate** sits beside **Test idea**. Load a stock and
choose an idea, starting money and trading costs, then click **Simulate** to open
a separate window. Choose a **Start date** and **End date**, then
**Start simulation**.

The window reveals one trading day at a time: green circles mark buys, red
squares mark sells, and the table lists the trades that have happened so far.
Switch between **Stock price + trades** and **Your money** to watch the price
and your cash-plus-stock value. **Pause**, **Next day** and the time slider let
you inspect a moment; **Show final result** skips to the end. **Play** after the
finish replays the same experiment from its first day.

The final cards show how much money remains, the profit or loss in INR and its
percentage of the starting money. For example, starting with INR 1,000 and ending
with INR 1,100 means INR 100 profit, or 10%. This example illustrates the
arithmetic; it is not a market result.

Important boundaries:

- Both dates are included, using only observations already loaded. Load a wider
  date range in **Explore** first if you need other dates. Missing days are not filled.
- Each run starts in cash. The idea warms up using days **inside** your selected
  interval; nothing is bought before the start. Too-short, reversed or empty
  intervals show an error instead of reusing an earlier result.
- Buys and sells use the next available opening price, including your fee and
  worse-price settings. A signal on the final day cannot trade without a next day.
- Stock still owned at the end is valued at the final close, **not automatically
  sold**. Its gain or loss is included in the total but is not cash earned yet;
  hypothetical exit costs and a complete tax model are not included.
- Changing dates clears the old run. Changes in the main window do not replace
  the simulation's captured stock, idea, history or costs. Main-window
  **Save results** still exports the main experiment, not this separate run.
- Turning off **Animations** pauses simulation playback too; stepping and
  skipping to the final result still work.

This feature is in the latest source, **not** the already-published v0.2.0 EXE.

## Actual history, clear boundaries

The initial connection uses free, unofficial Yahoo completed daily history:
**not live prices**. No API token is required. Unavailable data produces an
explicit error, never made-up observations.

Older prices are rescaled for changes to shares and payments to owners. These
research quantities are not literal historical share purchases. Later downloads
can revise older values. The **Data** panel preserves source and timing.

Decisions use a finished day; practice trades happen at the next available
opening price with chosen costs. No broker or real-money trading is connected.
[All 27 implemented strategies](strategies.md) have a complete reference:
ELI15 ideas, exact buy/sell/hold conditions, formulas, warmups, examples,
limitations and sources for the original seven and the 20 additions.
Broader pattern families, baskets of stocks and AI-proposed ideas remain planned.

## About the moving pictures

The logo is original decorative artwork: the reticle darts across a clear square
chart without glass reflections or an optical rim.
The fixed-palette GIF avoids broad gradient fills that hide the grid or candles.
It settles on the center candle and fires a visible bullet. After
the impact, the corners smoothly round away over 2.56 seconds, leaving a circle
with a transparent outside. Only the completed circle reveals the glass,
thin curved reflections and layered rim, followed by one 1.2-second shimmer
sweeping across the lens and a still finish. The full loop remains 9.08 seconds.
That transition is 1.5x faster than the earlier
3.84-second version; the search and shot keep their original pace.
It starts and finishes gently, without shrinking. The still logo keeps the
reticle centered. The app header always shows that still, even with **Animations**
enabled; the search-and-shot animation is for the README.
This phase change and shimmer apply only to the GIF. The unchanged static glass
artwork supplies the README cover and native app/window
icons, rendered at seven sizes from 16 to 256px. The
[Windows/browser ICO](../src/stonks_sniper/assets/logo.ico) contains those same
sizes. This is a native app, not a hosted website: the ICO is favicon-ready,
but a README cannot replace GitHub's own browser favicon.
An already running app must be relaunched to load the updated icon; no existing
user window is restarted by the asset builder.
The square's side matches the circle's diameter, so the logo does not change size.
Its candles are **not market observations or a recommendation**.

The five GUI GIFs are actual native-window captures using downloaded RELIANCE.NS
history, not dashboard mockups. Price/money/rule demos advance the actual replay
cursor through the final 60 completed sessions; lesson/dictionary demos navigate
authored content. Frames are sampled and encoded into loops, not real-time
screen recordings. [Capture dates, source and actions](images/gif-captures.json).
The app's own motion switch does not control GitHub's GIF playback.

The README artwork and shared logo use the requested dark graph-paper palette:
soft green/blue outlines, white titles and grey supporting text, with no gold.
Red/green candle colors are allowed. The app keeps its square-cornered DeepSeaFoam
interface and always-static header.

## Go deeper

- [Exact product, simulator and architecture](product-and-architecture.md)
- [All 27 buy/sell strategies with ELI15 examples, exact rules and sources](strategies.md)
- [Data providers and qualification gaps](data-providers.md)
- [Design and explanation contract](ui-design.md)
- [Development, media reproduction and verification](development.md)
- [Numbered roadmap](../TODO/00_INDEX.todo)
- [GitHub Project](https://github.com/users/Zanark/projects/14)

For education and simulation only; not investment advice or a guarantee of results.
