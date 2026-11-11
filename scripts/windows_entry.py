"""Native launcher and explicit, isolated frozen-runtime diagnostic."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QApplication, QFileDialog

from stonks_sniper import __version__
from stonks_sniper.app import MainWindow, lesson_html, main
from stonks_sniper.glossary import TERMS
from stonks_sniper.lessons import LESSONS
from stonks_sniper.patterns import PATTERNS
from stonks_sniper.providers import INDIA
from stonks_sniper.theme import LOGO, configure_application


def smoke_test(report: Path, *, live: bool) -> None:
    import yfinance as yf

    report.parent.mkdir(parents=True, exist_ok=True)
    if report.exists():
        raise FileExistsError(f"Refusing to overwrite diagnostic evidence: {report}")
    yf.set_tz_cache_location(str(report.parent / "yfinance-cache"))
    app = QApplication([])
    configure_application(app)
    window = MainWindow()
    window.motion.setChecked(False)
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
    window.resize(1366, 768)
    window.show()
    app.processEvents()
    checks: dict[str, object] = {
        "version": __version__,
        "frozen": bool(getattr(sys, "frozen", False)),
        "platform_plugin": app.platformName(),
        "strategies": len(PATTERNS),
        "lessons": len(LESSONS),
        "dictionary_entries": len(TERMS),
        "network_tested": live,
        "motion": False,
    }
    try:
        if window.windowIcon().isNull() or window.brand_mark.pixmap().isNull():
            raise RuntimeError("The packaged application icon could not be decoded.")
        if not window.loading_movie.isValid() or not window.loading_movie.jumpToFrame(0):
            raise RuntimeError("The packaged loading GIF could not be decoded.")
        logo_movie = QMovie(str(LOGO.with_suffix(".gif")))
        if not logo_movie.isValid() or not logo_movie.jumpToFrame(0):
            raise RuntimeError("The packaged animated logo could not be decoded.")
        for index, pattern in enumerate(PATTERNS):
            if pattern.key not in LESSONS or not lesson_html(index, complete=True):
                raise RuntimeError(f"Missing packaged lesson: {pattern.key}")
        if live:
            window.symbol.setText("HDFCBANK")
            window.fetch_data()
            deadline = time.monotonic() + 120
            while window.fetch_thread is not None and time.monotonic() < deadline:
                app.processEvents()
                time.sleep(0.01)
            if window.fetch_thread is not None:
                raise TimeoutError(
                    "The owned diagnostic data worker did not finish in 120 seconds."
                )
            if window.data is None:
                raise RuntimeError(window.provenance.text())
            results = []
            for index, pattern in enumerate(PATTERNS):
                window.pattern.setCurrentIndex(index)
                window.run_experiment()
                app.processEvents()
                if window.result is None or not all(
                    math.isfinite(value) for value in window.result.equity
                ):
                    raise RuntimeError(f"The packaged simulation failed: {pattern.key}")
                results.append({"strategy": pattern.key, "trades": len(window.result.trades)})
            exported = report.with_suffix(".experiment.json")
            if exported.exists():
                raise FileExistsError(f"Refusing to overwrite an experiment: {exported}")
            with patch.object(QFileDialog, "getSaveFileName", return_value=(str(exported), "JSON")):
                window.export.click()
            payload = json.loads(exported.read_text(encoding="utf-8"))
            if payload["observations"]["symbol"] != "HDFCBANK.NS":
                raise RuntimeError("The packaged export did not preserve the fetched stock.")
            checks.update(
                symbol=window.data.symbol,
                bars=len(window.data.candles),
                first_session=str(window.data.candles[0].session),
                last_session=str(window.data.candles[-1].session),
                warnings=window.data.warnings,
                simulations=results,
                exported=True,
            )
        if not window.grab().save(str(report.with_suffix(".png"))):
            raise OSError("Could not save the owned diagnostic window capture.")
        checks["checked_at"] = datetime.now(INDIA).isoformat()
        checks["ok"] = True
        with report.open("x", encoding="utf-8") as output:
            json.dump(checks, output, indent=2, allow_nan=False)
    finally:
        if window.fetch_thread is not None:
            window.fetch_thread.quit()
            window.fetch_thread.wait(30_000)
        window.close()
        window.deleteLater()
        app.processEvents()


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--smoke-test", required=True, type=Path, metavar="REPORT_JSON")
        parser.add_argument("--live", action="store_true", help="Fetch actual HDFCBANK history.")
        arguments = parser.parse_args()
        smoke_test(arguments.smoke_test, live=arguments.live)
    else:
        main()
