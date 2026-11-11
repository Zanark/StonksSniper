from __future__ import annotations

import json
import os
import time
from dataclasses import replace
from threading import Event

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication, QThread  # noqa: E402
from PySide6.QtGui import QMovie  # noqa: E402
from PySide6.QtWidgets import QApplication, QFileDialog  # noqa: E402
from test_research import observations  # noqa: E402

from stonks_sniper.app import MainWindow  # noqa: E402
from stonks_sniper.engine import simulate  # noqa: E402
from stonks_sniper.models import DataError  # noqa: E402
from stonks_sniper.patterns import PATTERNS  # noqa: E402


def test_circular_logo_animates_and_respects_motion_and_close():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        assert window.brand_movie.state() == QMovie.MovieState.Running
        assert window.brand_movie.currentImage().pixelColor(0, 0).alpha() == 0
        frame = window.brand_movie.currentFrameNumber()
        deadline = time.monotonic() + 1
        while window.brand_movie.currentFrameNumber() == frame and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.01)
        assert window.brand_movie.currentFrameNumber() != frame
        window.motion.setChecked(False)
        assert window.brand_movie.state() == QMovie.MovieState.Paused
        assert window.brand_mark.movie() is None
        assert not window.brand_mark.pixmap().isNull()
        frame = window.brand_movie.currentFrameNumber()
        deadline = time.monotonic() + 0.2
        while time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.01)
        assert window.brand_movie.currentFrameNumber() == frame
        window.motion.setChecked(True)
        assert window.brand_movie.state() == QMovie.MovieState.Running
        assert window.brand_mark.movie() is window.brand_movie
        assert window.loading_movie.state() == QMovie.MovieState.NotRunning
        assert window.windowIcon().pixmap(46, 46).toImage().pixelColor(0, 0).alpha() == 0
    finally:
        window.close()
        assert window.brand_movie.state() == QMovie.MovieState.NotRunning
        window.deleteLater()
        app.processEvents()


def test_logo_cuts_from_rectangle_to_transparent_circle():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        window.motion.setChecked(False)
        movie = QMovie(window.brand_movie.fileName())
        movie.setCacheMode(QMovie.CacheMode.CacheAll)
        assert movie.jumpToFrame(0)
        assert movie.currentImage().pixelColor(16, 80).alpha() == 255
        for frame in range(movie.frameCount()):
            assert movie.jumpToFrame(frame)
        final = movie.currentImage()
        assert final.pixelColor(16, 80).alpha() == 0
        assert final.pixelColor(327, 96).alpha() == 0
        assert final.pixelColor(176, 176).alpha() == 255
        still = window.windowIcon().pixmap(256, 256).toImage()
        assert still.pixelColor(238, 70).alpha() == 0
        assert still.pixelColor(128, 128).alpha() == 255
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()


def test_desktop_replay_hides_future_fills_and_recomputes_summary():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    data = observations()
    window.data_ready(data)
    assert window.result is not None
    assert window.export.isEnabled()
    window.replay.setValue(50)
    prefix = simulate(replace(data, candles=data.candles[:50]), PATTERNS[0])
    assert window.trades.rowCount() == len(prefix.trades)
    assert str(data.candles[49].session) in window.summary.text()
    assert f"{prefix.equity[-1]:,.2f}" in window.summary.text()
    window.pattern.setCurrentIndex(1)
    assert window.result is None
    assert not window.export.isEnabled()
    assert window.trades.rowCount() == 0
    window.close()
    window.deleteLater()
    QCoreApplication.sendPostedEvents()
    app.processEvents()


@pytest.mark.parametrize("fails", [False, True])
@pytest.mark.parametrize("motion", [False, True])
def test_fetch_uses_worker_and_clears_previous_run_on_failure(fails, motion, caplog):
    app = QApplication.instance() or QApplication([])
    release = Event()
    data = observations()
    threads = []
    requests = []

    class Provider:
        def fetch(self, *request):
            threads.append(QThread.currentThread())
            requests.append(request)
            if not release.wait(5):
                raise TimeoutError("Test did not release its owned worker")
            if fails:
                raise DataError("Explicit test provider failure")
            return data

    window = MainWindow(Provider())
    window.data_ready(data)
    window.motion.setChecked(motion)
    window.show()
    window.fetch_data()
    try:
        assert window.workspace.currentWidget() is window.loading_page
        assert window.loading_image.isVisible()
        assert "RELIANCE / NSE" in window.loading_status.text()
        assert window.loading_movie.state() == (
            QMovie.MovieState.Running if motion else QMovie.MovieState.Paused
        )
        frame = window.loading_movie.currentFrameNumber()
        deadline = time.monotonic() + (1 if motion else 0.1)
        while time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.01)
            if motion and window.loading_movie.currentFrameNumber() != frame:
                break
        assert (window.loading_movie.currentFrameNumber() != frame) is motion
        window.motion.setChecked(not motion)
        assert window.loading_movie.state() == (
            QMovie.MovieState.Paused if motion else QMovie.MovieState.Running
        )
        window.motion.setChecked(motion)
        assert window.data is None and window.result is None
        assert not window.export.isEnabled()
        assert not window.fetch.isEnabled()
        assert window.replay_label.text() == "No data"
        window.symbol.setText("CHANGED")
        window.close()
        assert window.isVisible()
    finally:
        release.set()
        deadline = time.monotonic() + 5
        while window.fetch_thread is not None and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.01)
        assert window.fetch_thread is None
    try:
        assert threads[0] != app.thread()
        assert requests[0][:2] == ("RELIANCE", "NSE")
        assert window.fetch.isEnabled()
        assert window.workspace.currentWidget() is window.tabs
        assert not window.loading_image.isVisible()
        assert window.loading_movie.state() == QMovie.MovieState.NotRunning
        window.motion.setChecked(not motion)
        assert window.loading_movie.state() == QMovie.MovieState.NotRunning
        if fails:
            assert window.data is None and window.result is None
            assert not window.export.isEnabled()
            assert "Explicit test provider failure" in window.provenance.text()
            assert "Fetch failed" in window.summary.text()
            assert window.trades.rowCount() == 0
            assert "Market-data fetch failed" in caplog.text
            assert "Explicit test provider failure" in caplog.text
        else:
            assert window.data is data and window.result is not None
            assert data.symbol in window.provenance.text()
            assert "CHANGED" not in window.provenance.text()
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()


def test_export_contains_full_run_provenance_and_replay_cursor(monkeypatch, tmp_path):
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    data = observations()
    window.data_ready(data)
    window.replay.setValue(50)
    destination = tmp_path / "experiment.json"
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", lambda *_: (str(destination), "JSON (*.json)")
    )
    try:
        window.export_run()
        payload = json.loads(destination.read_text(encoding="utf-8"))
        assert payload["observations"]["source"] == data.source
        assert len(payload["observations"]["candles"]) == len(data.candles)
        assert payload["observations"]["fetched_at"] == str(data.fetched_at)
        assert payload["replay_as_of"] == str(data.candles[49].session)
        assert payload["experiment"]["assumptions"]["initial_cash"] == 100_000
        assert payload["experiment"]["pattern"]["rules"] == PATTERNS[0].rules
        assert len(payload["experiment"]["equity"]) == len(data.candles)
        window.data_ready(replace(data, candles=data.candles[:5]))
        assert window.result is None
        assert not window.export.isEnabled()
        assert "needs at least 31 completed bars" in window.summary.text()
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()
