"""Optional present-day Yahoo reference data; never point-in-time backtest inputs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime
from numbers import Real

from stonks_sniper.models import DataError
from stonks_sniper.providers import INDIA, yahoo_symbol


@dataclass(frozen=True)
class FundamentalValue:
    key: str
    value: float
    source: str


@dataclass(frozen=True)
class FundamentalSnapshot:
    symbol: str
    exchange: str
    fetched_at: datetime
    price_session: date
    sector: str
    values: tuple[FundamentalValue, ...]
    warnings: tuple[str, ...]


class YahooFundamentalsProvider:
    def fetch(self, symbol: str, exchange: str) -> FundamentalSnapshot:
        import yfinance as yf
        from yfinance.exceptions import YFException

        name = yahoo_symbol(symbol, exchange)
        today = datetime.now(INDIA).date()
        try:
            ticker = yf.Ticker(name)
            history = ticker.history(
                period="1mo",
                interval="1d",
                auto_adjust=False,
                actions=False,
                repair=False,
                raise_errors=True,
                timeout=20,
            )
            metadata = ticker.history_metadata
            info = ticker.get_info()
            balance = ticker.get_balance_sheet(pretty=False)
            income = ticker.get_income_stmt(pretty=False)
        except (YFException, OSError, ValueError, KeyError) as error:
            raise DataError(
                f"Yahoo fundamentals unavailable for {name}: {type(error).__name__}: {error}"
            ) from error
        allowed = {"NSE": "NSI", "BSE": "BSE"}[exchange]
        if metadata.get("currency") != "INR" or metadata.get("exchangeName") != allowed:
            raise DataError("Fundamental quote currency/exchange is absent or does not match.")
        values: list[FundamentalValue] = []
        warnings = [
            "Unofficial Yahoo reference, not audited or point-in-time data. "
            "Fetch time is NOT the date these facts became public.",
            "Completed unadjusted Close is separate from Explore's dividend-adjusted prices. "
            "Yahoo may still split-adjust history; verify a consistent per-share basis.",
            "Statement dates, book value, TTM EPS and quote date may differ. Verify annual "
            "reports and corporate actions before comparing. Blank fields are unavailable.",
            "No 10/20-year history is inferred from a short provider history. Missing "
            "preferred stock is NOT assumed zero. Dividend history requires manual evidence.",
        ]

        def append(key: str, raw: object, source: str, divisor: float = 1) -> None:
            if raw is None:
                return
            if not isinstance(raw, Real) or isinstance(raw, bool):
                warnings.append(f"{key}: provider value is nonnumeric; left unavailable.")
                return
            value = float(raw) / divisor
            if not math.isfinite(value):
                warnings.append(f"{key}: provider value is nonfinite; left unavailable.")
                return
            values.append(FundamentalValue(key, value, source))

        close: tuple[date, float] | None = None
        for timestamp, row in history.iterrows():
            if timestamp.tzinfo is None:
                raise DataError("Fundamental history has timezone-naive timestamps.")
            session = timestamp.tz_convert(INDIA).date()
            raw = float(row["Close"])
            if session < today and math.isfinite(raw) and raw > 0:
                if close is None or session > close[0]:
                    close = session, raw
        if close is None:
            raise DataError(f"No usable completed unadjusted Close for {name} in the last month.")
        append("price", close[1], f"Yahoo unadjusted Close, session {close[0]}, INR/share")
        if (today - close[0]).days > 7:
            warnings.append("Latest quote is over seven calendar days old; freshness unverified.")
        if info.get("financialCurrency") != "INR":
            warnings.append(
                "Statement currency is absent or not INR. No financial amounts were imported; "
                "verify currency and enter sourced INR figures manually."
            )
        else:
            append("ttm_eps", info.get("trailingEps"), "Yahoo trailingEps, period not verified")
            append("book", info.get("bookValue"), "Yahoo bookValue, period not verified")
            if balance.empty:
                warnings.append("Yahoo supplied no annual balance sheet; balance inputs unknown.")
            else:
                period = max(balance.columns)
                source = f"Yahoo annual balance sheet, period end {period.date()}"
                for key, row_name in (
                    ("assets", "CurrentAssets"),
                    ("current_liabilities", "CurrentLiabilities"),
                    ("liabilities", "TotalLiabilitiesNetMinorityInterest"),
                    ("shares", "OrdinarySharesNumber"),
                    ("long_debt", "LongTermDebt"),
                    ("debt", "TotalDebt"),
                ):
                    if row_name in balance.index:
                        append(key, balance.loc[row_name, period], f"{source}; {row_name}", 1e7)
            if income.empty:
                warnings.append("Yahoo supplied no annual income statement; annual EPS unknown.")
            else:
                periods = sorted(income.columns, reverse=True)
                period = periods[0]
                if "TotalRevenue" in income.index:
                    append(
                        "sales",
                        income.loc["TotalRevenue", period],
                        f"Yahoo annual income, period end {period.date()}; TotalRevenue",
                        1e7,
                    )
                if "DilutedEPS" in income.index:
                    selected = periods[:3]
                    consecutive = all(
                        300 <= (left - right).days <= 430
                        for left, right in zip(selected, selected[1:], strict=False)
                    )
                    if consecutive:
                        for index, period in enumerate(selected, 1):
                            append(
                                f"eps{index}",
                                income.loc["DilutedEPS", period],
                                f"Yahoo annual DilutedEPS, period end {period.date()}",
                            )
                    else:
                        warnings.append("Annual EPS periods are not consecutive; left unknown.")
        if info.get("sector") == "Financial Services":
            warnings.append(
                "Financial-sector company: industrial current-ratio/net-net screens do not apply. "
                "Use bank/insurer-specific capital, asset-quality and regulatory analysis."
            )
        return FundamentalSnapshot(
            name,
            exchange,
            datetime.now(INDIA),
            close[0],
            str(info.get("sector") or "Unclassified"),
            tuple(values),
            tuple(warnings),
        )
