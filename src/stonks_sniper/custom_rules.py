"""A small, data-only rule language. No Python, eval, plugins or future offsets."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from operator import eq, ge, gt, le, lt, ne

from stonks_sniper.models import Candle
from stonks_sniper.patterns import Pattern, ema, wilder_rsi
from stonks_sniper.studies import Series, sma

OPERATORS = {">": gt, ">=": ge, "<": lt, "<=": le, "==": eq, "!=": ne}


@dataclass(frozen=True)
class Comparison:
    left: str | float
    op: str
    right: str | float


@dataclass(frozen=True)
class Group:
    kind: str
    children: tuple[Comparison | Group, ...]


Expression = Comparison | Group


def mapping(raw: object) -> dict[str, object]:
    if not isinstance(raw, dict) or any(not isinstance(key, str) for key in raw):
        raise ValueError("Expected an object with string keys.")
    return {key: value for key, value in raw.items()}


def feature(name: str) -> tuple[str, int]:
    if name in {"open", "high", "low", "close", "volume"}:
        return name, 1
    match = re.fullmatch(r"(sma|ema|rsi|roc|prior_high|prior_low):([1-9][0-9]{0,3})", name)
    if match is None:
        raise ValueError(f"Unknown feature {name!r}; use a documented causal series.")
    kind, period = match[1], int(match[2])
    if period > 2520 or (kind == "rsi" and period != 14):
        raise ValueError("Periods must be 1..2520; the supported Wilder RSI is rsi:14.")
    return kind, period


def parse_expression(raw: object, budget: list[int], depth: int = 0) -> Expression:
    budget[0] -= 1
    if budget[0] < 0 or depth > 8:
        raise ValueError("A custom rule allows at most 64 nodes and depth 8.")
    data = mapping(raw)
    if len(data) == 1 and next(iter(data)) in {"all", "any"}:
        kind = next(iter(data))
        children = data[kind]
        if not isinstance(children, list) or not 1 <= len(children) <= 16:
            raise ValueError("all/any require 1..16 child expressions.")
        return Group(kind, tuple(parse_expression(child, budget, depth + 1) for child in children))
    if set(data) != {"left", "op", "right"} or data["op"] not in tuple(OPERATORS):
        raise ValueError("Use left/op/right with >, >=, <, <=, ==, !=; or all/any.")

    def operand(value: object) -> str | float:
        if isinstance(value, str):
            feature(value)
            return value
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("Operands must be feature names or finite numbers, not code/bools.")
        number = float(value)
        if not math.isfinite(number) or abs(number) > 1e15:
            raise ValueError("Numeric thresholds must be finite and at most 1e15 in magnitude.")
        return number

    return Comparison(operand(data["left"]), str(data["op"]), operand(data["right"]))


def names(expression: Expression) -> set[str]:
    if isinstance(expression, Group):
        return set().union(*(names(child) for child in expression.children))
    return {value for value in (expression.left, expression.right) if isinstance(value, str)}


def measurements(bars: tuple[Candle, ...], name: str) -> Series:
    kind, period = feature(name)
    if kind in {"open", "high", "low", "close", "volume"}:
        return [float(getattr(bar, kind)) for bar in bars]
    closes = [bar.close for bar in bars]
    if kind == "sma":
        return sma(closes, period)
    if kind == "ema":
        return ema(closes, period)
    if kind == "rsi":
        return wilder_rsi(closes)
    if kind == "roc":
        return [
            100 * (bar.close / bars[i - period].close - 1) if i >= period else None
            for i, bar in enumerate(bars)
        ]
    return [
        (
            max(bar.high for bar in bars[i - period : i])
            if kind == "prior_high"
            else min(bar.low for bar in bars[i - period : i])
        )
        if i >= period
        else None
        for i in range(len(bars))
    ]


def matches(expression: Expression, values: dict[str, Series], index: int) -> bool:
    if isinstance(expression, Group):
        results = [matches(child, values, index) for child in expression.children]
        return all(results) if expression.kind == "all" else any(results)

    def value(operand: str | float) -> float:
        if isinstance(operand, str):
            result = values[operand][index]
            assert result is not None
            return result
        return operand

    return bool(OPERATORS[expression.op](value(expression.left), value(expression.right)))


@dataclass(frozen=True)
class CustomRule:
    name: str
    entry: Expression
    exit: Expression

    @classmethod
    def parse(cls, raw: object) -> CustomRule:
        data = mapping(raw)
        if set(data) != {"schema", "name", "entry", "exit"} or type(data["schema"]) is not int:
            raise ValueError("A rule requires exactly schema, name, entry and exit.")
        name = data["name"]
        if data["schema"] != 1 or not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
            raise ValueError("Use schema 1 and a nonempty name of at most 100 characters.")
        budget = [64]
        return cls(
            name.strip(),
            parse_expression(data["entry"], budget),
            parse_expression(data["exit"], budget),
        )

    @property
    def pattern(self) -> Pattern:
        periods = []
        for name in names(self.entry) | names(self.exit):
            kind, period = feature(name)
            periods.append(period + (kind in {"rsi", "roc", "prior_high", "prior_low"}))
        return Pattern(
            "custom",
            self.name,
            max(periods, default=1),
            "User-authored declarative entry/exit. Retain target between conditions; "
            "both true is an error. All referenced measurements must be ready.",
            "Unvalidated research hypothesis, not a recommendation or profit forecast.",
            "User-provided rule JSON; see the captured custom_rule in this experiment.",
        )

    def targets(self, bars: tuple[Candle, ...]) -> tuple[bool | None, ...]:
        values = {name: measurements(bars, name) for name in names(self.entry) | names(self.exit)}
        for name, series in values.items():
            if any(value is not None and not math.isfinite(value) for value in series):
                raise ValueError(f"{name}: calculated measurements must remain finite.")
        targets: list[bool | None] = []
        holding = False
        for index, bar in enumerate(bars):
            if any(series[index] is None for series in values.values()):
                targets.append(None)
                continue
            enter = matches(self.entry, values, index)
            leave = matches(self.exit, values, index)
            if enter and leave:
                raise ValueError(f"{bar.session}: entry and exit are both true; clarify the rule.")
            if enter:
                holding = True
            elif leave:
                holding = False
            targets.append(holding)
        return tuple(targets)
