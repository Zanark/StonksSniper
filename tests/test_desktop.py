from __future__ import annotations

import json
import os
import time
from dataclasses import replace
from importlib.resources import files
from pathlib import Path
from threading import Event
from xml.etree import ElementTree

import pytest
from PIL import Image, ImageChops, ImageSequence

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication, QThread  # noqa: E402
from PySide6.QtGui import QBitmap, QImage, QMovie, QRegion  # noqa: E402
from PySide6.QtWidgets import QApplication, QFileDialog  # noqa: E402
from test_research import observations  # noqa: E402

from stonks_sniper.app import MainWindow  # noqa: E402
from stonks_sniper.engine import simulate  # noqa: E402
from stonks_sniper.models import DataError  # noqa: E402
from stonks_sniper.patterns import PATTERNS  # noqa: E402
from stonks_sniper.theme import application_icon  # noqa: E402

pytestmark = pytest.mark.usefixtures("qt_events")


def test_readme_artwork_uses_requested_palette_with_candle_exception():
    palette = {"#0A0E0F", "#192220", "#8AC8B1", "#B6CAD6", "#FFFFFF", "#BDBEBE"}

    def check(element, *, candles=False):
        candles = candles or element.get("id") == "candles"
        for attribute in ("fill", "stroke", "stop-color"):
            color = element.get(attribute, "").upper()
            if color.startswith("#"):
                assert color in palette or (candles and color == "#E88472")
        for child in element:
            check(child, candles=candles)

    images = Path(__file__).parents[1] / "docs" / "images"
    for path in [
        images / "readme-banner.svg",
        *(images / f"button-{name}.svg" for name in ("start", "guide", "download")),
        files("stonks_sniper") / "assets" / "logo.svg",
    ]:
        check(ElementTree.fromstring(path.read_text(encoding="utf-8")))
    with Image.open(str(files("stonks_sniper") / "assets" / "logo.gif")) as logo:
        for frame in ImageSequence.Iterator(logo):
            colors = frame.convert("RGBA").getcolors(256)
            assert colors is not None
            for _, (red, green, blue, alpha) in colors:
                color = f"#{red:02X}{green:02X}{blue:02X}"
                assert alpha == 0 or color in palette or color == "#E88472"


def test_header_logo_stays_static_with_motion_on_and_off():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        expected = window.windowIcon().pixmap(46, 46).toImage()
        assert window.brand_mark.movie() is None
        assert not window.brand_mark.pixmap().isNull()
        assert window.brand_mark.pixmap().toImage() == expected
        for enabled in (False, True):
            window.motion.setChecked(enabled)
            app.processEvents()
            assert window.brand_mark.movie() is None
            assert window.brand_mark.pixmap().toImage() == expected
        assert window.loading_movie.state() == QMovie.MovieState.NotRunning
        assert window.windowIcon().pixmap(46, 46).toImage().pixelColor(0, 0).alpha() == 0
    finally:
        window.close()
        window.deleteLater()
        app.processEvents()


def test_scope_has_blue_glass_shading_instead_of_a_flat_background():
    app = QApplication.instance() or QApplication([])
    still = application_icon().pixmap(256, 256).toImage()
    app.processEvents()
    upper_glass = still.pixelColor(116, 34)
    lower_glass = still.pixelColor(116, 220)
    assert upper_glass.lightness() > lower_glass.lightness() + 8
    assert upper_glass.blue() > upper_glass.red()


def test_animated_glass_keeps_the_chart_clear_without_opaque_palette_patches():
    with Image.open(str(files("stonks_sniper") / "assets" / "logo.gif")) as logo:
        square = logo.convert("RGB")
        for x, y in ((88, 88), (220, 88), (88, 264), (264, 264)):
            assert square.getpixel((x, y)) == (25, 34, 32)
            assert square.getpixel((x + 6, y + 6)) == (10, 14, 15)
        for index, frame in enumerate(ImageSequence.Iterator(logo)):
            colors = frame.convert("RGBA").getcolors(256)
            assert colors is not None
            opaque = sum(count for count, color in colors if color[3] == 255)
            clear = sum(count for count, color in colors if color == (10, 14, 15, 255))
            assert clear / opaque > 0.65, index


def test_gif_reveals_glass_only_on_the_circle_then_sweeps_a_finishing_shimmer():
    with Image.open(str(files("stonks_sniper") / "assets" / "logo.gif")) as logo:
        logo.seek(logo.n_frames - 1)
        still = logo.convert("RGBA")
        circle = still.getchannel("A").tobytes()
        reflection = (78, 65, 112, 95)
        reflection_colors = still.crop(reflection).getcolors()
        assert reflection_colors is not None
        assert any(
            color[:3] in {(182, 202, 214), (255, 255, 255)} for _, color in reflection_colors
        )
        logo.seek(0)
        elapsed = 0
        shimmer_centres = []
        for frame in ImageSequence.Iterator(logo):
            image = frame.convert("RGBA")
            if 3940 <= elapsed < 7280 and image.getchannel("A").tobytes() != circle:
                reflection_colors = image.crop(reflection).getcolors()
                assert reflection_colors is not None
                assert not any(
                    color[:3] in {(182, 202, 214), (255, 255, 255)}
                    for _, color in reflection_colors
                ), elapsed
            if elapsed >= 7280:
                assert image.getchannel("A").tobytes() == circle
                difference = ImageChops.difference(image.convert("RGB"), still.convert("RGB"))
                changed = difference.getbbox()
                if changed is not None:
                    shimmer_centres.append((changed[0] + changed[2]) / 2)
            elapsed += frame.info["duration"]
        assert len(shimmer_centres) >= 12
        assert min(shimmer_centres) < 100
        assert max(shimmer_centres) > 250


def test_exported_windows_browser_icon_matches_native_glass_at_each_resolution():
    app = QApplication.instance() or QApplication([])
    icon = application_icon()
    sizes = {16, 24, 32, 48, 64, 128, 256}
    assert {(size.width(), size.height()) for size in icon.availableSizes()} == {
        (size, size) for size in sizes
    }
    with Image.open(str(files("stonks_sniper") / "assets" / "logo.ico")) as exported:
        assert exported.ico.sizes() == {(size, size) for size in sizes}
        for size in sizes:
            actual = exported.ico.getimage((size, size)).convert("RGBA")
            native = (
                icon.pixmap(size, size).toImage().convertToFormat(QImage.Format.Format_RGBA8888)
            )
            expected = Image.frombytes("RGBA", (size, size), bytes(native.constBits()))
            assert actual.tobytes() == expected.tobytes(), size
            assert actual.getpixel((0, 0))[3] == 0
            assert actual.getpixel((size // 2, size // 2))[3] == 255
    app.processEvents()


def test_logo_morphs_smoothly_at_faster_speed_from_equal_square_to_transparent_circle():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        window.motion.setChecked(False)
        movie = QMovie(str(files("stonks_sniper") / "assets" / "logo.gif"))
        movie.setCacheMode(QMovie.CacheMode.CacheAll)
        assert movie.jumpToFrame(0)
        first = movie.currentImage()
        search_bounds = QRegion(QBitmap.fromImage(first.createAlphaMask())).boundingRect()
        assert search_bounds.width() == search_bounds.height()
        assert first.pixelColor(16, 80).alpha() == 255
        for frame in range(movie.frameCount()):
            assert movie.jumpToFrame(frame)
            bounds = QRegion(
                QBitmap.fromImage(movie.currentImage().createAlphaMask())
            ).boundingRect()
            assert bounds == search_bounds, frame
        final = movie.currentImage()
        assert final.pixelColor(16, 80).alpha() == 0
        assert final.pixelColor(327, 96).alpha() == 0
        assert final.pixelColor(176, 176).alpha() == 255
        still = window.windowIcon().pixmap(256, 256).toImage()
        assert still.pixelColor(238, 70).alpha() == 0
        assert still.pixelColor(128, 128).alpha() == 255
        with Image.open(str(files("stonks_sniper") / "assets" / "logo.gif")) as logo:
            coverage = [
                (frame.convert("RGBA").getchannel("A").histogram()[255], frame.info["duration"])
                for frame in ImageSequence.Iterator(logo)
            ]
        square, circle = coverage[0][0], coverage[-1][0]
        transition = [(area, duration) for area, duration in coverage if circle < area < square]
        assert len({area for area, _ in transition}) >= 50
        assert 2200 <= sum(duration for _, duration in transition) <= 2560
        assert sum(duration for _, duration in coverage) == 9080
        areas = [square, *(area for area, _ in transition), circle]
        steps = [before - after for before, after in zip(areas, areas[1:], strict=False)]
        assert all(step >= 0 for step in steps)
        assert max(steps) < (square - circle) / 15
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
