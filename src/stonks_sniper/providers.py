from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo

from stonks_sniper.models import Candle, DataError, MarketData

INDIA = ZoneInfo("Asia/Kolkata")


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
            candles.append(
                Candle(
                    session,
                    float(row["Open"]),
                    float(row["High"]),
                    float(row["Low"]),
                    float(row["Close"]),
                    float(row["Volume"]),
                )
            )
        if not candles:
            raise DataError(
                f"Yahoo returned no usable completed daily candles for {ticker_symbol} "
                f"between {start} and {end}. Current-day observations are excluded."
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
