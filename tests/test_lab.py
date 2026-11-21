from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

import pytest
from test_research import observations

from stonks_sniper.custom_rules import CustomRule
from stonks_sniper.engine import Assumptions, simulate, simulate_targets
from stonks_sniper.lab import load_observations, main, read_document
from stonks_sniper.patterns import PATTERNS, targets

EXAMPLES = (
    Path(__file__).resolve().parents[1] / ".github" / "skills" / "stonks-sniper-lab" / "examples"
)


@pytest.mark.parametrize(
    "filename,key", [("sma-crossover.json", "sma"), ("prior-range-breakout.json", "donchian")]
)
def test_custom_examples_reproduce_reference_signals_accounting_and_causal_prefixes(filename, key):
    document, _ = read_document(EXAMPLES / filename)
    rule = CustomRule.parse(document)
    data = observations()
    pattern = next(pattern for pattern in PATTERNS if pattern.key == key)
    desired = rule.targets(data.candles)
    assert desired == targets(data.candles, pattern)
    expected = simulate(data, pattern, Assumptions(25000, 25, 30))
    result = simulate_targets(data, rule.pattern, desired, expected.assumptions)
    assert result.equity == expected.equity and result.trades == expected.trades
    for count in (rule.pattern.minimum_bars + 1, 63, 90):
        prefix = replace(data, candles=data.candles[:count])
        assert rule.targets(prefix.candles) == desired[:count]
        partial = simulate_targets(prefix, rule.pattern, desired[:count], expected.assumptions)
        assert partial.equity == result.equity[:count]


def rule_document():
    return {
        "schema": 1,
        "name": "Explicit test hypothesis",
        "entry": {"left": "close", "op": ">", "right": 100},
        "exit": {"left": "close", "op": "<=", "right": 100},
    }


@pytest.mark.parametrize(
    "change",
    [
        {"schema": True},
        {"name": ""},
        {"entry": {"left": "__import__('os')", "op": ">", "right": 0}},
        {"entry": {"left": "close:+1", "op": ">", "right": 0}},
        {"entry": {"left": "sma:0", "op": ">", "right": 0}},
        {"entry": {"left": "sma:2521", "op": ">", "right": 0}},
        {"entry": {"left": "rsi:2", "op": ">", "right": 0}},
        {"entry": {"left": "close", "op": ">", "right": True}},
        {"entry": {"left": "close", "op": ">", "right": float("inf")}},
        {"entry": {"any": []}},
        {"entry": {"left": "close", "op": ">", "right": 0, "offset": 1}},
    ],
)
def test_custom_language_rejects_ambiguous_code_future_and_unsupported_rules(change):
    with pytest.raises(ValueError):
        CustomRule.parse(rule_document() | change)


def test_custom_rule_rejects_nonfinite_derived_measurements():
    bars = observations().candles[:2]
    bars = (
        replace(bars[0], open=1, high=1, low=1, close=1),
        replace(bars[1], open=1e308, high=1e308, low=1e308, close=1e308),
    )
    document = rule_document()
    document["entry"] = {"left": "roc:1", "op": ">", "right": 0}
    document["exit"] = {"left": "roc:1", "op": "<=", "right": 0}
    with pytest.raises(ValueError, match="measurements must remain finite"):
        CustomRule.parse(document).targets(bars)


def test_custom_groups_wait_for_all_data_retain_state_and_reject_overlap():
    document = rule_document()
    document["entry"] = {
        "all": [
            {"left": "roc:12", "op": ">", "right": 0},
            {
                "any": [
                    {"left": "volume", "op": ">", "right": 0},
                    {"left": "close", "op": ">", "right": "sma:30"},
                ]
            },
        ]
    }
    document["exit"] = {"left": "roc:12", "op": "<", "right": 0}
    rule = CustomRule.parse(document)
    decisions = rule.targets(observations().candles)
    assert decisions[:29] == (None,) * 29
    assert set(decisions[29:]) == {True, False}
    document = rule_document()
    document["exit"] = document["entry"]
    with pytest.raises(ValueError, match="both true"):
        CustomRule.parse(document).targets(observations().candles)
    nested = rule_document()["entry"]
    for _ in range(10):
        nested = {"all": [nested]}
    with pytest.raises(ValueError, match="depth"):
        CustomRule.parse(rule_document() | {"entry": nested})


def snapshot_file(tmp_path):
    filename = tmp_path / "input.json"
    filename.write_text(
        json.dumps({"schema": 1, "observations": asdict(observations())}, default=str),
        encoding="utf-8",
    )
    return filename


def test_cli_capital_costs_dates_receipts_and_no_overwrite(tmp_path, capsys):
    filename = snapshot_file(tmp_path)
    output = tmp_path / "result.json"
    command = [
        "simulate",
        "--input",
        str(filename),
        "--strategy",
        "sma",
        "--capital",
        "25000",
        "--fee-bps",
        "25",
        "--slippage-bps",
        "30",
        "--start",
        "2024-01-11",
        "--end",
        "2024-04-04",
        "--output",
        str(output),
    ]
    assert main(command) == 0
    response = json.loads(capsys.readouterr().out)
    assert response["output"] == str(output.resolve())
    saved = json.loads(output.read_text(encoding="utf-8"))
    expected = simulate(
        replace(observations(), candles=observations().candles[10:95]),
        PATTERNS[0],
        Assumptions(25000, 25, 30),
    )
    assert saved["experiment"]["equity"] == list(expected.equity)
    assert response["summary"]["marked_profit_loss_inr"] == expected.equity[-1] - 25000
    assert len(saved["input_sha256"]) == len(response["sha256"]) == 64
    assert main(command) == 2
    assert "Refusing to overwrite" in capsys.readouterr().err
    assert json.loads(output.read_text(encoding="utf-8")) == saved


def test_cli_custom_receipt_and_provider_failure_do_not_fabricate_results(
    tmp_path, monkeypatch, capsys
):
    filename = snapshot_file(tmp_path)
    output = tmp_path / "custom.json"
    assert (
        main(
            [
                "simulate",
                "--input",
                str(filename),
                "--rule",
                str(EXAMPLES / "sma-crossover.json"),
                "--capital",
                "1000",
                "--output",
                str(output),
            ]
        )
        == 0
    )
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["summary"]["initial_capital_inr"] == 1000
    assert saved["custom_rule"]["schema"] == 1 and len(saved["custom_rule_sha256"]) == 64
    failed = tmp_path / "failed.json"

    def unavailable(*_):
        raise ValueError("Explicit provider outage")

    monkeypatch.setattr("stonks_sniper.lab.YahooDailyProvider.fetch", unavailable)
    assert (
        main(
            [
                "fetch",
                "--symbol",
                "ICICIBANK",
                "--start",
                "2024-01-01",
                "--end",
                "2024-04-04",
                "--output",
                str(failed),
            ]
        )
        == 2
    )
    failure = json.loads(capsys.readouterr().err)
    assert "Explicit provider outage" in failure["message"] and not failed.exists()


@pytest.mark.parametrize(
    "raw", ['{"schema": 1, "schema": 2}', '{"schema": NaN}', '{"schema": Infinity}']
)
def test_json_does_not_silently_accept_duplicate_or_nonfinite_fields(tmp_path, raw):
    path = tmp_path / "bad.json"
    path.write_text(raw, encoding="utf-8")
    with pytest.raises(ValueError):
        read_document(path)


def test_import_validation_and_explicit_targets_reject_invalid_contracts():
    data = observations()
    document = json.loads(json.dumps({"schema": 1, "observations": asdict(data)}, default=str))
    assert load_observations(document) == data
    document["observations"]["currency"] = "USD"
    with pytest.raises(ValueError, match="INR"):
        load_observations(document)
    with pytest.raises(ValueError, match="one bool"):
        simulate_targets(data, PATTERNS[0], (True,))
    with pytest.raises(ValueError, match="immutable tuple"):
        simulate_targets(data, PATTERNS[0], [None] * 100)
    with pytest.raises(ValueError, match="warmup"):
        simulate_targets(data, PATTERNS[0], (True,) * 100)
    with pytest.raises(ValueError, match="positive whole"):
        simulate_targets(data, replace(PATTERNS[0], minimum_bars=0), (False,) * 100)
