"""Independent arithmetic and entry/exit fixtures, never application market data."""

from dataclasses import replace
from datetime import date, timedelta
from math import isfinite

import pytest

from stonks_sniper.models import Candle
from stonks_sniper.patterns import PATTERNS, targets
from stonks_sniper.studies import ema, study, true_ranges

NEW = PATTERNS[7:]


def bars(prices, *, volume=1000, upper=2, lower=2):
    return tuple(
        Candle(
            date(2024, 1, 1) + timedelta(days=i), price, price + upper, price - lower, price, volume
        )
        for i, price in enumerate(prices)
    )


@pytest.mark.parametrize("pattern", NEW, ids=lambda p: p.key)
def test_full_seed_warmup_and_every_prefix_match(pattern):
    data = bars([100 + i * 0.3 + (i % 9) for i in range(90)])
    result = study(data, pattern.key)
    assert result.targets == targets(data, pattern)
    assert result.targets[: pattern.minimum_bars - 1] == (None,) * (pattern.minimum_bars - 1)
    assert all(isinstance(value, bool) for value in result.targets[pattern.minimum_bars - 1 :])
    for length in (0, pattern.minimum_bars - 1, pattern.minimum_bars, 83):
        prefix = study(data[:length], pattern.key)
        assert prefix.targets == result.targets[:length]
        assert [(name, values) for name, values in prefix.guides] == [
            (name, values[:length]) for name, values in result.guides
        ]


@pytest.mark.parametrize(
    "key,expected",
    [
        ("stochastic", 1500 / 17),
        ("williams", -200 / 17),
        ("cci", 9.5 / (0.015 * 5)),
        ("roc", 12),
        ("tsi", 100),
        ("adx", 100),
        ("aroon", 100),
        ("ichimoku", 177),
        ("keltner", 119),
        ("bollinger-breakout", 119),
        ("chandelier", 121),
        ("obv", 19000),
        ("cmf", 0),
        ("mfi", 100),
        ("chaikin", 0),
        ("emv", 400000),
        ("ultimate", 50),
        ("vortex", 1.25),
        ("trix", 100 / 121),
        ("force", 1000),
    ],
)
def test_first_available_value_against_hand_calculated_linear_prices(key, expected):
    pattern = next(p for p in NEW if p.key == key)
    data = bars(list(range(100, 100 + pattern.minimum_bars)))
    assert study(data, key).guides[0][1][-1] == pytest.approx(expected)


@pytest.mark.parametrize("pattern", NEW, ids=lambda p: p.key)
def test_flat_zero_range_and_zero_volume_are_explicitly_neutral(pattern):
    result = study(bars([100] * 90, volume=0, upper=0, lower=0), pattern.key)
    assert result.targets[pattern.minimum_bars - 1 :] == (False,) * (91 - pattern.minimum_bars)
    assert all(
        isfinite(value) for _, values in result.guides for value in values if value is not None
    )


def test_gap_aware_true_range_wilder_and_nested_ema_seeds():
    data = bars([100, 112], upper=2, lower=2)
    assert true_ranges(data) == [4, 14]
    assert ema([None, 1, 3, 5], 2, wilder=True) == [None, None, 2, 3.5]
    assert ema(ema([1, 2, 3, 4], 2), 2) == [None, None, 2, 3]
    assert ema([1, 2, None, 5, 7], 2) == [None, 1.5, None, None, 6]


def test_range_reversion_and_range_momentum_are_opposite_hypotheses():
    low = bars([100] * 20, upper=9, lower=1)
    high = bars([100] * 20, upper=1, lower=9)
    assert study(low, "stochastic").targets[-1] is True
    assert study(low, "williams").targets[-1] is False
    assert study(high, "stochastic").targets[-1] is False
    assert study(high, "williams").targets[-1] is True
    bottom = bars([100] * 16, upper=8, lower=2)
    assert study(bottom, "stochastic").targets[-1] is True  # Exactly 20.
    midpoint = bars([100] * 14)
    assert study(midpoint, "williams").targets[-1] is False  # Exactly -50.


def test_volume_formulas_and_degenerate_day_conventions():
    rising = bars(list(range(100, 140)), upper=1, lower=3)
    assert study(rising, "cmf").guides[0][1][-1] == pytest.approx(0.5)
    assert study(rising[:10], "chaikin").guides[0][1][-1] == pytest.approx(1750)
    assert study(rising, "mfi").targets[-1] is False
    falling = bars(list(range(140, 100, -1)))
    assert study(falling, "mfi").guides[0][1][-1] == 0
    assert study(falling, "mfi").targets[-1] is True
    assert study(bars([100] * 40), "mfi").guides[0][1][-1] == 50
    no_volume = tuple(replace(bar, volume=0) for bar in rising)
    assert study(no_volume, "cmf").guides[0][1][-1] == 0
    assert study(no_volume, "emv").guides[0][1][-1] == 0
    flat = bars([100] * 40, upper=0, lower=0)
    assert study(flat, "chaikin").guides[0][1][-1] == 0


def test_bollinger_breakout_retains_until_middle_and_cci_until_zero():
    data = bars([100] * 25 + [120, 110, 90])
    assert study(data, "bollinger-breakout").targets[-3:] == (True, True, False)
    assert study(data, "cci").targets[-3:] == (True, True, False)


def test_channel_and_exit_levels_match_independent_arithmetic():
    data = bars(list(range(100, 122)))
    keltner = dict(study(data, "keltner").guides)
    assert keltner["Upper band (buy above)"][19] == pytest.approx(109.5 + 2 * 4)
    bollinger = dict(study(data, "bollinger-breakout").guides)
    assert bollinger["Upper band (buy above)"][19] == pytest.approx(109.5 + 2 * (33.25**0.5))
    chandelier = dict(study(data, "chandelier").guides)
    assert chandelier["Ratcheted exit while owning"][21] == pytest.approx(123 - 3 * 4)


@pytest.mark.parametrize("pattern", NEW, ids=lambda p: p.key)
def test_each_added_rule_can_both_buy_and_sell_on_reported_candles(pattern):
    prices = []
    price = 400.0
    for direction in (1, -1, 1, -1):
        for day in range(120):
            price += direction * (15 if day % 24 == 0 else 0.5)
            prices.append(price)
    data = list(bars(prices))
    for index in range(1, len(data)):
        bar = data[index]
        rising = bar.close > data[index - 1].close
        data[index] = replace(
            bar,
            high=bar.close + (0.5 if rising else 3),
            low=bar.close - (3 if rising else 0.5),
        )
    signals = targets(tuple(data), pattern)
    assert True in signals
    assert any(
        previous is True and current is False
        for previous, current in zip(signals, signals[1:], strict=False)
    )


def test_chandelier_ratchet_reset_and_no_same_close_reentry():
    data = bars(list(range(100, 150)) + [130] * 25 + list(range(131, 171)))
    result = study(data, "chandelier")
    stop_values = dict(result.guides)["Ratcheted exit while owning"]
    active = None
    exits = 0
    for index, position in enumerate(result.targets):
        if index and result.targets[index - 1] is True:
            assert stop_values[index] >= active
            if not position:
                exits += 1
                assert data[index].close <= stop_values[index]
        active = stop_values[index]
    assert exits > 0
    assert result.targets[-1] is True
    assert any(value is None for value in stop_values[50:75])


def test_visible_cloud_uses_past_not_future_or_unshifted_ranges():
    data = bars(list(range(100, 190)))
    guides = dict(study(data, "ichimoku").guides)
    assert guides["Visible cloud A (26 days old)"][77] == pytest.approx(142.75)
    assert guides["Visible cloud B (26 days old)"][77] == pytest.approx(125.5)
    assert study(data[:77], "ichimoku").targets[-1] is None
    assert study(data[:78], "ichimoku").targets[-1] is True


def test_direction_scores_need_correct_direction_and_aroon_ties_choose_newest():
    falling = bars(list(range(200, 110, -1)))
    adx = study(falling, "adx")
    assert adx.guides[0][1][-1] == pytest.approx(100)
    assert adx.targets[-1] is False
    tied = study(bars([100] * 26), "aroon")
    assert tied.guides[0][1][-1] == tied.guides[1][1][-1] == 100
    assert tied.targets[-1] is False


def test_unknown_study_is_an_explicit_error():
    with pytest.raises(ValueError, match="No study"):
        study(bars([100] * 30), "not-a-rule")
