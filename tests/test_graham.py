from __future__ import annotations

import math

import pytest

from stonks_sniper.graham import equal_money, evaluate, real_return, rebalance
from stonks_sniper.models import DataError


def finding(sections, section, title):
    return next(row for row in sections[section] if title in row.title)


def test_missing_facts_never_pass_a_screen_or_become_zero_inputs():
    sections = evaluate({"price": 100}, industrial=True)
    assert all(row.status == "Unknown" for rows in sections.values() for row in rows)
    assert "Missing: average" in finding(sections, "Defensive", "6.").detail
    assert "ncav" in finding(sections, "Valuation", "net-net price").detail


def test_independently_calculated_eps_price_bound_and_margin_have_distinct_denominators():
    sections = evaluate(
        {
            "price": 140,
            "eps1": 8,
            "eps2": 10,
            "eps3": 12,
            "book": 90,
            "value": 200,
            "discount": 30,
            "ttm_eps": 999,
        },
        industrial=True,
    )
    assert "10.0000" in finding(sections, "Valuation", "EPS mean").detail
    assert "14.0000" in finding(sections, "Valuation", "P/E and").detail
    assert "142.3025" in finding(sections, "Valuation", "price-ratio bound").detail
    margin = finding(sections, "Valuation", "Discount to").detail
    assert "30.0000%" in margin and "42.8571%" in margin
    assert finding(sections, "Valuation", "required margin").status == "Pass"
    assert "140.0000" in finding(sections, "Valuation", "maximum price").detail


@pytest.mark.parametrize("eps,book", [(-10, -90), (0, 90), (10, -90)])
def test_negative_or_zero_earnings_book_values_cannot_manufacture_graham_valuation(eps, book):
    sections = evaluate(
        {"price": 10, "eps1": eps, "eps2": eps, "eps3": eps, "book": book}, industrial=True
    )
    assert finding(sections, "Valuation", "price-ratio bound").status == "Unknown"
    assert finding(sections, "Defensive", "7.").status == "Fail"


def test_ncav_subtracts_all_liabilities_and_preferred_claims_in_matching_crore_units():
    values = {"price": 20, "assets": 1000, "liabilities": 600, "preferred": 100, "shares": 10}
    sections = evaluate(values, industrial=True)
    ncav = finding(sections, "Valuation", "asset arithmetic")
    assert "30.0000/share" in ncav.detail and "20.0000" in ncav.detail
    assert finding(sections, "Valuation", "net-net price").status == "Pass"
    values.pop("preferred")
    sections = evaluate(values, industrial=True)
    assert finding(sections, "Valuation", "net-net price").status == "Unknown"
    values["preferred"] = 500
    sections = evaluate(values, industrial=True)
    assert finding(sections, "Valuation", "net-net price").status == "Fail"


def test_defensive_and_enterprising_strength_differ_and_histories_are_not_inferred():
    values = {
        "assets": 160,
        "current_liabilities": 100,
        "debt": 65,
        "long_debt": 65,
        "positive_years": 4,
        "no_loss_years": 5,
        "dividend": 0,
    }
    sections = evaluate(values, industrial=True)
    assert finding(sections, "Defensive", "2a.").status == "Fail"
    assert finding(sections, "Defensive", "2b.").status == "Fail"
    assert finding(sections, "Enterprising", "Current strength").status == "Pass"
    assert finding(sections, "Enterprising", "Debt").status == "Pass"
    assert finding(sections, "Enterprising", "Earnings record").status == "Pass"
    assert finding(sections, "Defensive", "3.").status == "Fail"
    assert finding(sections, "Defensive", "4.").status == "Unknown"
    assert finding(sections, "Enterprising", "Current dividend").status == "Fail"


def test_historical_book_compensation_and_decade_endpoint_averages():
    values = {
        "price": 100,
        "eps1": 20,
        "eps2": 20,
        "eps3": 20,
        "book": 25,
        "old_average": 15,
        "positive_years": 10,
        "dividend_years": 20,
    }
    sections = evaluate(values, industrial=True)
    assert finding(sections, "Defensive", "5.").status == "Pass"
    assert finding(sections, "Defensive", "7.").status == "Pass"  # P/B 4, P/E 5, product 20.
    values["old_average"] = 15.01
    values["book"] = 20  # Product now 25.
    sections = evaluate(values, industrial=True)
    assert finding(sections, "Defensive", "5.").status == "Fail"
    assert finding(sections, "Defensive", "7.").status == "Fail"


def test_banks_unclassified_and_utilities_do_not_get_industrial_pass_fail_ratings():
    sections = evaluate({"price": 10, "assets": 100, "current_liabilities": 20}, industrial=False)
    assert all(row.status == "Not applicable" for row in sections["Defensive"])
    assert all(row.status == "Not applicable" for row in sections["Enterprising"])
    assert finding(sections, "Valuation", "net-net price").status == "Not applicable"


@pytest.mark.parametrize(
    "values",
    [
        {"price": 0},
        {"price": 1e-320},
        {"shares": 0},
        {"price": math.nan},
        {"book": math.inf},
        {"dividend": -1},
        {"discount": 100},
        {"positive_years": 9.5},
        {"sales": 1e100},
    ],
)
def test_invalid_inputs_are_explicit_errors(values):
    with pytest.raises(DataError):
        evaluate(values, industrial=True)


def test_portfolio_arithmetic_independently_calculated():
    assert real_return(8, 6) == pytest.approx(1.8867924528301883)
    assert rebalance(60_000, 40_000, 50) == -10_000
    assert rebalance(40_000, 60_000, 50) == 10_000
    units, cost = equal_money(1000, (100, 50))
    assert units == 30
    assert cost == pytest.approx(2000 / 30)


@pytest.mark.parametrize("kind", ["inflation", "return", "allocation", "empty", "zero", "nan"])
def test_invalid_scenario_inputs_are_explicit_errors(kind):
    with pytest.raises(DataError):
        if kind == "inflation":
            real_return(8, -100)
        elif kind == "return":
            real_return(math.inf, 6)
        elif kind == "allocation":
            rebalance(0, 0, 50)
        elif kind == "empty":
            equal_money(1000, ())
        elif kind == "zero":
            equal_money(1000, (0,))
        else:
            equal_money(math.nan, (100,))


@pytest.mark.parametrize("kind", ["inflation", "allocation", "purchases"])
def test_finite_inputs_cannot_produce_success_shaped_infinite_outputs(kind):
    with pytest.raises(DataError, match="arithmetic range"):
        if kind == "inflation":
            real_return(1e308, -99.99999999999999)
        elif kind == "allocation":
            rebalance(1e308, 1e308, 50)
        else:
            equal_money(1e308, (1e-308,))
