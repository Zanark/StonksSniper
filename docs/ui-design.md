# Learn first, then test

The product is a practice playground, not an expert terminal. Start with **load a
stock**, **pick an idea**, **test the idea**. Nothing requires knowing an acronym.
Each idea teaches when it buys, when it sells, what can fail and an everyday
analogy. Exact numbers and sources remain available separately.

## Explanation contract

`lessons.py` owns the seven authored lessons. `glossary.py` owns a shared dictionary:
plain-English meaning followed by an **Imagine this** example about toys,
vegetables or household items. Controls, hover links and the dictionary reuse
those entries. No model generates explanations at runtime.

Hover a highlighted word for a definition and example; activate the link to open
the dictionary. This works without a mouse through ordinary keyboard link
navigation: focus the explanation, press Tab to highlight a link, then Return.
**Explain pattern** opens the selected pattern's lesson. Search terms
and abbreviations in **Dictionary**; unmatched queries report the gap explicitly.
Everyday teaching examples are not stock observations and cannot feed the engine.

The scope is authored coverage, not a promise to understand every possible word
someone might type. New features must extend definitions/examples with their new
vocabulary. Human comprehension testing is separate from code checks.

## Technical evidence and remaining qualification

The current catalogue has seven explained rules and 74 authored dictionary
entries. Native hover and Tab/Return navigation, all seven rule-chart prefixes,
drawing-window invariance and motion-off behavior are covered by regression
checks. The final suite has 47 passing tests; lint, formatting and strict typing
also pass. Detailed failures and fixes are retained in `development.md`.

The original six screenshots remain in `images` with their receipt at
`images/captures.json`. README now uses five native GIF demos of retrieved
RELIANCE.NS history, lessons and Dictionary; `images/gif-captures.json` records
their exact cutoff and actions. They are sampled real widget states, not
dashboard mockups or real-time recordings. Each GIF has a concise README caption.
The main workspace fits at 1440x900 and 1366x768; long explanations remain
scrollable within their panels.

These are technical/visual checks, not demonstrated comprehension by a teenager,
normal Windows/DPI qualification, an installer test or independent price
reconciliation. Those remain explicit follow-up work.

## Visual decisions and source receipts

| Source inspected | Applied decision |
|---|---|
| [DeepSeaFoam canonical palette](https://github.com/Zanark/DeepSeaFoam/blob/main/palette/deepseafoam.json) and palette role documentation | Near-black teal workspace `#000F13`, panels `#001E26`, seafoam actions `#00A591`, warm headings `#EEE8D5`, muted sea-slate text. Original native mapping, not a copied showcase. |
| [Material 3 color roles](https://m3.material.io/styles/color/roles) | Assign colors by semantic role. The retrieved page exposed its metadata, not its complete JS-rendered guidance; this is inspiration, not a claim of full Material 3 compliance. |
| [Material 2 data visualization](https://m2.material.io/design/communication/data-visualization/) | A focused chart at a time, clear labels and honest comparisons. Search returned visualization principles; direct retrieval exposed a JS shell, not a fully inspected specification. |
| [Qt QChart](https://doc.qt.io/qt-6/qchart-qtcharts.html) | Short series-only transitions; never animated axis ranges. No recurring animation is needed to read data. |
| [Qt QChartView](https://doc.qt.io/qt-6/qchartview-qtcharts.html) | Keep native widget charts rather than replace the application with an unrelated browser UI. |
| [Qt QAreaSeries](https://doc.qt.io/qt-6/qareaseries-qtcharts.html) | Light area emphasis on money/falls charts; preserve explicit axis ranges and boundary-line lifetime. |
| [W3C animation from interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) | Offer an explicit motion control. This web accessibility guidance informs the native app; no WCAG certification or automatic OS-preference integration is claimed. |

These are source receipts and implementation choices, not user approval.
DeepSeaFoam notices and origin attribution ship in
`src\stonks_sniper\assets\DEEPSEAFOAM-NOTICE.txt`.
The original StonksSniper logo contains no third-party artwork or icons.

### Square surfaces, circular brand

Rectangular GUI elements use square corners consistently, including chart
backgrounds and controls. The animated logo begins as a square chart whose side
equals the final circle's outer diameter, including its border. The
reticle makes erratic, seeded jumps across all quadrants, settles in the center
and fires a visible bullet with a tracer and impact flash. It then cuts to a
circle with transparent surroundings, not a circle painted onto a square tile.
Its original green/coral candles are decorative illustrations, not observations.
The header uses the GIF, while the window/taskbar icon uses the centered still
SVG. Disabling **Animations** pauses the movie and shows that centered still;
reenabling restores the movie. Closing the window stops it.

The README has a separate gold-and-green banner and linked, square image buttons.
Its logo displays at 352px, four times the original 88px width. The application
keeps DeepSeaFoam rather than inheriting the README's promotional palette.
Detailed setup and explanations live in the linked written guides. GitHub's GIF
player has no application-controlled pause switch; the guide and still logo
provide a no-motion route, not a claim of automatic reduced-motion detection.

## Compact without hiding the truth

Four small results cards summarize money now, gain/loss, biggest fall and trades.
One chart shows price, money, falls or the numbers behind the selected rule.
Price can be a simple line or candles; shape and line style supplement color.
The default 90-day drawing window reduces clutter without changing the test.

The main page does not scroll. Longer explanations, trade history and data
details use focused panels; the lesson and dictionary pages show one entry at a
time instead of concatenating an entire manual. Long content can still scroll
inside its panel. A compact identity line keeps the actual stock, source status
and latest date visible; full provenance stays in **Data**.

Replay rebuilds only the visible observation prefix. Drawing a shorter window
does not reset the running high or change results. Playback starts only when
requested and stops on navigation, invalidation, new fetch, close or motion off.
Replay changes use immediate chart updates rather than repeated transitions.

Qt's current documentation marks Qt Charts deprecated. This redesign preserves
the existing widget architecture; a future Qt Graphs migration needs its own
compatibility and packaging work, not an unannounced framework switch.
