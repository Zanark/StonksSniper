"""Original study notes and transparent arithmetic, not trading signals."""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import fmean

from stonks_sniper.models import DataError

SOURCES = {
    "edition": (
        "Publisher edition description",
        "https://books.google.com/books?id=VwvyEAAAQBAJ",
    ),
    "contents": (
        "Licensed bookseller's 2024 chapter inventory",
        "https://www.perlego.com/book/4332826/"
        "the-intelligent-investor-third-edition-the-definitive-book-on-value-investing-pdf",
    ),
    "principles": (
        "Graham's investing principles (Investopedia)",
        "https://www.investopedia.com/articles/basics/07/grahamprinciples.asp",
    ),
    "market": ("Mr. Market", "https://www.investopedia.com/terms/m/mr-market.asp"),
    "number": ("Graham number", "https://www.investopedia.com/terms/g/graham-number.asp"),
    "ncav": ("Net current asset value", "https://www.investopedia.com/terms/n/ncavps.asp"),
    "safety": ("Margin of safety", "https://www.investopedia.com/terms/m/marginofsafety.asp"),
    "criteria": ("Historical selection criteria", "https://www.grahamvalue.com/quick-reference"),
    "aaii": (
        "AAII's discussion and explicitly modified screens",
        "https://www.aaii.com/journal/article/"
        "graham-s-long-term-winning-approach-for-enterprising-defensive-investors",
    ),
    "growth": (
        "Warning about the growth formula",
        "https://www.grahamvalue.com/article/understanding-benjamin-graham-formula-correctly",
    ),
    "sebi": (
        "SEBI investor education: advisers (Indian application)",
        "https://investor.sebi.gov.in/investment_advisor.html",
    ),
}

SCOPE = (
    "An independent reading companion, not the book or an endorsed interpretation. "
    "These original ELI15 notes map the 20 main chapters of Graham's revised text. "
    "Page numbers differ by edition. The 2024 edition keeps Graham's text and updates "
    "Jason Zweig's commentary; these notes do not claim to reproduce all commentary, "
    "case details, appendixes or every concept in every edition. "
    "Historical US rules are study benchmarks, not automatic Indian buy/sell advice. "
    "The 27 internet-sourced technical strategies remain separate."
)


@dataclass(frozen=True)
class BookLesson:
    chapter: int
    title: str
    idea: str
    example: str
    practical: str
    caution: str
    sources: tuple[str, ...] = ("contents", "principles")


BOOK_LESSONS = (
    BookLesson(
        1,
        "Investing or speculating?",
        "Investing means studying a business, protecting your starting money and seeking a "
        "reasonable return. Betting only that somebody will pay more is speculation. "
        "Defensive describes limited research effort; enterprising means doing substantially "
        "more work, not simply taking bigger risks.",
        "Buying a shop after checking its accounts differs from buying its sign because it "
        "has become fashionable. A short-term price chart does not replace the accounts.",
        "For an NSE/BSE company, write what it sells, how it earns cash, its debt, a "
        "conservative value range and what evidence would disprove your thesis.",
        "A successful speculative trade is not proof of investment analysis. The app's "
        "technical backtests are experiments, not proof that Graham's requirements are met.",
    ),
    BookLesson(
        2,
        "Inflation: count purchasing power",
        "More rupees do not necessarily buy more things. Compare investment growth with "
        "rising prices. Shares are business ownership, not a guaranteed inflation shield; "
        "fixed-income investments have inflation, credit and interest-rate risks.",
        "An illustrative 8% return with 6% inflation means about 1.89% more purchasing "
        "power, not 8%. Calculate 1.08 / 1.06 - 1.",
        "Use the Inflation worksheet with your own return and inflation assumptions. "
        "Compare after-tax alternatives separately; Indian taxes are not modelled.",
        "The calculator is arithmetic, not an inflation forecast or a promise that stocks, "
        "gold or any single asset will protect purchasing power.",
    ),
    BookLesson(
        3,
        "Market history is context, not a timetable",
        "Long histories include booms, crashes and changing valuation levels. A strong "
        "recent decade is not a permanent growth rate, and an expensive market need not "
        "fall on your chosen date.",
        "Ten unusually busy school-fair days do not tell you how many snacks the stall "
        "will sell every day for the next ten years.",
        "Compare long Indian index histories, earnings and valuations across cycles. "
        "In Explore, change dates and inspect drawdowns rather than cherry-picking a winner.",
        "The chapter's early-1972 US setting is historical. This app does not fetch a "
        "century of Indian index fundamentals or claim a market-timing signal.",
    ),
    BookLesson(
        4,
        "Defensive portfolio: allocation and rebalancing",
        "Choose a sensible mix of shares and high-quality fixed income before excitement "
        "takes over. Graham discusses a simple 50/50 mix and a historical 25%-75% band. "
        "Rebalancing brings a drifting mix back to a chosen target.",
        "If a pretend portfolio becomes INR 60,000 shares and INR 40,000 bonds, a 50% "
        "share target would move INR 10,000 from shares to bonds before costs.",
        "Use Allocation with your own values. Include emergency needs, bond credit "
        "quality, maturity and taxation in a separate written plan.",
        "These US-era proportions are examples, not a personal allocation prescription. "
        "No bond prices, basket execution or tax-aware rebalancing are simulated.",
    ),
    BookLesson(
        5,
        "Common stocks: diversify and invest regularly",
        "Spread business risk, prefer established financially sound businesses at "
        "reasonable prices, and avoid treating popularity as quality. Regular equal-money "
        "purchases reduce the need to guess one perfect entry date.",
        "Two illustrative INR 1,000 purchases at INR 100 and INR 50 buy 10 and 20 units. "
        "Average cost is 2,000 / 30 = INR 66.67, not the price average of INR 75.",
        "Use Equal-money purchases to understand rupee-cost averaging. For actual Indian "
        "holdings, review sector concentration, liquidity and transaction costs.",
        "Graham's historical diversification discussion includes roughly 10-30 stocks. "
        "A count alone does not remove correlated risk. Regular buying can still lose money.",
    ),
    BookLesson(
        6,
        "Enterprising: first avoid costly mistakes",
        "Extra effort should start with what not to buy blindly: weak credit, unsuitable "
        "preferred shares, promotional new issues and unfamiliar foreign securities. "
        "A high offered yield can be payment for a large chance of loss.",
        "A shop promising to pay twice the usual interest may be desperate for money, "
        "not twice as safe as its neighbour.",
        "Before an Indian IPO, NCD or preference share, inspect the offer document, debt "
        "ranking, cash flows, use of proceeds, related parties and liquidity.",
        "US bond, tax and preferred-stock details do not transfer literally to India. "
        "This app supplies a reading checklist, not instrument-specific approval.",
    ),
    BookLesson(
        7,
        "Enterprising: bargains and special situations",
        "Research may uncover neglected large companies, unusually cheap assets or "
        "special situations such as reorganisations and arbitrage. A bargain requires "
        "evidence of value, not just a fallen price.",
        "A discounted second-hand bicycle is cheap only if its frame and brakes still "
        "work. Repair costs can consume the apparent bargain.",
        "Use Net-net to compare a non-financial company's price with current assets "
        "minus ALL liabilities and preferred claims. Review asset recoverability and fraud risk.",
        "A net-net is not cash in your pocket. Receivables and inventory may be worth less "
        "than reported. Merger/arbitrage outcomes need separate event, legal and funding work.",
        ("contents", "principles", "ncav"),
    ),
    BookLesson(
        8,
        "Mr. Market: price is an offer, not an instruction",
        "The market offers changing prices. You may ignore them. Separate a company's "
        "earning ability from today's crowd mood, and distinguish a quote falling from "
        "a business permanently losing value.",
        "A classmate offering INR 60 for your calculator does not make it broken. But "
        "if the calculator really is broken, its old INR 100 price is no protection.",
        "Write a value range before checking the quote. Revisit the business thesis "
        "before adding, holding or selling. Use the Margin worksheet to test your assumptions.",
        "This is a behavioural principle, not 'buy every dip' or a mechanical sell rule. "
        "The app cannot decide whether a falling price is temporary or justified.",
        ("contents", "market", "safety"),
    ),
    BookLesson(
        9,
        "Funds: look past a winning leaderboard",
        "A fund can provide diversification and professional administration, but fees, "
        "incentives, portfolio risk and the price paid still matter. Recent top performance "
        "is not a reliable promise of future outperformance.",
        "Choosing a cricket team only from last week's highest scores ignores pitch, "
        "opposition and the cost of recruiting the players.",
        "Compare an Indian fund's scheme document, expense ratio, benchmark, portfolio, "
        "tracking difference and exit load. Compare like-for-like categories and dates.",
        "Modern Indian direct plans and index products are local applications, not names "
        "from Graham's original US text. The app does not rank or fetch fund schemes.",
    ),
    BookLesson(
        10,
        "Advisers: understand incentives",
        "Help is useful when you understand what the adviser does, how they are paid "
        "and what they cannot know. A confident forecast or impressive title is not evidence.",
        "A tutor paid for learning and a salesperson paid for selling more books may "
        "both sound helpful, but their incentives differ.",
        "Verify an Indian adviser's applicable SEBI registration, fees, conflicts, "
        "custody arrangements and written scope using the regulator's current records.",
        "The app does not verify registrations or replace professional judgement. "
        "Never share broker passwords or send money because a screen shows a low ratio.",
        ("contents", "sebi"),
    ),
    BookLesson(
        11,
        "Security analysis: facts before forecasts",
        "Study balance-sheet strength, earning power, dividends and the price paid. "
        "For bonds, ability to service debt matters. For shares, a forecast is an "
        "uncertain input, not a fact just because a calculator prints decimals.",
        "Two students can enter different growth guesses in the same spreadsheet and "
        "get very different values without changing the business at all.",
        "Use dated consolidated annual reports and the Fundamental workbook. "
        "Compare the earnings yield with a separately researched Indian bond yield, "
        "without treating risky equity earnings as guaranteed bond interest.",
        "The popular EPS x (8.5 + 2g) expression is discussed historically, with warnings; "
        "it is NOT a dependable buy-price oracle. Later bond-yield variants are not silently "
        "presented as this book's operational strategy.",
        ("contents", "number", "growth", "aaii"),
    ),
    BookLesson(
        12,
        "EPS: smooth cycles and inspect dilution",
        "Earnings per share means profit belonging to one share. One-off gains, charges, "
        "changing share counts and accounting choices can distort it. Read several years "
        "and compare basic with diluted EPS.",
        "A shop earning INR 300 for three owners earns INR 100 each. With six equal "
        "owners and unchanged profit, it earns INR 50 each.",
        "Enter the latest three annual diluted EPS values on a consistent split-adjusted "
        "basis. Their arithmetic average feeds the historical P/E check. Read exceptional "
        "items and cash-flow notes before calling the average normal earning power.",
        "Three annual observations are not ten years of stability. TTM EPS is a separate "
        "reference and never silently substituted for the three-year average.",
        ("contents", "number", "aaii"),
    ),
    BookLesson(
        13,
        "Compare businesses using the same yardstick",
        "Compare profitability, financial strength, growth and valuation together. "
        "The best-known company is not necessarily the best purchase at today's price.",
        "A better phone can still be a worse deal if it costs four times as much for "
        "only a small improvement.",
        "Run the same workbook for comparable Indian businesses with matching fiscal "
        "periods and accounting basis. Record differences in debt, EPS quality and valuation.",
        "The chapter's four US companies are historical teaching cases, not today's "
        "Indian equivalents. This is a repeatable comparison checklist, not a bulk screener.",
    ),
    BookLesson(
        14,
        "Defensive selection: seven evidence checks",
        "The historical checklist examines size, financial strength, stable earnings, "
        "dividends, earnings growth and restrained earnings/book multiples. Cheapness "
        "alone is not enough.",
        "A low-priced helmet is not a bargain if it fails the safety checks. Inspect "
        "both quality and price rather than averaging one away with the other.",
        "Use Defensive checks for industrial companies: current ratio at least 2, "
        "long-term debt no greater than working capital, 10 positive EPS years, 20 "
        "unbroken dividend years and at least one-third EPS growth over a decade using "
        "three-year endpoint averages. Inspect P/E 15, P/B 1.5 and their 22.5 product.",
        "Original size examples were USD 100m industrial sales / USD 50m utility assets "
        "in their historical setting. Choose and document a modern INR sales floor; "
        "the app does not invent an inflation/FX conversion. Banks, insurers and utilities "
        "require different analysis. Missing evidence is Unknown, never Pass.",
        ("contents", "criteria", "number", "aaii"),
    ),
    BookLesson(
        15,
        "Enterprising selection: more work, not magic",
        "Graham also explores cheaper, less stringently selected industrial companies. "
        "This is not permission to ignore debt or accept a business you do not understand.",
        "Renovating a cheaper house can work only if you inspect it more carefully "
        "and budget for the problems the first buyer avoided.",
        "The workbook shows historical research checks: current ratio 1.5, debt up to "
        "110% of working capital, no loss in five years, a current dividend, improving "
        "earnings, low P/E and price below 120% of tangible book value.",
        "The original earnings comparison uses a named historical year; this workbook "
        "explicitly adapts it to a user-supplied five-year-ago EPS. This partial industrial "
        "checklist is not a universal Graham grading system or a sell-timing algorithm.",
        ("contents", "criteria", "aaii"),
    ),
    BookLesson(
        16,
        "Convertibles and warrants: count the extra claims",
        "A convertible may become shares; a warrant gives a right to buy shares. "
        "The optional upside has a price, and extra shares can dilute existing owners. "
        "A bond label does not remove credit risk.",
        "A pizza divided into twelve slices instead of eight gives each slice a "
        "smaller claim on the same pizza.",
        "Read an Indian issuer's conversion terms, exercise price, expiry, coupon, "
        "seniority and diluted EPS. Calculate conversion value as shares received "
        "times share price and compare it with the security price.",
        "Terms are instrument-specific. The app does not price convertible options, "
        "model conversion cash flows or assume a distressed bond will repay principal.",
    ),
    BookLesson(
        17,
        "Case histories: recognise financial warning signs",
        "Famous names and rapid expansion do not cancel weak finances. Historical "
        "cases illustrate how debt, aggressive accounting, acquisitions and promotional "
        "valuations can destroy apparently impressive businesses.",
        "A student borrowing money to look wealthy is different from a student earning "
        "and saving. Growth bought with fragile borrowing needs investigation.",
        "For a company you study, trace operating cash flow versus profits, borrowing, "
        "related-party transactions, auditor qualifications and acquisition funding.",
        "This is an original checklist inspired by the chapter's role, not a retelling "
        "of its four cases or an automated fraud detector.",
    ),
    BookLesson(
        18,
        "Paired comparisons: business quality versus price",
        "Putting two businesses side by side exposes stories that a single impressive "
        "number can hide. Compare the price of quality, not just company size or popularity.",
        "Two shops sell similar products. One earns more but costs ten times as much "
        "to buy; deciding which is the better investment needs both figures.",
        "Compare Indian industry peers using the same worksheet and report dates. "
        "Explain differences in margins, debt, capital needs, governance and price.",
        "Eight historical US pairs are not a rule that today's lowest P/E peer wins. "
        "Banking and manufacturing ratios are not directly interchangeable.",
    ),
    BookLesson(
        19,
        "Owners, managers and dividends",
        "Shareholders should examine how managers use profits: reinvestment, dividends, "
        "buybacks or acquisitions. Keeping profits is justified by useful results, "
        "not by a claim that all growth is automatically good.",
        "If a school club keeps members' surplus to buy equipment, members should ask "
        "whether the equipment actually improves the club.",
        "Use Dividend arithmetic to calculate yield and payout. Read Indian dividend "
        "announcements, cash flows, capital allocation, promoter pledges and voting materials.",
        "A high yield can precede a dividend cut. A payout above earnings is a prompt "
        "to investigate, not proof of fraud. Tax and buyback rules require current local sources.",
    ),
    BookLesson(
        20,
        "Margin of safety: leave room for being wrong",
        "Pay sufficiently less than a conservatively assessed value to allow for "
        "mistakes and bad surprises. Diversification complements the cushion; neither "
        "guarantees against losses or makes a poor business safe.",
        "For an explicitly assumed INR 200 value and INR 140 price, the discount to "
        "value is 30%. That is not the same as the 42.86% rise needed to reach INR 200.",
        "Use Margin with your own value estimate and required discount. Use Valuation "
        "to inspect sqrt(22.5 x three-year average EPS x book value), a price-ratio bound, "
        "not independently proven intrinsic value. Recheck the thesis before selling.",
        "There is no universal safe discount and no guarantee of price convergence. "
        "The app does not automatically trade these notes or backtest today's fundamentals "
        "as if they had been known years ago.",
        ("contents", "safety", "number", "ncav"),
    ),
)


@dataclass(frozen=True)
class InputField:
    key: str
    title: str
    help: str
    signed: bool = False


FIELDS = (
    InputField(
        "price", "Completed close (INR/share)", "Unadjusted Close, not adjusted research units."
    ),
    InputField(
        "eps1", "Latest annual diluted EPS (INR)", "Full fiscal year, consistent share basis.", True
    ),
    InputField(
        "eps2", "Prior annual diluted EPS (INR)", "The immediately preceding fiscal year.", True
    ),
    InputField("eps3", "Third annual diluted EPS (INR)", "The next preceding fiscal year.", True),
    InputField(
        "ttm_eps", "TTM EPS (INR, reference)", "Trailing twelve months; NOT three-year EPS.", True
    ),
    InputField(
        "book", "Book value per share (INR)", "Common equity per share, not tangible book.", True
    ),
    InputField(
        "tangible",
        "Tangible book/share (INR)",
        "Net tangible common assets/share; check goodwill.",
        True,
    ),
    InputField("assets", "Current assets (INR crore)", "Use one dated consolidated balance sheet."),
    InputField(
        "current_liabilities", "Current liabilities (INR crore)", "Same statement date as assets."
    ),
    InputField(
        "liabilities", "ALL liabilities (INR crore)", "Not only borrowings or current liabilities."
    ),
    InputField(
        "preferred", "Preferred claims (INR crore)", "Enter 0 only after verifying no such claims."
    ),
    InputField("shares", "Ordinary shares (crore)", "Match period and per-share/split basis."),
    InputField("long_debt", "Long-term debt (INR crore)", "Do not replace with all liabilities."),
    InputField(
        "debt", "Total debt (INR crore)", "Interest-bearing debt for the enterprising check."
    ),
    InputField(
        "sales", "Annual sales (INR crore)", "Full fiscal year, not an undisclosed TTM proxy."
    ),
    InputField(
        "sales_floor",
        "Your size floor (INR crore)",
        "Your local adaptation, not Graham's US dollars.",
    ),
    InputField(
        "positive_years",
        "Consecutive positive EPS years",
        "Verified run ending in latest fiscal year.",
    ),
    InputField(
        "no_loss_years",
        "Consecutive no-loss EPS years",
        "Zero is not a loss; verified annual history.",
    ),
    InputField(
        "dividend_years", "Consecutive dividend years", "Verified uninterrupted annual payments."
    ),
    InputField(
        "old_average",
        "Decade-earlier 3-year EPS mean",
        "Comparable 3-year window ten years earlier.",
        True,
    ),
    InputField(
        "old_eps",
        "Five-year-ago annual EPS (INR)",
        "Explicit rolling-year adaptation for Ch. 15.",
        True,
    ),
    InputField(
        "dividend", "Annual dividend/share (INR)", "Verified current annual/last-12-month payments."
    ),
    InputField(
        "value",
        "Your estimated value/share (INR)",
        "An assumption, not a value supplied by this app.",
    ),
    InputField(
        "discount",
        "Your required discount (%)",
        "0 to less than 100; no universal safe percentage.",
    ),
    InputField(
        "bond_yield",
        "Comparable bond yield (%)",
        "User-researched; equity earnings are NOT interest.",
    ),
)
FIELD_MAP = {field.key: field for field in FIELDS}


@dataclass(frozen=True)
class Finding:
    title: str
    status: str
    detail: str


def validate_values(values: dict[str, float]) -> None:
    for key, value in values.items():
        if key not in FIELD_MAP:
            raise DataError(f"Unknown workbook field: {key}")
        if not math.isfinite(value) or abs(value) > 1e15:
            raise DataError(f"{FIELD_MAP[key].title}: enter a finite number within +/-1e15.")
        if 0 < abs(value) < 1e-12:
            raise DataError(f"{FIELD_MAP[key].title}: nonzero magnitudes must be at least 1e-12.")
        if value < 0 and not FIELD_MAP[key].signed:
            raise DataError(f"{FIELD_MAP[key].title}: cannot be negative.")
        if key.endswith("_years") and value != int(value):
            raise DataError(f"{FIELD_MAP[key].title}: enter a whole number of years.")
        if key == "discount" and value >= 100:
            raise DataError("Required discount must be below 100%.")
        if key in {"price", "shares", "value"} and value <= 0:
            raise DataError(f"{FIELD_MAP[key].title}: must be positive.")


def evaluate(values: dict[str, float], *, industrial: bool) -> dict[str, tuple[Finding, ...]]:
    """Missing evidence remains Unknown; never score incomplete screens as passes."""
    validate_values(values)
    derived = dict(values)
    if all(key in values for key in ("eps1", "eps2", "eps3")):
        derived["average"] = fmean(values[key] for key in ("eps1", "eps2", "eps3"))
    if all(key in values for key in ("assets", "current_liabilities")):
        derived["working"] = values["assets"] - values["current_liabilities"]
    sections: dict[str, list[Finding]] = {
        key: [] for key in ("Valuation", "Defensive", "Enterprising")
    }

    def check(
        section: str,
        title: str,
        keys: tuple[str, ...],
        condition: bool,
        formula: str,
        *,
        sector: bool = False,
    ) -> None:
        missing = [key for key in keys if key not in derived]
        if sector and not industrial:
            item = Finding(title, "Not applicable", "Classify as a non-financial industrial first.")
        elif missing:
            item = Finding(title, "Unknown", "Missing: " + ", ".join(missing) + ". " + formula)
        else:
            evidence = ", ".join(f"{key}={derived[key]:,.4g}" for key in keys)
            item = Finding(title, "Pass" if condition else "Fail", f"{formula} Inputs: {evidence}")
        sections[section].append(item)

    def get(key: str) -> float:
        # Placeholder is never rendered or scored when any required input is missing.
        return derived.get(key, 0.0)

    price, average, book = get("price"), get("average"), get("book")
    pe = price / average if average > 0 else None
    pb = price / book if book > 0 else None
    if "average" in derived:
        sections["Valuation"].append(
            Finding(
                "Three-year EPS mean",
                "Calculated",
                f"(EPS1 + EPS2 + EPS3) / 3 = INR {average:,.4f}. "
                "Not automatically normalised for exceptional items.",
            )
        )
    if pe is not None and "price" in values:
        sections["Valuation"].append(
            Finding(
                "P/E and earnings yield",
                "Calculated",
                f"P / mean EPS = {pe:,.4f}; mean EPS / P x 100 = {average / price * 100:,.4f}%. "
                "Earnings are not a promised cash distribution.",
            )
        )
    bound = math.sqrt(22.5 * average * book) if average > 0 and book > 0 else None
    sections["Valuation"].append(
        Finding(
            "Graham price-ratio bound",
            "Calculated" if bound is not None else "Unknown",
            f"sqrt(22.5 x mean EPS x book/share) = INR {bound:,.4f}. "
            "Not proven intrinsic value or a complete quality screen."
            if bound is not None
            else "Needs three annual EPS values with positive mean and positive "
            "book/share. Negative inputs must not produce a misleading square-root valuation.",
        )
    )
    if price > 0 and get("value") > 0:
        value = values["value"]
        sections["Valuation"].append(
            Finding(
                "Discount to YOUR value",
                "Calculated",
                f"(value - P) / value x 100 = {(value - price) / value * 100:,.4f}%. "
                f"Rise to value = {(value / price - 1) * 100:,.4f}%. Value is your assumption.",
            )
        )
    else:
        sections["Valuation"].append(
            Finding(
                "Discount to YOUR value",
                "Unknown",
                "Needs a positive price and your value estimate.",
            )
        )
    check(
        "Valuation",
        "Your required margin",
        ("price", "value", "discount"),
        price <= get("value") * (1 - get("discount") / 100),
        "P <= your value x (1 - your discount/100); not a recommendation.",
    )
    if all(key in values for key in ("value", "discount")):
        sections["Valuation"].append(
            Finding(
                "Your maximum price",
                "Calculated",
                f"INR {values['value'] * (1 - values['discount'] / 100):,.4f} "
                "under your assumptions.",
            )
        )
    check(
        "Valuation",
        "Earnings yield versus your bond benchmark",
        ("price", "average", "bond_yield"),
        average > 0 and price > 0 and average / price * 100 >= get("bond_yield"),
        "mean EPS/P x 100 >= benchmark yield; different risks, not equivalent returns.",
    )
    ncav_keys = ("assets", "liabilities", "preferred", "shares")
    if all(key in values for key in ncav_keys):
        ncav = (values["assets"] - values["liabilities"] - values["preferred"]) / values["shares"]
        derived["ncav"] = ncav
        sections["Valuation"].append(
            Finding(
                "Net-net asset arithmetic",
                "Calculated" if industrial else "Not applicable",
                f"(current assets - ALL liabilities - preferred claims) / ordinary shares = "
                f"INR {ncav:,.4f}/share; 2/3 = INR {ncav * 2 / 3:,.4f}. "
                "Totals and share count both use crore; no assumed liquidation recovery.",
            )
        )
    check(
        "Valuation",
        "Historical net-net price test",
        ("price", "ncav"),
        get("ncav") > 0 and price <= get("ncav") * 2 / 3,
        "Positive NCAV and P <= 2/3 x NCAV/share.",
        sector=True,
    )

    check(
        "Defensive",
        "1. Size (your Indian adaptation)",
        ("sales", "sales_floor"),
        get("sales") >= get("sales_floor"),
        "Annual INR crore sales >= your chosen floor.",
        sector=True,
    )
    check(
        "Defensive",
        "2a. Current strength",
        ("assets", "current_liabilities"),
        get("current_liabilities") > 0 and get("assets") >= 2 * get("current_liabilities"),
        "Current liabilities > 0; current assets >= 2 x current liabilities.",
        sector=True,
    )
    check(
        "Defensive",
        "2b. Debt cushion",
        ("long_debt", "working"),
        get("working") >= 0 and get("long_debt") <= get("working"),
        "Working capital = current assets - current liabilities; long-term debt <= it.",
        sector=True,
    )
    check(
        "Defensive",
        "3. Earnings stability",
        ("positive_years",),
        get("positive_years") >= 10,
        "At least 10 consecutive positive annual EPS years.",
        sector=True,
    )
    check(
        "Defensive",
        "4. Dividend record",
        ("dividend_years",),
        get("dividend_years") >= 20,
        "At least 20 uninterrupted dividend years.",
        sector=True,
    )
    check(
        "Defensive",
        "5. Decade growth",
        ("average", "old_average"),
        get("old_average") > 0 and average >= get("old_average") * 4 / 3,
        "Comparable three-year EPS endpoint means: latest >= 4/3 x decade-earlier.",
        sector=True,
    )
    check(
        "Defensive",
        "6. Historical P/E guide",
        ("price", "average"),
        pe is not None and 0 < pe <= 15,
        "P / three-year mean EPS <= 15; mean must be positive.",
        sector=True,
    )
    check(
        "Defensive",
        "7. Book/earnings price guide",
        ("price", "average", "book"),
        pe is not None and pb is not None and (pb <= 1.5 or pe * pb <= 22.5),
        "Positive mean EPS and book/share; P/B <= 1.5 OR (P/E x P/B <= 22.5). "
        "Inspect the separate P/E result too.",
        sector=True,
    )
    check(
        "Enterprising",
        "Current strength",
        ("assets", "current_liabilities"),
        get("current_liabilities") > 0 and get("assets") >= 1.5 * get("current_liabilities"),
        "Current assets >= 1.5 x positive current liabilities.",
        sector=True,
    )
    check(
        "Enterprising",
        "Debt",
        ("debt", "working"),
        get("working") >= 0 and get("debt") <= 1.1 * get("working"),
        "Total debt <= 110% of nonnegative working capital.",
        sector=True,
    )
    check(
        "Enterprising",
        "Earnings record",
        ("no_loss_years",),
        get("no_loss_years") >= 5,
        "At least five consecutive annual periods without a deficit.",
        sector=True,
    )
    check(
        "Enterprising",
        "Current dividend",
        ("dividend",),
        get("dividend") > 0,
        "Some verified current annual dividend.",
        sector=True,
    )
    check(
        "Enterprising",
        "Growth (rolling-year adaptation)",
        ("eps1", "old_eps"),
        get("eps1") > get("old_eps"),
        "Latest annual EPS > user-supplied five-year-ago EPS; not the original named year.",
        sector=True,
    )
    check(
        "Enterprising",
        "Low P/E research guide",
        ("price", "ttm_eps"),
        get("ttm_eps") > 0 and price <= 10 * get("ttm_eps"),
        "P <= 10 x positive TTM EPS; historical low-multiple research filter.",
        sector=True,
    )
    check(
        "Enterprising",
        "Tangible asset price",
        ("price", "tangible"),
        get("tangible") > 0 and price < 1.2 * get("tangible"),
        "P < 120% of positive tangible book/share (not ordinary book/share).",
        sector=True,
    )
    if price > 0 and "dividend" in values:
        sections["Valuation"].append(
            Finding(
                "Dividend arithmetic",
                "Calculated",
                f"Dividend / P x 100 = {values['dividend'] / price * 100:,.4f}% yield. "
                + (
                    "Dividend / latest EPS x 100 = "
                    f"{values['dividend'] / values['eps1'] * 100:,.4f}% "
                    "payout."
                    if get("eps1") > 0
                    else "Payout unavailable without positive latest EPS."
                ),
            )
        )
    return {key: tuple(rows) for key, rows in sections.items()}


def real_return(nominal: float, inflation: float) -> float:
    if not all(math.isfinite(x) and x > -100 for x in (nominal, inflation)):
        raise DataError("Return and inflation must be finite and greater than -100%.")
    result = ((1 + nominal / 100) / (1 + inflation / 100) - 1) * 100
    if not math.isfinite(result):
        raise DataError("Inputs exceed the supported real-return arithmetic range.")
    return result


def rebalance(stocks: float, bonds: float, target: float) -> float:
    if not all(math.isfinite(x) and x >= 0 for x in (stocks, bonds, target)) or target > 100:
        raise DataError("Values must be finite/nonnegative; share target must be 0%-100%.")
    if stocks + bonds <= 0:
        raise DataError("Enter a positive portfolio value.")
    result = (stocks + bonds) * (target / 100) - stocks
    if not math.isfinite(result):
        raise DataError("Inputs exceed the supported allocation arithmetic range.")
    return result


def equal_money(amount: float, prices: tuple[float, ...]) -> tuple[float, float]:
    if not prices or not all(math.isfinite(x) and x > 0 for x in (amount, *prices)):
        raise DataError("Enter a positive amount and positive finite purchase prices.")
    units = sum(amount / price for price in prices)
    if not math.isfinite(units) or units <= 0:
        raise DataError("Inputs exceed the supported purchase-unit arithmetic range.")
    cost = amount * len(prices) / units
    if not math.isfinite(cost) or cost <= 0:
        raise DataError("Inputs exceed the supported average-cost arithmetic range.")
    return units, cost
