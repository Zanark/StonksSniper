# Agent and human simulation lab

The latest source exposes `python -m stonks_sniper.lab`; it needs no GUI, broker
or LLM service. It does not predict profits or execute real orders.

The canonical detailed operating instructions are the repository's
[stonks-sniper-lab skill](../.github/skills/stonks-sniper-lab/SKILL.md). They cover
setup, capital, actual history, every strategy family, exact commands, custom
rules, receipts, costs, dated explanations, holdouts and honest profit/loss reporting.
Copilot CLI discovers repository skills under `.github/skills`; other agents
can read the same Markdown and invoke the Python module.

## Interface

| Command | Contract |
|---|---|
| `catalogue` | JSON for 27 rules, full formulas, warmups, sources and ELI15 lessons |
| `fetch --symbol ICICIBANK --exchange NSE --start DATE --end DATE --output PATH` | Actual completed daily Yahoo history with dates, warnings and SHA256 receipt |
| `simulate --input PATH --strategy sma --capital 100000 --output PATH` | Captured-input experiment, marked INR/% outcome, trades and benchmark |
| `simulate --input PATH --rule RULE.json --capital 100000 --output PATH` | Same engine using validated declarative custom entry/exit targets |

Simulation accepts `--fee-bps` and `--slippage-bps` (default 10 each).
Optional `--start`/`--end` are inclusive and must fall inside the captured history.
Each interval starts cash and warms up inside that interval, not before it.
See `--help` and the skill for complete runnable PowerShell examples.

Success prints JSON to stdout and returns zero. Runtime research failures return
code 2 with explicit error JSON on stderr; argument syntax errors use standard
argparse usage/error text. Provider warnings/logging may also use stderr.
Output paths are absolute in receipts. Output files are never overwritten.
No synthetic fallback or ticker substitution is allowed.

## Persisted evidence

`fetch` saves schema 1 with `observations` (the validated `MarketData` fields).
Simulation output additionally saves `experiment`, `summary`, `input_sha256`,
`custom_rule`/`custom_rule_sha256` when applicable, execution policy and limitations.
These include exact observations, rule/assumptions, target per observation,
decision/fill dates, fees, adjusted units, equity, benchmark and open holdings.
The SHA256 identifies file bytes, not data authenticity or independent price validation.
Imported source strings are claims, not trusted evidence.

The importer rejects ambiguous currency/interval, invalid symbols, unordered/duplicate
sessions, invalid OHLCV, naive fetch timestamps and current/future-day observations
relative to fetch time and now. JSON rejects duplicate keys, NaN and Infinity.
Inputs are bounded to 20 MiB and 20,000 daily observations.

## Custom rules and safety boundaries

The skill contains the complete grammar and two shipped runnable examples.
Expressions are comparisons or `all`/`any` groups over OHLCV, close SMA/EMA,
Wilder RSI(14), ROC and strictly previous high/low ranges. Periods, tree size
and depth are bounded. All inputs must be ready and calculated measurements finite.
If neither condition is true, retain the previous target; simultaneous entry/exit
is an error. No executable expressions, future offsets,
plugins, orders, shorts, intraday stops or arbitrary network calls are supported.

`engine.simulate_targets` shares existing accounting and validates target shape
and declared warmup. It cannot certify arbitrary Python-generated targets are
causal. Source extensions need explicit authority plus arithmetic/prefix tests.
The GUI's built-in dropdown does not load custom JSON. No automatic optimisation,
basket engine or autonomous research agent has been introduced.

## Interpret results honestly

Final value includes unsold stock at the last close, not just realised cash.
No forced final sale, second dividend credit or complete tax model is applied.
The reference starts after each rule's warmup, so different rules can have
different comparison start dates. Record fees, drawdown, trades/no trades,
open holdings, assumptions and actual dates, not only the best return.
Preserve unsuccessful hypotheses and freeze a rule before testing a later holdout.

The book's current fundamentals remain separate from historical simulations.
Qualitative investing principles are not converted into fictional timing rules.
The app and skill teach a learner to ask better questions; neither proves a
strategy will generate future profits.
