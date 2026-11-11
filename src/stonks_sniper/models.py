from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime


class DataError(ValueError):
    """Market data cannot safely be used for this experiment."""


@dataclass(frozen=True)
class Candle:
    session: date
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        prices = (self.open, self.high, self.low, self.close)
        if not all(math.isfinite(value) and value > 0 for value in prices):
            raise DataError(f"{self.session}: prices must be finite and positive.")
        if not math.isfinite(self.volume) or self.volume < 0:
            raise DataError(f"{self.session}: volume must be finite and nonnegative.")
        tolerance = self.high * 1e-8
        if self.low > min(prices) + tolerance or self.high < max(prices) - tolerance:
            raise DataError(f"{self.session}: inconsistent OHLC bounds.")


@dataclass(frozen=True)
class MarketData:
    symbol: str
    exchange: str
    candles: tuple[Candle, ...]
    fetched_at: datetime
    source: str
    price_basis: str
    warnings: tuple[str, ...] = ()
    currency: str = "INR"
    interval: str = "1d"

    def __post_init__(self) -> None:
        if not self.candles:
            raise DataError("The provider returned no usable completed daily candles.")
        if self.fetched_at.tzinfo is None or self.fetched_at.utcoffset() is None:
            raise DataError("Fetch time must include a timezone.")
        sessions = [candle.session for candle in self.candles]
        if sessions != sorted(set(sessions)):
            raise DataError("Sessions must be unique and strictly increasing.")
        if not self.source or not self.price_basis:
            raise DataError("Provider and price-basis provenance are required.")
