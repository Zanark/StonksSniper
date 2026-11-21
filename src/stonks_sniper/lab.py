"""Headless, JSON-based research interface for agents and humans."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict, replace
from datetime import date, datetime
from pathlib import Path

from stonks_sniper import __version__
from stonks_sniper.custom_rules import CustomRule, mapping
from stonks_sniper.engine import Assumptions, simulate, simulate_targets
from stonks_sniper.lessons import LESSONS
from stonks_sniper.models import Candle, MarketData
from stonks_sniper.patterns import PATTERNS
from stonks_sniper.providers import INDIA, YahooDailyProvider, yahoo_symbol


def _reject_constant(value: str) -> object:
    raise ValueError(f"Nonfinite JSON number {value} is not allowed.")


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_document(path: Path) -> tuple[dict[str, object], str]:
    limit = 20 * 1024 * 1024
    with path.open("rb") as source:
        raw = source.read(limit + 1)
    if len(raw) > limit:
        raise ValueError("Research input exceeds the 20 MiB limit.")
    parsed = json.loads(
        raw.decode("utf-8-sig"), parse_constant=_reject_constant, object_pairs_hook=_unique_pairs
    )
    return mapping(parsed), hashlib.sha256(raw).hexdigest()


def _text(data: dict[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a nonempty string.")
    return value


def _number(data: dict[str, object], key: str) -> float:
    value = data.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{key} must be a finite JSON number.")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{key} must be finite.")
    return number


def load_observations(document: dict[str, object]) -> MarketData:
    if type(document.get("schema")) is not int or document["schema"] != 1:
        raise ValueError("Unsupported observation schema; expected 1.")
    data = mapping(document.get("observations"))
    if data.get("currency") != "INR" or data.get("interval") != "1d":
        raise ValueError("The lab requires INR daily observations.")
    symbol, exchange = _text(data, "symbol"), _text(data, "exchange")
    if yahoo_symbol(symbol, exchange) != symbol:
        raise ValueError("Observation identity must use the matching exchange-qualified symbol.")
    rows = data.get("candles")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 20_000:
        raise ValueError("Expected 1..20000 daily observations.")
    candles: list[Candle] = []
    for row in rows:
        bar = mapping(row)
        if set(bar) != {"session", "open", "high", "low", "close", "volume"}:
            raise ValueError("Each observation requires session/open/high/low/close/volume.")
        candles.append(
            Candle(
                date.fromisoformat(_text(bar, "session")),
                *(_number(bar, key) for key in ("open", "high", "low", "close", "volume")),
            )
        )
    warnings = data.get("warnings", [])
    if not isinstance(warnings, list) or any(not isinstance(item, str) for item in warnings):
        raise ValueError("Data warnings must be a list of strings.")
    result = MarketData(
        symbol,
        exchange,
        tuple(candles),
        datetime.fromisoformat(_text(data, "fetched_at")),
        _text(data, "source"),
        _text(data, "price_basis"),
        tuple(str(item) for item in warnings),
    )
    cutoff = min(result.fetched_at.astimezone(INDIA).date(), datetime.now(INDIA).date())
    if any(bar.session >= cutoff for bar in result.candles):
        raise ValueError("Current/future-day observations relative to fetch/now are not admitted.")
    return result


def write_document(path: Path, document: dict[str, object]) -> dict[str, str]:
    content = json.dumps(document, indent=2, default=str, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as destination:
        destination.write(content)
    return {
        "output": str(path.resolve()),
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Stonks Sniper educational research lab. Simulated profits can be losses."
    )
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("catalogue", help="List all built-in rules and ELI15 lessons as JSON.")
    fetch = commands.add_parser(
        "fetch", help="Save actual completed Yahoo history, never fake data."
    )
    fetch.add_argument("--symbol", required=True)
    fetch.add_argument("--exchange", choices=("NSE", "BSE"), default="NSE")
    fetch.add_argument("--start", type=date.fromisoformat, required=True)
    fetch.add_argument("--end", type=date.fromisoformat, required=True)
    fetch.add_argument("--output", type=Path, required=True)
    run = commands.add_parser("simulate", help="Run a rule over a captured daily snapshot.")
    run.add_argument("--input", type=Path, required=True)
    strategy = run.add_mutually_exclusive_group(required=True)
    strategy.add_argument("--strategy", choices=[pattern.key for pattern in PATTERNS])
    strategy.add_argument("--rule", type=Path, help="Validated custom rule JSON, never Python.")
    run.add_argument("--capital", type=float, required=True)
    run.add_argument("--fee-bps", type=float, default=10)
    run.add_argument("--slippage-bps", type=float, default=10)
    run.add_argument("--start", type=date.fromisoformat)
    run.add_argument("--end", type=date.fromisoformat)
    run.add_argument("--output", type=Path, required=True)
    return root


def execute(args: argparse.Namespace) -> dict[str, object]:
    if args.command == "catalogue":
        return {
            "schema": 1,
            "strategies": [
                {"pattern": asdict(pattern), "lesson": asdict(LESSONS[pattern.key])}
                for pattern in PATTERNS
            ],
            "execution": "Long/cash; signal at completed close; fill next available open.",
            "limits": "Historical adjusted units, not orders, predictions or guaranteed profits.",
        }
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output.resolve()}; choose a new path.")
    if args.command == "fetch":
        data = YahooDailyProvider().fetch(args.symbol, args.exchange, args.start, args.end)
        document = {
            "schema": 1,
            "application": f"StonksSniper {__version__}",
            "observations": asdict(data),
        }
        return {
            **write_document(args.output, document),
            "symbol": data.symbol,
            "observations": len(data.candles),
            "first_session": str(data.candles[0].session),
            "latest_session": str(data.candles[-1].session),
            "warnings": list(data.warnings),
        }
    document, digest = read_document(args.input)
    data = load_observations(document)
    start = args.start or data.candles[0].session
    end = args.end or data.candles[-1].session
    if start > end:
        raise ValueError("Start must be on or before end.")
    if start < data.candles[0].session or end > data.candles[-1].session:
        raise ValueError("Simulation dates must lie within the captured history.")
    data = replace(data, candles=tuple(bar for bar in data.candles if start <= bar.session <= end))
    assumptions = Assumptions(args.capital, args.fee_bps, args.slippage_bps)
    custom: dict[str, object] | None = None
    rule_digest: str | None = None
    if args.rule is not None:
        custom, rule_digest = read_document(args.rule)
        rule = CustomRule.parse(custom)
        result = simulate_targets(data, rule.pattern, rule.targets(data.candles), assumptions)
    else:
        pattern = next(pattern for pattern in PATTERNS if pattern.key == args.strategy)
        result = simulate(data, pattern, assumptions)
    summary = {
        "symbol": data.symbol,
        "strategy": result.pattern.key,
        "name": result.pattern.name,
        "first_session": str(data.candles[0].session),
        "latest_session": str(data.candles[-1].session),
        "initial_capital_inr": assumptions.initial_cash,
        "final_marked_value_inr": result.equity[-1],
        "marked_profit_loss_inr": result.equity[-1] - assumptions.initial_cash,
        "return_pct": result.return_pct,
        "buy_hold_return_pct": result.benchmark_return_pct,
        "max_drawdown_pct": result.max_drawdown_pct,
        "trades": len(result.trades),
        "completed_sales": sum(trade.side == "SELL" for trade in result.trades),
        "open_adjusted_units": result.open_units,
        "total_fees_inr": sum(trade.fee for trade in result.trades),
    }
    output = {
        "schema": 1,
        "application": f"StonksSniper {__version__}",
        "input_sha256": digest,
        "custom_rule_sha256": rule_digest,
        "custom_rule": custom,
        "observations": asdict(data),
        "experiment": asdict(result),
        "summary": summary,
        "execution": "Start in cash; warmup inside chosen range; next available opening; "
        "fractional adjusted units; fees/slippage on both sides; no forced liquidation or "
        "complete tax model. Last-day targets may not fill. Benchmark starts after warmup.",
        "limits": "Research hypothesis, NOT a forecast or investment recommendation. "
        "Imported provenance is a claim, not independent authentication; a SHA256 preserves "
        "input identity, not truth. Fit/holdout separation and independent validation are "
        "the researcher's responsibility. Missing provider sessions are not repaired.",
    }
    return {**write_document(args.output, output), "summary": summary}


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        response = execute(args)
        print(json.dumps(response, allow_nan=False))
    except (OSError, ValueError, TypeError, OverflowError, RecursionError) as error:
        print(json.dumps({"error": type(error).__name__, "message": str(error)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
