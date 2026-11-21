# Read The Intelligent Investor with Stonks Sniper

[Guide](guide.md) | [27 technical strategies](strategies.md) | [Run source](getting-started.md)

**Latest source only: this companion is not in the published v0.3.0 EXE.**

Open **Learn the patterns**. Its two sections are **Internet technical strategies**
and **The Intelligent Investor**. The first retains the 27 price-based experiments.
The second contains original ELI15 reading notes for the 20 main chapters,
a fundamental stock workbook, and portfolio/inflation arithmetic exercises.
**Explain pattern** still opens the selected technical lesson, not a book method.

## What this companion covers

This is an independent companion, not the book, an authorised adaptation, or a
claim to reproduce every concept/example/appendix across all editions. Keep your
own copy alongside it. The chapter map follows Graham's revised text; page
numbers vary. The publisher describes the 2024 edition as retaining Graham's
text with newly updated Jason Zweig commentary. The app does not label modern
Indian adaptations or later commentary as Graham's original words.

Each chapter has an original plain-English explanation, a clearly illustrative
example, an Indian-market research task, limitations and source links.
Principles and historical case discussions are **not all buy/sell algorithms**.
There is deliberately no invented daily signal for temperament, fund selection,
adviser diligence, accounting quality or shareholder governance.

| Chapter | Reading topic and practical support |
|---|---|
| 1 | Investing versus speculation; defensive versus enterprising effort. Write a business thesis and what would disprove it. Technical success alone is not fundamental analysis. |
| 2 | Inflation and purchasing power. Calculate real return; compare taxes and risks separately. Shares are not a guaranteed inflation hedge. |
| 3 | Market history and changing valuation levels. Inspect different dates and drawdowns rather than treating recent growth as a forecast. |
| 4 | Defensive allocation, high-quality fixed income and rebalancing. Calculate a transfer back to your chosen target; historical 50/50 and 25%-75% examples are not personal advice. |
| 5 | Established companies, diversification and regular equal-money purchases. Calculate rupee-cost averaging; stock count does not eliminate correlated losses. |
| 6 | Enterprising exclusions: weak credit, unsuitable preferred shares, promotional new issues and unfamiliar foreign instruments. Read local offer documents and claims ranking. |
| 7 | Neglected companies, bargains, net current assets and special situations. Calculate a net-net threshold; event arbitrage and asset recoverability need separate investigation. |
| 8 | Mr. Market, price versus business value and emotional discipline. Compare the quote with an independently reasoned value range; do not buy every dip. |
| 9 | Investment funds, expenses, incentives, portfolio risk and performance chasing. Compare Indian scheme documents and benchmarks; no automatic fund ranking. |
| 10 | Advisers and conflicts of interest. Check applicable SEBI registration, fees, custody and written scope using current official records. |
| 11 | Security analysis: financial strength, earning power, bond servicing and valuation uncertainty. Compare earnings yield and a separately researched bond benchmark without equating their risks. |
| 12 | Per-share earnings, exceptional items, multi-year averaging and dilution. Average three annual diluted EPS values; inspect notes and cash flow separately. |
| 13 | Multi-factor company comparison. Repeat the same dated workbook for comparable Indian companies; no single-ratio winner or fabricated Indian equivalent of a historical US company. |
| 14 | Defensive stock selection: size, strength, earnings, dividends, growth and price. Inspect individual evidence checks, including explicit Unknown results. |
| 15 | Enterprising industrial selection: liquidity, debt, no-loss history, current dividends, growth and cheap tangible assets. Explicitly disclosed rolling-year adaptation. |
| 16 | Convertibles, warrants, contractual options and dilution. Read conversion/expiry/seniority terms and compare conversion value; no convertible pricing engine. |
| 17 | Historical failures and financial warning signs. Investigate leverage, aggressive accounting, acquisitions, cash conversion and auditor qualifications; no automated fraud verdict. |
| 18 | Paired comparisons: business quality versus price. Compare sector peers on a common accounting/date basis; cheap does not automatically mean good. |
| 19 | Shareholder oversight, retained profits, dividends and capital allocation. Calculate yield and payout, then read cash-flow/governance evidence. |
| 20 | Margin of safety, diversification and uncertainty. Calculate the discount to your own assumed value and inspect the historical price-ratio bound without calling it proven intrinsic value. |

Introductions, appendixes, Zweig's edition-specific commentary, the postscript's
individual investment account and the detailed historical company narratives
are reading references, not an asserted exhaustive digitisation. The 20-chapter
inventory is bounded coverage, not a claim that every paragraph has an algorithm.

## Apply a concept to an Indian company

1. In **Fundamental workbook**, type an NSE/BSE ticker, or click
   **Use Explore stock** to copy it. Copying/changing the stock clears this
   workbook's old figures and results; it does not alter Explore or an open Simulate.
2. Click **Fetch latest reference**, or enter dated figures from annual reports.
   The fetch works independently of whether the exchange is open.
3. Review the quote date, statement period ends, currency, sector and per-input
   source. Most inputs may remain blank. Blank means **unknown**, never zero.
4. For manually supplied/edited figures, enter a report/URL/page in
   **Manual evidence/source** and its as-of date. Explicitly label a hypothetical
   scenario as such. The app records your evidence but cannot independently audit it.
5. Only after verifying an ordinary non-financial industrial company, select
   **Non-financial industrial** to enable the industrial checklists. Banks,
   insurers, utilities and unclassified companies do not receive those ratings.
6. Click **Calculate / check evidence**. Inspect formulas and inputs, not an
   overall score: there is intentionally **no overall buy/sell verdict**.
   **Save worksheet HTML** preserves the displayed inputs, sources, warnings
   and individual results. An input/date/classification change invalidates the
   old result and disables saving until you recalculate.

Numbers must be finite, no larger than 1e15 in magnitude, and any nonzero
workbook magnitude must be at least 1e-12. Unsupported ranges, zero denominators,
invalid years/percentages and scenario overflow fail explicitly, not as infinite
or stale successful outputs.

### Real reference data, not a manufactured complete database

The optional Yahoo/yfinance snapshot imports a recent prior completed daily
**unadjusted Close**, available annual diluted EPS, book value, separate TTM
EPS and available annual balance-sheet/revenue fields. Statement totals are
converted from INR to **INR crore**; ordinary share count is converted to
**crore shares**. Their quotient is INR/share. The per-input statement end date
is retained. Three EPS periods must be annual/consecutive to be imported
together; sparse or nonfinite observations stay unavailable with disclosures.

The snapshot requires the correct quote exchange/INR currency. Financial
amounts are imported only when Yahoo identifies the statement currency as INR.
Foreign/unknown statement currency leaves financial fields unavailable with
an explicit warning; no FX rate or zero is invented. A quote without a usable
prior completed Close, invalid identity or failed request produces an error.

Missing current assets, preferred claims, tangible book and long dividend/
earnings histories are **not inferred**. Preferred stock's balance-sheet
carrying amount is not silently treated as its liquidation preference.
The user must verify claims and provide the relevant figure, including an
explicit zero only when absence is established.

TTM EPS and book value supplied in quote metadata have unverified period ends;
they are labelled accordingly, not relabelled as annual report facts.
Fetch time is **not the original publication time** of a statement.
Yahoo can split-adjust even an unadjusted Close; old EPS, share counts and
newer book values require a consistent corporate-action basis. Consolidation
scope and restatements need human review.

**Do not use these present-day fundamentals in historical Simulate.**
That would pretend you knew later financial results earlier. The workbook is
deliberately disconnected from the daily strategy/accounting engine.

## Calculations and exact boundaries

### Valuation and margin

`E = (EPS latest annual + EPS prior annual + EPS third annual) / 3`.
Loss years remain in that average; averaging is not adjustment for exceptional items.
The earnings multiple is `price / E`, with `E` the three-year mean defined
above. `P/B = price / book value per share`.
Earnings yield is `100 * E / P`; it is not guaranteed interest or a dividend.

The popular **Graham number**, implemented as a historical price-ratio bound,
is `sqrt(22.5 * E * book/share)`, from `15 * 1.5 = 22.5`.
It requires positive mean earnings and positive book value. Multiplying two
negative inputs must not manufacture a positive valuation. A low price against
this bound does not establish a good business, complete screen or true value.

For **your** assumed positive value `V`:

- Discount to value: `100 * (V - P) / V`.
- Rise needed to reach value: `100 * (V/P - 1)`; a different denominator.
- Maximum price under your required discount `d`: `V * (1 - d/100)`.

Illustration only: `V=200`, `P=140`, `d=30%` gives 30% discount, 42.8571%
rise to value and an assumed maximum price of INR 140. This is not an ICICIBANK
valuation. The app supplies neither an intrinsic-value forecast nor a universally
safe discount. No arbitrary percentage is attributed to Graham.

`EPS * (8.5 + 2g)` and later yield-adjusted variants are **not implemented as
buy-price calculators**. Public interpretations differ and warnings are often
omitted. A guessed growth rate must not become an authoritative target.

### Defensive industrial checklist

The workbook reports each check separately, not a weighted score.

| Check | Implemented comparison |
|---|---|
| Size | Annual INR crore sales >= a user-chosen INR crore floor; explicitly an Indian adaptation. |
| Current strength | Positive current liabilities; current assets >= 2 x current liabilities. |
| Debt cushion | Working capital = current assets - current liabilities; nonnegative working capital and long-term debt <= working capital. |
| Earnings | At least 10 consecutive **positive** annual EPS years, ending in the latest fiscal year; manually verified. |
| Dividends | At least 20 uninterrupted dividend years; manually verified. |
| Growth | Latest three-year EPS mean >= 4/3 x a comparable three-year mean a decade earlier; old mean must be positive. |
| Earnings price guide | Positive three-year EPS mean and P/E <= 15. |
| Book/earnings price guide | Positive mean EPS/book value, and P/B <= 1.5 **or** P/E x P/B <= 22.5. Inspect the separate P/E result as well. |

Financial strength has two subchecks, so the historical seven categories
produce eight displayed findings. Original size examples of USD 100m
industrial sales / USD 50m utility assets are historical, **not present-day INR
cutoffs**. No automatic FX/inflation conversion is asserted. The app has no
utility-specific substitute and no bank/insurance pass/fail screen.

AAII describes modified P/E/product/history thresholds for its own database.
This workbook does **not** silently adopt its 20/30 multiples or shorten
10/20-year history to the few years Yahoo happens to supply.

### Enterprising industrial research checklist

Current assets >= 1.5 x positive current liabilities; total debt <= 1.1 x
nonnegative working capital; five consecutive annual periods with no loss;
some verified current annual dividend; latest annual EPS above a manually
provided five-year-ago EPS; price <= 10 x positive TTM EPS; and price strictly
below 1.2 x positive tangible book/share.

These are displayed research filters, not an assertion that the chapter
defines one universal modern grading system. Sources differ in implementations
of debt, the low-P/E starting universe and price constraints. The app uses
**total interest-bearing debt**, not just long-term debt, in this checklist;
both the P/E and tangible-book checks are visible rather than silently
substituting one for the other. The rolling five-year comparison is an
explicit adaptation of the chapter's named historical comparison year.
The defensive checklist instead uses long-term debt, as labelled.

### Net-net

`NCAV/share = (current assets - ALL liabilities - preferred claims) / ordinary shares`.
Only positive NCAV can pass `P <= (2/3) * NCAV/share`. Current liabilities
alone or interest-bearing debt alone are **not** sufficient deductions.
The worksheet requires preferred claims explicitly; missing does not equal zero.
This industrial asset test is disabled for other classifications.

Illustration: INR 1,000 crore current assets, INR 600 crore total liabilities,
INR 100 crore preferred claims and 10 crore shares produce INR 30/share NCAV
and an INR 20 two-thirds threshold. Assets may be overstated or difficult to
recover; this is not guaranteed liquidation cash.

### Dividends, inflation and portfolio exercises

Dividend yield is `100 * annual dividend/share / price`; payout is
`100 * annual dividend/share / latest annual EPS` when EPS is positive.
No forward indicated dividend is silently imported as a realised payment.

Real purchasing-power return is
`100 * [(1 + nominal/100)/(1 + inflation/100) - 1]`.
Return/inflation must exceed -100%. For 8% and 6%, the result is 1.8868%.

Allocation transfer to shares is
`(shares value + fixed-income value) * target_shares_pct/100 - shares value`.
For INR 60,000/40,000 and a 50% target, it is -INR 10,000.
These are user-chosen scenarios, not actual portfolio rebalancing or bond prices.

For equal money `A` at each supplied price, units are `sum(A/price)` and
average cost is `(A * number of purchases)/units`. INR 1,000 at 100 and 50
produces 30 illustrative units at an average INR 66.6667, not INR 75.
There is no profit calculation without a sale/final value, and no promise of profit.

## Research receipts and source roles

Public research performed 21 November 2026. These are references, not endorsements.
No full book text, downloaded book PDF, illustrations or proprietary tables are bundled.
The application text is original; equations and historical thresholds are explained
with explicit attribution and limitations.

| Source | Role and access boundary |
|---|---|
| [Publisher description via Google Books](https://books.google.com/books?id=VwvyEAAAQBAJ) | Read: 2024 edition, unchanged Graham text/new Zweig commentary. Not evidence of reading the complete book. |
| [Perlego licensed catalogue](https://www.perlego.com/book/4332826/the-intelligent-investor-third-edition-the-definitive-book-on-value-investing-pdf) | Read public description and full chapter inventory, not subscription book text. |
| [Investopedia: Graham principles](https://www.investopedia.com/articles/basics/07/grahamprinciples.asp) | Read: investor/speculator, active/defensive effort, margin, regular purchases, allocation. Modern interpretation is not primary book text. |
| [Investopedia: Mr. Market](https://www.investopedia.com/terms/m/mr-market.asp) | Read: behavioural allegory and Chapter 8 association. |
| [Investopedia: Graham number](https://www.investopedia.com/terms/g/graham-number.asp) | Read: three-year EPS, 15/1.5/22.5 algebra, limits. The app avoids the article's stronger intrinsic-value/prediction claims. |
| [Investopedia: NCAV](https://www.investopedia.com/terms/n/ncavps.asp) | Read: all liabilities, preferred claims and two-thirds threshold. The app uses explicit parentheses to avoid ambiguous inline typesetting and does not call book assets guaranteed recovery. |
| [Investopedia: margin of safety](https://www.investopedia.com/terms/m/marginofsafety.asp) | Read: discount to estimated value and estimation uncertainty; no guaranteed protection. |
| [GrahamValue: quick reference](https://www.grahamvalue.com/quick-reference) | Relevant indexed search excerpts reviewed for historical defensive/enterprising criteria; direct page returned 403. Third-party interpretation, not a complete primary-text review. |
| [AAII: defensive/enterprising approach](https://www.aaii.com/journal/article/graham-s-long-term-winning-approach-for-enterprising-defensive-investors) | Indexed excerpts reviewed: original and explicitly modified histories/multiples. Its modifications are not silently attributed to Graham. |
| [GrahamValue: growth formula warning](https://www.grahamvalue.com/article/understanding-benjamin-graham-formula-correctly) | Indexed excerpts reviewed: cautions and disagreement about operational use. Reason not to present a growth guess as verified value. |
| [SEBI: understanding investment advisers](https://investor.sebi.gov.in/investment_advisor.html) | Read: current Indian adviser/fee/registration education, explicitly a local application, not Graham text. |

The public CFI value-investing guide was also read as a cross-check; it mixes
multiple formulations and adaptations and is **not** the canonical Chapter 14
checklist here. A generic third-party chapter guide was inspected but its
bank-working-capital example was not adopted. Disagreeing online summaries
are a reason to disclose scope, not invent one perfectly authoritative screen.

## Closed-market evidence

The history adapter has no market-open gate. In a real Saturday request on
**21 November 2026 at 19:57 IST**, `ICICIBANK.NS` returned **496** completed
observations from 21 November 2024 through **20 November 2026**. An independent
actual fundamental request at 20:00 IST also returned the 20 November Close
and dated available fundamentals. These are historical verification receipts,
not a promise that Yahoo is always available or independently reconciled.
An additional actual Yahoo quote-state check at **20:11 IST** explicitly
returned `marketState: CLOSED` for `ICICIBANK.NS`.

Saturday/Sunday, a holiday-style missing-session range, after-hours exclusion
and preservation of a supplied special Sunday session have deterministic
regressions. A fixture is not a live exchange-calendar check. Even after close,
**today's candle remains conservatively excluded**. A request ending on an
older date remains confined to that date range; missing days are not filled.
