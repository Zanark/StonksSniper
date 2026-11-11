from __future__ import annotations

import logging
import math
import re
from datetime import date, datetime, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo

from stonks_sniper.models import Candle, DataError, MarketData

INDIA = ZoneInfo("Asia/Kolkata")
LOGGER = logging.getLogger(__name__)


class MarketDataProvider(Protocol):
    """Future broker adapters return the same validated, provenance-bearing contract."""

    def fetch(self, symbol: str, exchange: str, start: date, end: date) -> MarketData: ...


def yahoo_symbol(symbol: str, exchange: str) -> str:
    symbol = symbol.strip().upper()
    if exchange not in {"NSE", "BSE"}:
        raise DataError("Select NSE or BSE.")
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9&.-]{0,29}", symbol):
        raise DataError("Enter a Yahoo exchange ticker, for example RELIANCE.")
    if symbol.endswith((".NS", ".BO")):
        suffix = ".NS" if exchange == "NSE" else ".BO"
        if not symbol.endswith(suffix):
            raise DataError("Ticker suffix and selected exchange disagree.")
        return symbol
    return symbol + (".NS" if exchange == "NSE" else ".BO")


class YahooDailyProvider:
    """Unofficial personal-research adapter; no fallback or fabricated observations."""

    def fetch(self, symbol: str, exchange: str, start: date, end: date) -> MarketData:
        import yfinance as yf
        from yfinance.exceptions import YFException

        ticker_symbol = yahoo_symbol(symbol, exchange)
        today = datetime.now(INDIA).date()
        if start >= end or end > today:
            raise DataError("Start must precede end; end cannot be after today.")
        try:
            ticker = yf.Ticker(ticker_symbol)
            frame = ticker.history(
                start=start.isoformat(),
                end=(end + timedelta(days=1)).isoformat(),
                interval="1d",
                auto_adjust=True,
                actions=False,
                repair=False,
                raise_errors=True,
                timeout=20,
            )
            metadata = ticker.history_metadata
        except (YFException, OSError, ValueError, KeyError) as error:
            raise DataError(
                f"Yahoo could not supply {ticker_symbol}: {type(error).__name__}: {error}"
            ) from error
        if metadata.get("currency") != "INR":
            raise DataError("Provider currency is absent or not INR; refusing ambiguous data.")
        provider_exchange = metadata.get("exchangeName")
        allowed = {"NSE": {"NSI"}, "BSE": {"BSE"}}[exchange]
        if provider_exchange not in allowed:
            raise DataError(f"Provider exchange {provider_exchange!r} does not match {exchange}.")
        candles: list[Candle] = []
        excluded_current = False
        missing_sessions: list[date] = []
        for timestamp, row in frame.iterrows():
            if timestamp.tzinfo is None:
                raise DataError("Provider returned timezone-naive session timestamps.")
            session = timestamp.tz_convert(INDIA).date()
            # Today's bar may still change even after close; only prior dates are admitted.
            if session >= today:
                excluded_current = True
                continue
            if not start <= session <= end:
                raise DataError("Provider returned a session outside the requested range.")
            prices = tuple(float(row[key]) for key in ("Open", "High", "Low", "Close"))
            # A missing adjusted close can make yfinance's entire adjusted OHLC row NaN.
            if all(math.isnan(value) for value in prices):
                missing_sessions.append(session)
                continue
            candles.append(
                Candle(
                    session,
                    prices[0],
                    prices[1],
                    prices[2],
                    prices[3],
                    float(row["Volume"]),
                )
            )
        missing_warning = ""
        if missing_sessions:
            missing_warning = (
                f"Excluded {len(missing_sessions)} provider row(s) with missing OHLC prices: "
                + ", ".join(str(session) for session in missing_sessions)
                + ". Prices were not filled or replaced; history has gaps and strategies "
                "use only the remaining observations."
            )
            LOGGER.warning("%s: %s", ticker_symbol, missing_warning)
        if not candles:
            raise DataError(
                f"Yahoo returned no usable completed daily candles for {ticker_symbol} "
                f"between {start} and {end}. Current-day observations are excluded. "
                + missing_warning
            )
        warnings = [
            "Unofficial Yahoo access: personal research only; availability/accuracy "
            "not guaranteed.",
            "Adjusted research units, not historical tradable share prices. Dividends are not "
            "credited again; adjustments can revise past observations.",
            "Daily data only; current-day candles are excluded. This is not a live quote.",
            "No holiday-calendar completeness or cross-provider reconciliation yet.",
        ]
        if excluded_current:
            warnings.append(
                "The provider's current-day bar was excluded as potentially incomplete."
            )
        if missing_warning:
            warnings.append(missing_warning)
        if candles and (today - candles[-1].session).days > 7:
            warnings.append(
                "Last observation is over seven calendar days old. Historical range, "
                "suspension, holidays or stale provider data may explain this; not verified fresh."
            )
        return MarketData(
            ticker_symbol,
            exchange,
            tuple(candles),
            datetime.now(INDIA),
            "Yahoo Finance via yfinance (unofficial)",
            "Yahoo split/dividend-adjusted OHLC (auto_adjust=True); total-return research proxy",
            tuple(warnings),
        )
