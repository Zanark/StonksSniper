---
name: stonks-sniper-lab
description: Teach Indian-stock strategies and run reproducible Stonks Sniper simulations for hypothetical capital using real completed NSE/BSE history. Use for backtest, paper trading, simulated profit/loss, compare strategies, explain a trade, learn an indicator, test an agent-proposed algorithm, or Intelligent Investor practicals. Supports 27 built-in rules and validated custom JSON rules. No broker orders or profit guarantees.
---

# Stonks Sniper: agent and human research lab

## Mission and non-negotiable boundaries

Help a learner answer: "With this hypothetical starting capital, stock, interval,
rule and costs, what would this exact simulation have done, and why?"

Use the running tool, not invented prices, remembered quotes, guessed trade dates
or an LLM's arithmetic as a substitute for execution. Report **losses, no trades,
drawdowns and underperformance** as readily as profits. A real historical example
demonstrates rule application, NOT that the rule reliably works or predicts tomorrow.
Past returns, especially a selected winner, are not a profit promise.

This skill supplies the LLM teaching/research layer; it does not embed an LLM in
the application. Agents can explain new questions, translate an idea into a
testable rule, run the lab and critique the evidence. Humans can use the native
lessons/replay and read the same receipts. No broker, account credential, real
order, autonomous investment mandate, paid feed or deployment is authorised.

The latest source contains the lab and learning demos. The older v0.3.0 EXE does
not; do not claim these features are present in that download.

## Find the actual checkout and Python

Locate the StonksSniper checkout; verify its `pyproject.toml` identifies
`stonks-sniper` and `src\stonks_sniper\lab.py` exists. Do not execute a similarly
named unrelated project. The installed skill may be invoked from another folder:
its own folder is `.github\skills\stonks-sniper-lab`, not the project root.

On the established Windows checkout:

```powershell
$Repo = 'C:\devdesk\homedesk\StonksSniper'
$Python = "$Repo\.venv\Scripts\python.exe"
& $Python -m stonks_sniper.lab --help
& $Python -m stonks_sniper.lab catalogue
```

For another clone, replace `$Repo` with its verified absolute path and use its
existing Python environment. On other platforms use that environment's Python
with the same `-m stonks_sniper.lab` arguments; JSON formats do not change.
No GUI/display is needed for the lab. If dependencies are missing, follow the
repository's getting-started guide; do not mutate a shared environment blindly.

Use a private/session artifact directory outside the tracked source for downloaded
history, authored hypotheses and reports. Choose one immutable filename per run.
The lab **refuses to overwrite** an existing output. Do not commit raw downloaded
market history, private prompts, credentials or personal portfolio information.

This is a repository skill in a Copilot-discovered `.github\skills` directory.
Other agents can read this Markdown and run the documented Python interface;
their own skill discovery/installation may differ. No agent is launched by it.

## Establish the experiment before looking for a winner

Capture the stock/exchange, hypothetical INR capital, interval, exact strategy,
fee and slippage assumptions, and learning question. If the user gave capital,
use it exactly. If something essential is absent, ask or explicitly label an
illustrative assumption; never imply the user supplied it.

Treat all capital here as hypothetical. Fractional **adjusted research units**
are not a purchasable real-share count. NSE tickers normally use `.NS` and BSE
`.BO`; ticker and selected exchange must agree. Verify ambiguous BSE identifiers
instead of substituting a company. Financial/bank fundamentals have different
sector rules; price-indicator experiments do not establish fundamental suitability.

Before tuning, reserve a later interval as holdout and write a falsifiable idea:
"This trend rule may lag in reversals and lose repeatedly in a sideways market."
Do not silently run many alternatives and present only the best. Keep an
experiment log including failed candidates and the number of variants tried.

## Fetch once, preserve the observations

Example dates below are an explicit historical study, not "latest" placeholders:

```powershell
$Runs = Join-Path $env:TEMP ('stonks-lab-' + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $Runs | Out-Null
& $Python -m stonks_sniper.lab fetch `
  --symbol ICICIBANK --exchange NSE `
  --start 2024-01-01 --end 2026-11-20 `
  --output "$Runs\icicibank-history.json"
if ($LASTEXITCODE -ne 0) { throw 'History fetch failed; do not simulate substitute data.' }
```

Inspect the JSON response: absolute output path, SHA256, actual first/latest
session, count and warnings. Requested dates and returned dates can differ.
Provider errors are real failures, not permission to invent data, use a stale
result without labelling it, change ticker or keep retrying aggressively.

Yahoo/yfinance is unofficial and availability/accuracy is not guaranteed. A
market-open connection is not required: weekends/holidays return actual available
prior observations. Today's bar is excluded even after the exchange closes.
No weekend fill or assumed Friday is inserted. Valid supplied special weekend
sessions are preserved. Missing entire OHLC rows are dated exclusions; partly
corrupt observations fail. Completeness and cross-provider agreement are not proven.

Yahoo split/dividend-adjusted OHLC is a total-return research proxy and can be
revised. Do not add cash dividends again. Preserve the fetched snapshot: rerunning
on the saved file is reproducible with the same code; downloading again can change
old signals. A SHA256 proves file identity, NOT that data/provenance is authentic.
Imported files are unverified inputs; never rename illustrative fixtures as real.

## Run a built-in algorithm with the given capital

```powershell
& $Python -m stonks_sniper.lab simulate `
  --input "$Runs\icicibank-history.json" --strategy sma `
  --capital 100000 --fee-bps 10 --slippage-bps 10 `
  --output "$Runs\sma-full-history.json"
if ($LASTEXITCODE -ne 0) { throw 'Simulation failed; no result may be reported.' }
```

Replace `100000` with the user's hypothetical capital. `10` basis points means
0.10% of traded value, not INR 10 or 10%. Fees and adverse slippage apply on both
entry and exit. Defaults are 10 bps each, not a broker-specific complete cost model.
There is no complete Indian tax/STT/DP-charge model.

The command prints a compact JSON receipt/summary. The saved JSON includes exact
observations, full strategy/assumptions, target per day, trades, money curve,
buy-and-hold curve, drawdown, input hash and any custom rule/hash. Keep this file.

Execution contract:

1. Start in cash. Warm up **inside** the chosen interval; no inherited position.
2. Read completed session `t`; request the target.
3. Execute a change only at the next available session's opening, with adverse
   slippage and a fee. Never fill at an earlier open or the signal close.
4. Hold stock or cash; no shorts, leverage, intraday stops or repeated buys while
   the target stays long. A final-day target without a next bar does not execute.
5. Mark remaining units at the last close. Unsold gain/loss is not realised cash.
   The end does not force a sale or charge a nonexistent exit fee.
6. The reference buys once after that strategy's declared warmup and holds, paying
   entry costs. Different warmups have different benchmark starts; do not interpret
   their raw benchmark percentages as a perfectly matched strategy ranking.

## Discover and choose among all 27 built-ins

`catalogue` is the authoritative machine-readable inventory, including full
rules, minimum observations, source, limitations and the ELI15 lesson.
Read it rather than inferring a formula from a name.

| Family | Keys and teaching question |
|---|---|
| Moving trends | `sma`, `ema`: are short averages above longer averages? |
| Momentum | `macd`, `roc`, `tsi`, `trix`: is recent movement stronger than the rule's reference? |
| Range/bounce | `rsi`, `stochastic`, `bollinger`: does weakness trigger this variant, and when does it leave? |
| Range strength | `williams`, `cci`, `aroon`: is position/movement strong by the exact rule? |
| Breakouts | `donchian`, `keltner`, `bollinger-breakout`: has price exceeded the specified band? |
| Direction/volatility | `adx`, `ichimoku`, `chandelier`, `vortex`: what direction/filter/trailing state does this implementation require? |
| Volume-linked | `obv`, `cmf`, `mfi`, `chaikin`, `emv`, `force`: what does this rule infer from price and reported volume? |
| Mixed oscillator / candles | `ultimate`, `engulfing`: inspect the exact formula or adjacent bodies, not the name alone. |

Verify these keys against the current catalogue before executing: code is
authoritative if this guide and a future catalogue diverge. Full definitions:
`docs\strategies.md`; lessons: `src\stonks_sniper\lessons.py`.
Equivalent/related indicators are not independent confirmations of an edge.

## Turn an agent's new hypothesis into a custom algorithm

Use the **data-only JSON rule language**, never arbitrary Python/JS in JSON.
Example: the supplied `examples\sma-crossover.json`:

```json
{
  "schema": 1,
  "name": "Research hypothesis: 10/30 SMA trend",
  "entry": {"left": "sma:10", "op": ">", "right": "sma:30"},
  "exit": {"left": "sma:10", "op": "<=", "right": "sma:30"}
}
```

```powershell
& $Python -m stonks_sniper.lab simulate `
  --input "$Runs\icicibank-history.json" `
  --rule "$Repo\.github\skills\stonks-sniper-lab\examples\sma-crossover.json" `
  --capital 100000 --fee-bps 10 --slippage-bps 10 `
  --output "$Runs\custom-sma.json"
```

Supported feature operands:

| Operand | Meaning at the completed current session |
|---|---|
| `open`, `high`, `low`, `close`, `volume` | This reported session's observation |
| `sma:N` | Last N closes, including current close, simple mean |
| `ema:N` | Close EMA, full-N simple-mean seed, alpha 2/(N+1) |
| `rsi:14` | This tool's Wilder 14-change RSI; flat series neutral 50 |
| `roc:N` | 100 * (close / close N observations ago - 1) |
| `prior_high:N` | Maximum high of N PREVIOUS sessions; excludes current |
| `prior_low:N` | Minimum low of N PREVIOUS sessions; excludes current |

Periods are 1..2520; only `rsi:14` is currently supported. The other operand may
be a finite JSON number with absolute value <=1e15, never a numeric string/bool.
Operators: `>`, `>=`, `<`, `<=`, `==`, `!=`. Beware exact float equality.
Combine comparisons with `{"all": [expression, ...]}` or `{"any": [...]}`.
Each group has 1..16 children; the entire rule has <=64 expression nodes and
depth <=8. Additional fields, code, future offsets and unsupported features fail.

For example, enter on a prior-range breakout with positive momentum:

```json
{
  "schema": 1,
  "name": "Untested breakout plus momentum hypothesis",
  "entry": {"all": [
    {"left": "close", "op": ">", "right": "prior_high:20"},
    {"left": "roc:12", "op": ">", "right": 0}
  ]},
  "exit": {"left": "close", "op": "<", "right": "prior_low:20"}
}
```

All referenced series must be ready before a decision, even within an `any`
branch. Entry sets long; exit sets cash. If neither condition is true, retain
the previous target. Nonfinite calculated measurements fail explicitly.
**Both true is an explicit error**, not an arbitrary hidden precedence rule.
Warmup is derived from all operands. There is no intraday protective stop.
The initial target is cash. A breakout first calculated after 20 prior sessions
cannot fill until the following observation.

Explain the hypothesis, reasons it might fail and chosen parameters **before**
running it. Do not disguise this as a published strategy or claim an LLM invented
a novel profitable algorithm. Preserve each version as a new JSON file.

If the idea cannot be expressed here, say so. Do not drop unsupported conditions
silently or smuggle executable code through a feature name. A separately
user-authorised source extension can use `engine.simulate_targets` with one
`bool | None` per observation and a truthful `Pattern.minimum_bars`. That API
validates shape/warmup, NOT causal signal generation; author focused arithmetic
and prefix-invariance tests before trusting it. It is not a generic safe plugin
runner. Current GUI dropdowns do not load custom JSON rules.

## Compare, validate and avoid fooling the learner

Run alternatives against the **same saved observations**, capital, interval and
cost assumptions. Report actual dates and warmup/benchmark-start differences.
Use more than one regime/stock when authorised; one surviving listed bank is
not the Indian market, and selection/survivorship bias remains.

Use `--start YYYY-MM-DD --end YYYY-MM-DD` to select an inclusive interval inside
the snapshot. Each run starts cash and warms up inside that interval. For a
later holdout, freeze the rule first, save a new result and keep the training
receipt. Do not tune against the holdout or claim rolling/walk-forward validation
that you did not run. This interface does not automatically optimise parameters,
correct multiple comparisons, construct baskets or stitch funded holdout positions.

Inspect:

- Marked INR and percentage gain/loss, total capital, actual fees and open units.
- Worst marked equity drawdown; ending positive can hide large interim losses.
- Trade count/completed sales. A positive open holding is not a completed win.
- Same-run buy-and-hold result and differing cash exposure.
- Sensitivity to realistic higher costs, dates and parameters; preserve failures.
- Missing sessions/warnings, adjustment revisions and independent data limitations.

Never report "win rate" without defining closed round trips, matching their
entries/exits and handling costs; the summary's sale count is NOT a win count.
Never annualise a short or zero-length period as if it were reliable evidence.
Do not present the best historical parameter as a prediction or conceal a
negative/zero/no-trade run. If every attempt fails, explain that useful result.

## Teach from evidence and answer novel questions

For "why did it buy here?", find the **signal session**, calculate the indicator
using only observations up to that close, quote the rule/threshold/state, then
show the next actual fill session/open, slippage and fee from the receipt.
Distinguish no signal, retained target, actionable change and actual filled trade.
Use `demonstrations.rule_guides(prefix, key)` for built-in measurement values.
Do not let future prices leak into an explanation of what was knowable then.

For "what if?", save a separate experiment with the one changed assumption,
compare it with the original and label it retrospective. For "will it make money
next month?", explain that this tool cannot answer with a trustworthy forecast;
offer a testable hypothesis and evidence, not an assurance.

In the GUI: **Learn the patterns -> Internet technical strategies -> select a
lesson -> See a real-market demo**. Choose actual data or captured Explore history.
Use **Why this decision?**, **Next signal**, **Next trade**, day slider, price/trades
and money/hold comparison. Event navigation inspects recorded history; it is not
a live alert. Examples are not chosen by future profit. No setup is a valid result.

For The Intelligent Investor: chapters 2/3/5/8 have bounded actual-history exercises
(assumed inflation, context/offers, scheduled equal-money purchases). Chapters
7/11/12/13/14/15/20 offer separate current-company worksheets. Qualitative/unsupported
chapters explain why a mechanical demo is unavailable instead of inventing one.
Current facts are **never** fed into historical simulations. Financial-sector
industrial screens remain inapplicable; missing facts stay unknown. Read
`docs\intelligent-investor.md`; `graham.evaluate` is transparent arithmetic,
not an automated Graham endorsement. Hypothetical intrinsic value and inflation
must remain clearly labelled user assumptions.

Agents can also use the existing current-reference Python API without a GUI:

```python
from dataclasses import asdict
from stonks_sniper.fundamentals import YahooFundamentalsProvider
from stonks_sniper.graham import evaluate

snapshot = YahooFundamentalsProvider().fetch("ICICIBANK", "NSE")
values = {item.key: item.value for item in snapshot.values}
# This is a bank: do NOT apply industrial current-ratio/net-net screens.
findings = evaluate(values, industrial=False)
evidence = {
    "snapshot": asdict(snapshot),
    "findings": {section: [asdict(item) for item in items] for section, items in findings.items()},
}
```

Inspect the actual snapshot dates, field sources, missing keys and warnings,
and preserve them with any explanation. Verify the return contract against the
current `graham.evaluate` before adapting this example. For a non-financial
industrial, sector classification requires human/source verification, not
automatic inference from the absence of a bank label. Value estimates, preferred
liquidation claims, 10/20-year histories and inflation are not silently supplied.
Do not treat the current reference as information available on an earlier date.

## Deliver an honest, useful result

Keep the handoff readable to a beginner:

1. State the tested question, exact hypothesis, capital, actual stock/dates and costs.
2. Explain the algorithm in everyday language with one dated actual decision/fill,
   or explain why there was no trade. No made-up example presented as market data.
3. Give actual marked INR/% profit or loss, comparison, drawdown, trade count and
   open holdings. Clearly separate realised cash from marked unsold positions.
4. Explain what this run does and does not establish, including fit/holdout status.
5. Provide visible absolute paths to the preserved observations, rule and result,
   with hashes/revision where useful. Do not claim a file/command succeeded unless
   its exit status and receipt were checked.

The skill is instructions, not a scheduler, trading bot, independent financial
adviser or ability to awaken another agent. Follow the active human's permissions
and the host's security/privacy rules. Never request broker passwords or place trades.
