"""Opt-in real network check; no fixtures, purchases, broker calls or stored raw datasets."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from stonks_sniper.engine import simulate
from stonks_sniper.patterns import PATTERNS
from stonks_sniper.providers import INDIA, YahooDailyProvider


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--render", type=Path, help="Save an offscreen native UI image at this path."
    )
    parser.add_argument(
        "--gallery", type=Path, help="Save the native learning views and capture provenance here."
    )
    args = parser.parse_args()
    today = datetime.now(INDIA).date()
    provider = YahooDailyProvider()
    datasets = []
    for symbol, exchange in (("RELIANCE", "NSE"), ("TCS", "NSE"), ("TCS", "BSE")):
        data = provider.fetch(symbol, exchange, today - timedelta(days=730), today)
        datasets.append(data)
        results = [simulate(data, pattern) for pattern in PATTERNS]
        print(
            json.dumps(
                {
                    "symbol": data.symbol,
                    "exchange": data.exchange,
                    "currency": data.currency,
                    "first_observation": str(data.candles[0].session),
                    "last_observation": str(data.candles[-1].session),
                    "bars": len(data.candles),
                    "fetched_at": data.fetched_at.isoformat(),
                    "source": data.source,
                    "basis": data.price_basis,
                    "pattern_runs": [
                        {
                            "pattern": result.pattern.key,
                            "fills": len(result.trades),
                            "return_pct": round(result.return_pct, 4),
                        }
                        for result in results
                    ],
                }
            )
        )
    if args.render or args.gallery:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtCore import QCoreApplication, QEvent
        from PySide6.QtGui import QFontDatabase
        from PySide6.QtWidgets import QApplication

        from stonks_sniper.app import MainWindow, configure_application

        app = QApplication([])
        if sys.platform == "win32" and app.platformName() == "offscreen":
            # Qt's offscreen Windows plugin does not discover installed system fonts.
            font_path = Path(os.environ["WINDIR"]) / "Fonts" / "segoeui.ttf"
            if QFontDatabase.addApplicationFont(str(font_path)) < 0:
                raise RuntimeError(f"Could not load the installed UI font: {font_path}")
        configure_application(app)
        window = MainWindow()
        window.motion.setChecked(False)
        window.resize(1440, 900)
        window.data_ready(datasets[0])
        window.show()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()
        if args.render and not window.grab().save(str(args.render)):
            raise RuntimeError("Native UI screenshot could not be saved.")
        if args.gallery:
            destination = args.gallery.resolve()
            destination.mkdir(parents=True, exist_ok=True)
            captures = []

            def capture(name: str, width: int = 1440, height: int = 900) -> None:
                window.resize(width, height)
                QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
                app.processEvents()
                if (window.width(), window.height()) != (width, height):
                    raise RuntimeError(
                        f"Requested {width}x{height}, but the layout requires "
                        f"{window.width()}x{window.height()}: {name}"
                    )
                if not window.grab().save(str(destination / name)):
                    raise RuntimeError(f"Native UI screenshot could not be saved: {name}")
                captures.append({"file": name, "width": width, "height": height})

            window.price_style.setCurrentIndex(1)
            capture("01-explore.png")
            window.chart_tabs.setCurrentIndex(1)
            capture("02-money.png")
            window.chart_tabs.setCurrentIndex(3)
            capture("03-rule.png")
            window.pattern.setCurrentIndex(2)
            window.run_experiment()
            window.pattern_help.click()
            capture("04-pattern.png")
            window.open_glossary("drawdown")
            capture("05-dictionary.png")
            window.tabs.setCurrentIndex(0)
            window.chart_tabs.setCurrentIndex(0)
            window.price_style.setCurrentIndex(0)
            capture("06-compact.png", 1366, 768)
            data = datasets[0]
            receipt = {
                "captured_at": datetime.now(INDIA).isoformat(),
                "source": data.source,
                "symbol": data.symbol,
                "exchange": data.exchange,
                "currency": data.currency,
                "fetched_at": data.fetched_at.isoformat(),
                "first_observation": str(data.candles[0].session),
                "last_observation": str(data.candles[-1].session),
                "observations": len(data.candles),
                "price_basis": data.price_basis,
                "platform": app.platformName(),
                "motion": False,
                "captures": captures,
            }
            (destination / "captures.json").write_text(
                json.dumps(receipt, indent=2), encoding="utf-8"
            )
            print(f"Rendered real-data native gallery: {destination}")
        window.close()
        app.processEvents()
        if args.render:
            print(f"Rendered real-data native UI: {args.render}")


if __name__ == "__main__":
    main()
