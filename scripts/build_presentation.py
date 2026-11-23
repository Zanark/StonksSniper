"""Rebuild original branding and opt-in real-data native GIF demonstrations."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import subprocess
import sys
from collections.abc import Callable
from datetime import date, datetime
from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image  # noqa: E402
from PySide6.QtCore import (  # noqa: E402
    QCoreApplication,
    QDate,
    QEvent,
    QPoint,
    QPointF,
    QRectF,
    Qt,
)
from PySide6.QtGui import (  # noqa: E402
    QColor,
    QFont,
    QFontDatabase,
    QImage,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PySide6.QtSvg import QSvgRenderer  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSlider,
    QStyle,
    QStyleOptionSlider,
    QTabWidget,
    QWidget,
)

from stonks_sniper import __version__  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "src" / "stonks_sniper" / "assets"
IMAGES = ROOT / "docs" / "images"
BACKGROUND = "#0A0E0F"
GRID = "#192220"
GREEN = "#8AC8B1"
BLUE = "#B6CAD6"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#BDBEBE"
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)


def scope_svg(
    x: float = 64,
    y: float = 64,
    flash: float = 0,
    *,
    roundness: float = 1,
    bullet: float | None = None,
    palette_safe: bool = False,
    shimmer: float | None = None,
) -> str:
    """Illustrated branding, never market observations or a trading signal."""
    candles = ""
    for cx, opening, closing, high, low in (
        (12, 93, 79, 71, 102),
        (26, 80, 60, 53, 89),
        (40, 61, 73, 56, 84),
        (52, 74, 82, 66, 93),
        (64, 78, 50, 41, 88),
        (78, 51, 60, 38, 69),
        (92, 59, 43, 34, 72),
        (106, 44, 52, 29, 64),
        (119, 53, 35, 25, 65),
    ):
        color = GREEN if closing < opening else "#E88472"
        candles += (
            f'<path d="M{cx} {high}V{low}" stroke="{color}" stroke-width="1.5"/>'
            f'<rect x="{cx - 3.5}" y="{min(opening, closing)}" width="7" '
            f'height="{abs(opening - closing)}" fill="{color}"/>'
        )
    target = ""
    if bullet is not None:
        bx, by = 116 - 52 * bullet, 102 - 38 * bullet
        angle = math.degrees(math.atan2(-38, -52))
        target += (
            f'<g transform="translate({bx:.3f} {by:.3f}) rotate({angle:.3f})">'
            f'<path d="M-22 0H-6" stroke="{BLUE}" stroke-width="1.3" opacity=".7"/>'
            f'<path d="M-5 -1.6H2L5 0L2 1.6H-5Z" fill="{TEXT_PRIMARY}" stroke="{BLUE}" '
            'stroke-width=".5"/></g>'
        )
    if flash:
        target += (
            f'<circle cx="{x}" cy="{y}" r="{8 + 15 * flash}" fill="none" '
            f'stroke="{BLUE}" stroke-width="1.5" opacity="{flash}"/>'
            f'<path d="M64 53v22M53 64h22M56 56l16 16M56 72l16-16" '
            f'stroke="{TEXT_PRIMARY}" stroke-width="2" opacity="{flash}"/>'
            f'<circle cx="{x}" cy="{y}" r="4" fill="{TEXT_PRIMARY}" opacity="{flash}"/>'
        )
    outline = f'<rect x="5" y="5" width="118" height="118" rx="{59 * roundness:.5f}"'
    shape = f"{outline}/>"
    glass_enabled = roundness == 1
    surface = f'{outline} fill="{BACKGROUND}"/>'
    if glass_enabled and not palette_safe:
        surface += f'{outline} fill="url(#glass-depth)"/>'
    bezel = (
        '<rect x="10" y="10" width="108" height="108" '
        f'rx="{54 * roundness:.5f}" fill="none" stroke="{BACKGROUND}" '
        'stroke-width="6" stroke-opacity=".7"/>'
        f'{outline} fill="none" stroke="{GREEN}" stroke-width="1.5"/>'
        '<rect x="7.5" y="7.5" width="113" height="113" '
        f'rx="{56.5 * roundness:.5f}" fill="none" stroke="{BLUE}" '
        f'stroke-width=".7" stroke-opacity="{1 if palette_safe else 0.65}"/>'
    )
    # Broad gradients collapse into opaque bands in the exact seven-color GIF.
    glass = ""
    if not palette_safe:
        glass += (
            f'{outline} fill="url(#glass-reflection)"/>'
            f'{outline} fill="url(#glass-edge)"/>'
            '<path d="M20 53C22 30 39 15 64 13C43 20 31 34 29 54Z" '
            'fill="url(#glass-glint)"/>'
        )
    glass += (
        f'<path d="M15 54C19 30 33 17 54 13" fill="none" stroke="{BLUE}" '
        f'stroke-width="{0.8 if palette_safe else 1.4}" stroke-linecap="round" '
        f'opacity="{1 if palette_safe else 0.65}"/>'
        f'<path d="M21 39C28 25 36 20 47 17" fill="none" stroke="{TEXT_PRIMARY}" '
        f'stroke-width="{0.5 if palette_safe else 0.7}" stroke-linecap="round" '
        f'opacity="{1 if palette_safe else 0.72}"/>'
        f'<path d="M74 115C101 110 112 94 115 73" fill="none" stroke="{GREEN}" '
        f'stroke-width="{0.6 if palette_safe else 0.8}" stroke-linecap="round" '
        f'opacity="{1 if palette_safe else 0.45}"/>'
    )
    if not glass_enabled:
        glass = ""
        bezel = f'{outline} fill="none" stroke="{GREEN}" stroke-width="1.5"/>'
    shimmer_glint = ""
    if glass_enabled and shimmer is not None:
        # Bound the reflection inside the lens, never its antialiased silhouette.
        sweep = 128 * shimmer
        slope = 0.4
        norm = 1 + slope**2
        offset = sweep - 64
        discriminant = norm * 54**2 - offset**2
        if discriminant > 0:
            reach = math.sqrt(discriminant)
            start = (-slope * offset - reach) / norm
            end = (-slope * offset + reach) / norm
            path = (
                f"M{sweep + slope * start:.3f} {64 + start:.3f}"
                f"L{sweep + slope * end:.3f} {64 + end:.3f}"
            )
            shimmer_glint = (
                f'<path d="{path}" fill="none" stroke="{BLUE}" stroke-width="2.4"/>'
                f'<path d="{path}" fill="none" stroke="{TEXT_PRIMARY}" stroke-width=".7"/>'
            )
    grid = "".join(f"M5 {position}h118M{position} 5v118" for position in range(16, 113, 16))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="352" height="352" '
        'viewBox="0 0 128 128">'
        "<title>Stonks Sniper circular candlestick scope</title>"
        "<desc>A pale blue reticle looks through blue-tinted scope glass at a candlestick chart. "
        "Clear glass, curved reflections and a layered rim keep the chart visible. "
        "The animation searches a square, fires a bullet "
        "and smoothly rounds into an equally wide circle over 2.56 seconds. "
        "Decorative branding, not market data.</desc>"
        f'<defs><clipPath id="scope">{shape}</clipPath>'
        '<radialGradient id="glass-depth" cx="46%" cy="36%" r="74%">'
        f'<stop offset="0" stop-color="{BLUE}" stop-opacity=".14"/>'
        f'<stop offset=".65" stop-color="{GRID}" stop-opacity=".30"/>'
        f'<stop offset="1" stop-color="{BACKGROUND}"/></radialGradient>'
        '<linearGradient id="glass-reflection" x1="0" y1="0" x2=".35" y2="1">'
        f'<stop offset="0" stop-color="{TEXT_PRIMARY}" stop-opacity=".08"/>'
        f'<stop offset=".48" stop-color="{BLUE}" stop-opacity=".035"/>'
        f'<stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>'
        '<radialGradient id="glass-edge" cx="50%" cy="50%" r="55%">'
        f'<stop offset=".50" stop-color="{BACKGROUND}" stop-opacity="0"/>'
        f'<stop offset=".84" stop-color="{BACKGROUND}" stop-opacity=".10"/>'
        f'<stop offset="1" stop-color="{BACKGROUND}" stop-opacity=".65"/></radialGradient>'
        '<linearGradient id="glass-glint" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{TEXT_PRIMARY}" stop-opacity=".35"/>'
        f'<stop offset=".45" stop-color="{BLUE}" stop-opacity=".08"/>'
        f'<stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>'
        "</defs>"
        f'{surface}<g clip-path="url(#scope)">'
        f'<path d="{grid}" '
        f'fill="none" stroke="{GRID}" stroke-width=".5"/>'
        f'<g id="candles">{candles}</g>{glass}'
        f'<g transform="translate({x - 64:.3f} {y - 64:.3f})" '
        f'fill="none" stroke="{BLUE}" stroke-width="1.2">'
        '<circle cx="64" cy="64" r="22"/>'
        '<path d="M64 23v31M64 74v31M23 64h31M74 64h31'
        "M59 42v4M69 42v4M59 82v4M69 82v4"
        'M42 59h4M42 69h4M82 59h4M82 69h4"/>'
        '<circle cx="64" cy="64" r="3"/>'
        f"</g>{target}{shimmer_glint}</g>{bezel}</svg>"
    )


def image_from_qt(image: QImage) -> Image.Image:
    image = image.convertToFormat(QImage.Format.Format_RGBA8888)
    return Image.frombytes("RGBA", (image.width(), image.height()), bytes(image.constBits()))


def render_svg(svg: str, size: int, *, roundness: float = 1) -> Image.Image:
    renderer = QSvgRenderer(svg.encode("utf-8"))
    if not renderer.isValid():
        raise RuntimeError("Could not render the authored SVG.")
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    # Qt's SVG renderer does not enforce the artwork's SVG clip path.
    clip = QPainterPath()
    scale = size / 128
    clip.addRoundedRect(
        QRectF(4.25 * scale, 4.25 * scale, 119.5 * scale, 119.5 * scale),
        59.75 * roundness * scale,
        59.75 * roundness * scale,
    )
    painter.setClipPath(clip)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    return image_from_qt(image)


def save_gif(
    frames: list[Image.Image],
    path: Path,
    durations: list[int],
    *,
    transparent: bool = False,
    palette_colors: tuple[str, ...] | None = None,
    disposal: int = 2,
) -> None:
    if palette_colors is not None:
        palette = Image.new("P", (1, 1))
        colors = [value for color in palette_colors for value in bytes.fromhex(color[1:])]
        palette.putpalette(colors + colors[:3] * (256 - len(palette_colors)))
    else:
        # One palette prevents static UI colors from flickering between frames.
        swatches = Image.new("RGB", (128, 128 * len(frames)))
        for i, frame in enumerate(frames):
            swatches.paste(frame.convert("RGB").resize((128, 128)), (0, i * 128))
        palette = swatches.quantize(colors=255 if transparent else 256)
    converted = []
    for frame in frames:
        indexed = frame.convert("RGB").quantize(palette=palette, dither=Image.Dither.NONE)
        if transparent:
            mask = frame.getchannel("A").point(lambda alpha: 255 if alpha < 128 else 0)
            indexed.paste(255, mask=mask)
            indexed.info["transparency"] = 255
        converted.append(indexed)
    options = {"transparency": 255} if transparent else {}
    converted[0].save(
        path,
        save_all=True,
        append_images=converted[1:],
        duration=durations,
        loop=0,
        disposal=disposal,
        optimize=False,
        **options,
    )


def build_brand() -> None:
    still_svg = scope_svg()
    (ASSETS / "logo.svg").write_text(still_svg, encoding="utf-8")
    icon_images = [render_svg(still_svg, size) for size in ICON_SIZES]
    icon_images[-1].save(
        ASSETS / "logo.ico",
        sizes=[(size, size) for size in ICON_SIZES],
        append_images=icon_images[:-1],
    )
    frames = []
    durations = []
    rng = random.Random(27)
    x, y = 64.0, 64.0
    quadrants = [(0, 0), (1, 1), (1, 0), (0, 1)]
    # Seeded jumps cover every quadrant while keeping regeneration reproducible.
    for sweep in range(3):
        if sweep:
            rng.shuffle(quadrants)
        for right, bottom in quadrants:
            tx = rng.uniform(81, 116) if right else rng.uniform(12, 47)
            ty = rng.uniform(81, 116) if bottom else rng.uniform(12, 47)
            for step in range(1, 5):
                progress = step / 4
                frames.append(
                    render_svg(
                        scope_svg(
                            x + (tx - x) * progress,
                            y + (ty - y) * progress,
                            roundness=0,
                            palette_safe=True,
                        ),
                        352,
                        roundness=0,
                    )
                )
                durations.append((50, 70, 40, 90)[step - 1])
            x, y = tx, ty
    for step in range(1, 9):
        progress = 1 - (1 - step / 8) ** 3
        frames.append(
            render_svg(
                scope_svg(
                    x + (64 - x) * progress,
                    y + (64 - y) * progress,
                    roundness=0,
                    palette_safe=True,
                ),
                352,
                roundness=0,
            )
        )
        durations.append(70 if step < 8 else 450)
    for step in range(7):
        frames.append(
            render_svg(scope_svg(roundness=0, bullet=step / 6, palette_safe=True), 352, roundness=0)
        )
        durations.append(60)
    for step in range(6):
        frames.append(
            render_svg(
                scope_svg(flash=1 - step / 6, roundness=0, palette_safe=True), 352, roundness=0
            )
        )
        durations.append(60)
    morph_elapsed = 0
    for step in range(96):
        # GIF delays use 10ms ticks: three frames share 80ms, totaling exactly 2.56s.
        duration = (30, 30, 20)[step % 3]
        morph_elapsed += duration
        progress = morph_elapsed / 2560
        # Quintic easing starts and ends with zero speed and acceleration.
        roundness = progress**3 * (progress * (6 * progress - 15) + 10)
        frames.append(
            render_svg(scope_svg(roundness=roundness, palette_safe=True), 352, roundness=roundness)
        )
        durations.append(duration)
    for step in range(30):
        progress = step / 29
        shimmer = progress**3 * (progress * (6 * progress - 15) + 10)
        frames.append(render_svg(scope_svg(palette_safe=True, shimmer=shimmer), 352))
        durations.append(40)
    frames.append(render_svg(scope_svg(palette_safe=True), 352))
    durations.append(600)
    save_gif(
        frames,
        ASSETS / "logo.gif",
        durations,
        transparent=True,
        palette_colors=(BACKGROUND, GRID, GREEN, BLUE, TEXT_PRIMARY, TEXT_SECONDARY, "#E88472"),
    )
    IMAGES.mkdir(parents=True, exist_ok=True)
    paper = "".join(f"M{position} 0v144" for position in range(0, 961, 14))
    paper += "".join(f"M0 {position}h960" for position in range(0, 145, 14))
    banner = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="144" '
        'viewBox="0 0 960 144"><rect x="1" y="1" width="958" height="142" '
        f'fill="{BACKGROUND}" stroke="{BLUE}"/>'
        f'<path d="{paper}" fill="none" stroke="{GRID}" stroke-width=".5"/>'
        f'<path d="M176 28h80M856 28h80M176 116h80M856 116h80" stroke="{GREEN}" '
        'stroke-opacity=".6"/>'
        '<text x="480" y="78" text-anchor="middle" '
        'font-family="Times New Roman" '
        f'font-size="58" font-weight="400" letter-spacing="3" fill="{TEXT_PRIMARY}">'
        'Stonks Sniper</text><text x="480" y="113" text-anchor="middle" '
        f'font-family="Times New Roman" font-size="16" fill="{TEXT_SECONDARY}" '
        'letter-spacing="2">LEARN THE IDEA. TEST IT ON REAL HISTORY.</text></svg>'
    )
    (IMAGES / "readme-banner.svg").write_text(banner, encoding="utf-8")
    cover = QImage(960, 144, QImage.Format.Format_ARGB32_Premultiplied)
    cover.fill(Qt.GlobalColor.transparent)
    painter = QPainter(cover)
    QSvgRenderer(banner.encode("utf-8")).render(painter)
    painter.end()
    cover_image = image_from_qt(cover)
    cover_image.alpha_composite(render_svg(still_svg, 120), (32, 12))
    cover_image.save(IMAGES / "readme-banner.png")
    paper = "".join(f"M{position} 0v86" for position in range(0, 301, 14))
    paper += "".join(f"M0 {position}h300" for position in range(0, 87, 14))
    for name, title, subtitle in (
        ("start", "Run the latest source", "Windows / Python / setup"),
        ("guide", "Understand the tool", "Simple lessons / rules / real data"),
        ("download", "Download for Windows", f"v{__version__} / First public release"),
    ):
        button = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="86" '
            'viewBox="0 0 300 86">'
            f'<rect width="300" height="86" fill="{BACKGROUND}"/>'
            f'<path d="{paper}" fill="none" stroke="{GRID}" stroke-width=".5"/>'
            f'<g fill="none" stroke="{GREEN}">'
            '<rect x="2" y="2" width="296" height="82" stroke-width="4" stroke-opacity=".12"/>'
            '<rect x="2" y="2" width="296" height="82" stroke-width="1"/>'
            f'</g><g fill="none" stroke="{BLUE}">'
            '<rect x="7" y="7" width="286" height="72" stroke-width="4" stroke-opacity=".10"/>'
            '<rect x="7" y="7" width="286" height="72" stroke-width="1"/>'
            '</g><g text-anchor="middle" font-family="Times New Roman" font-weight="400">'
            f'<text x="150" y="38" font-size="20" letter-spacing=".6" fill="{TEXT_PRIMARY}">'
            f"{escape(title.upper())}</text>"
            '<text x="150" y="61" font-size="11.5" letter-spacing=".65" '
            f'fill="{TEXT_SECONDARY}">{escape(subtitle.upper())}</text></g></svg>'
        )
        (IMAGES / f"button-{name}.svg").write_text(button, encoding="utf-8")
    print("Built final-circle glass/shimmer GIF, static SVG/ICO and branded cover.")


class Walkthrough:
    """Owned Qt clicks and rendered pointer overlays, never system mouse automation."""

    width, height, footer = 1366, 768, 76

    def __init__(self, app: QApplication, main_window: QWidget, caption: str) -> None:
        if app.platformName() != "offscreen":
            raise RuntimeError("Walkthroughs require the isolated offscreen Qt platform.")
        self.app, self.main_window = app, main_window
        self.root = main_window
        self.pointer = QPoint(36, 36)
        self.caption = caption
        self.frames: list[Image.Image] = []
        self.durations: list[int] = []
        self.actions: list[dict[str, object]] = []
        self.bind(main_window)
        self.record(1000)

    def process(self) -> None:
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        self.app.processEvents()

    def bind(self, root: QWidget, *, full: bool = True) -> None:
        self.root = root
        if full:
            root.resize(self.width, self.height)
        self.process()
        if root.width() > self.width or root.height() > self.height:
            raise RuntimeError("Native window exceeds the capture canvas.")
        self.offset = QPoint((self.width - root.width()) // 2, (self.height - root.height()) // 2)

    def record(self, duration: int = 100, ripple: float | None = None) -> None:
        if len(self.frames) >= 180:
            raise RuntimeError("Split this walkthrough; the per-clip frame budget is exhausted.")
        self.process()
        image = QImage(self.width, self.height + self.footer, QImage.Format.Format_RGB32)
        image.fill(QColor(BACKGROUND))
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.root is not self.main_window:
            painter.drawPixmap(0, 0, self.main_window.grab())
            painter.fillRect(0, 0, self.width, self.height, QColor(0, 0, 0, 100))
        painter.drawPixmap(self.offset, self.root.grab())
        origin = self.root.mapToGlobal(QPoint())
        for popup in self.app.topLevelWidgets():
            if popup.isVisible() and popup.windowType() == Qt.WindowType.Popup:
                painter.drawPixmap(popup.mapToGlobal(QPoint()) - origin + self.offset, popup.grab())
        if ripple is not None:
            color = QColor(GREEN)
            color.setAlpha(round(210 * (1 - ripple)))
            painter.setPen(QPen(color, 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(self.pointer), 10 + ripple * 24, 10 + ripple * 24)
        painter.translate(self.pointer)
        painter.setPen(QPen(QColor(BACKGROUND), 2))
        painter.setBrush(QColor(TEXT_PRIMARY))
        painter.drawPolygon(
            QPolygonF(
                [
                    QPointF(x, y)
                    for x, y in (
                        (0, 0),
                        (0, 27),
                        (7, 21),
                        (12, 32),
                        (18, 29),
                        (13, 19),
                        (24, 19),
                    )
                ]
            )
        )
        painter.resetTransform()
        painter.fillRect(0, self.height, self.width, self.footer, QColor(BACKGROUND))
        painter.setPen(QColor(GREEN))
        painter.drawLine(0, self.height, self.width, self.height)
        painter.setFont(QFont("Segoe UI", 14))
        painter.setPen(QColor(TEXT_PRIMARY))
        painter.drawText(
            QRectF(20, self.height + 6, self.width - 40, 32),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.caption,
        )
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(TEXT_SECONDARY))
        painter.drawText(
            20,
            self.height + 60,
            "ACTUAL NATIVE UI  |  Scripted Qt clicks + pointer overlay  |  "
            "Practice money, not orders",
        )
        painter.end()
        self.frames.append(image_from_qt(image).convert("RGB"))
        self.durations.append(duration)

    def hold(self, duration: int = 1500) -> None:
        self.durations[-1] += duration

    def point(self, widget: QWidget, local: QPoint) -> QPoint:
        return widget.mapToGlobal(local) - self.root.mapToGlobal(QPoint()) + self.offset

    def move(self, destination: QPoint, caption: str) -> None:
        self.caption = caption
        start = self.pointer
        for step in range(1, 5):
            progress = step / 4
            progress = progress * progress * (3 - 2 * progress)
            self.pointer = QPoint(
                round(start.x() + (destination.x() - start.x()) * progress),
                round(start.y() + (destination.y() - start.y()) * progress),
            )
            self.record(60)

    def click(self, widget: QWidget, caption: str, local: QPoint | None = None) -> None:
        self.process()
        if not widget.isVisible() or not widget.isEnabled():
            raise RuntimeError(f"Cannot demonstrate a hidden/disabled control: {caption}")
        local = local if local is not None else widget.rect().center()
        destination = self.point(widget, local)
        if not (0 <= destination.x() < self.width and 0 <= destination.y() < self.height):
            raise RuntimeError(f"Click target lies outside the visible capture: {caption}")
        self.move(destination, caption)
        QTest.mousePress(widget, Qt.MouseButton.LeftButton, pos=local)
        self.record(90, 0)
        QTest.mouseRelease(widget, Qt.MouseButton.LeftButton, pos=local)
        self.record(100, 0.4)
        self.record(140, 1)
        self.hold(max(1400, 220 * len(caption.split())))
        self.actions.append(
            {"kind": "click", "caption": caption, "position": [destination.x(), destination.y()]}
        )

    def tab(self, widget: QTabWidget, text: str, caption: str) -> None:
        index = next(i for i in range(widget.count()) if widget.tabText(i) == text)
        bar = widget.tabBar()
        self.click(bar, caption, bar.tabRect(index).center())
        if widget.currentIndex() != index:
            raise RuntimeError(f"Tab click did not select {text}.")

    def row(self, widget: QListWidget, index: int, caption: str) -> None:
        item = widget.item(index)
        if item is None:
            raise RuntimeError(f"No native list row {index}.")
        widget.scrollToItem(item)
        self.process()
        self.click(widget.viewport(), caption, widget.visualItemRect(item).center())
        if widget.currentRow() != index:
            raise RuntimeError("List click did not select the demonstrated row.")

    def choose(self, widget: QComboBox, index: int, caption: str) -> None:
        self.click(widget, caption)
        # Native popups briefly suppress releases immediately after opening.
        QTest.qWait(self.app.doubleClickInterval())
        view = widget.view()
        item = widget.model().index(index, widget.modelColumn(), widget.rootModelIndex())
        view.scrollTo(item)
        self.process()
        self.click(view.viewport(), caption, view.visualRect(item).center())
        if widget.currentIndex() != index:
            raise RuntimeError("Dropdown click did not select the demonstrated value.")

    def enter(self, widget: QLineEdit | QAbstractSpinBox, text: str, caption: str) -> None:
        editor = widget if isinstance(widget, QLineEdit) else widget.findChild(QLineEdit)
        if editor is None:
            raise RuntimeError("Input control has no native editor.")
        self.click(editor, caption)
        QTest.keyClick(editor, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
        for start in range(0, len(text), 3):
            QTest.keyClicks(editor, text[start : start + 3])
            self.record(130)
        QTest.keyClick(editor, Qt.Key.Key_Return)
        self.record(150)
        self.hold(700)
        self.actions.append({"kind": "keyboard", "caption": caption, "text": text})

    def drag(self, slider: QSlider, target: int, caption: str, *, steps: int = 12) -> None:
        option = QStyleOptionSlider()
        slider.initStyleOption(option)

        def handle(value: int) -> QPoint:
            option.sliderPosition = value
            return (
                slider.style()
                .subControlRect(
                    QStyle.ComplexControl.CC_Slider,
                    option,
                    QStyle.SubControl.SC_SliderHandle,
                    slider,
                )
                .center()
            )

        before = slider.value()
        start, end = handle(before), handle(target)
        self.move(self.point(slider, start), caption)
        QTest.mousePress(slider, Qt.MouseButton.LeftButton, pos=start)
        for step in range(1, steps + 1):
            local = start + (end - start) * (step / steps)
            event = QMouseEvent(
                QEvent.Type.MouseMove,
                QPointF(local),
                QPointF(slider.mapToGlobal(local)),
                Qt.MouseButton.NoButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier,
            )
            QApplication.sendEvent(slider, event)
            self.pointer = self.point(slider, local)
            self.record(120, 0.3)
        QTest.mouseRelease(slider, Qt.MouseButton.LeftButton, pos=end)
        self.record(150)
        self.hold(1100)
        if abs(slider.value() - target) > 2:
            raise RuntimeError(f"Native slider did not reach requested observation {target}.")
        self.actions.append(
            {
                "kind": "drag",
                "caption": caption,
                "from": before,
                "requested": target,
                "actual": slider.value(),
            }
        )

    def wait(self, ready: Callable[[], bool], *, timeout: float = 120) -> None:
        deadline = monotonic() + timeout
        while not ready():
            if monotonic() > deadline:
                raise TimeoutError("The actual provider request did not finish in time.")
            QTest.qWait(30)
        self.record(300)
        self.hold()

    def finish(self, output: Path, filename: str) -> dict[str, object]:
        self.hold(1800)
        output.mkdir(parents=True, exist_ok=True)
        path = output / filename
        save_gif(self.frames, path, self.durations, disposal=1)
        if path.stat().st_size >= 10_000_000:
            raise RuntimeError(f"Split this walkthrough; {filename} exceeds the 10 MB budget.")
        with Image.open(path) as encoded:
            encoded_frames = encoded.n_frames
        result = {
            "file": filename,
            "frames": len(self.frames),
            "encoded_frames": encoded_frames,
            "duration_ms": sum(self.durations),
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "actions": self.actions,
        }
        self.frames.clear()
        self.durations.clear()
        print(
            f"Captured {filename}: {result['frames']} frames, {result['bytes']} bytes.", flush=True
        )
        return result


def build_gallery(app: QApplication, end: date | None, output: Path = IMAGES) -> None:
    if app.platformName() != "offscreen":
        raise RuntimeError("Gallery capture must be offscreen before creating any windows.")

    from stonks_sniper.app import BookHistoryDemo, MainWindow, MarketDemoWindow, SimulationWindow
    from stonks_sniper.providers import INDIA
    from stonks_sniper.theme import configure_application

    def button(parent: QWidget, text: str) -> QPushButton:
        matches = [b for b in parent.findChildren(QPushButton) if b.text() == text]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one native button: {text}")
        return matches[0]

    def dialog(kind):
        matches = [w for w in window.findChildren(kind) if w.isVisible()]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one owned {kind.__name__} window.")
        return matches[0]

    today = datetime.now(INDIA).date()
    requested_end = end or today
    configure_application(app)
    window = MainWindow()
    window.motion.setChecked(False)
    window.resize(Walkthrough.width, Walkthrough.height)
    window.end.setDate(QDate(requested_end.year, requested_end.month, requested_end.day))
    window.show()
    captures = []
    try:
        tour = Walkthrough(app, window, "Load a stock, choose a rule, test with practice money.")
        tour.enter(window.symbol, "ICICIBANK", "1. Enter ICICIBANK; NSE and the dates are visible.")
        tour.enter(window.capital, "10000", "2. Use INR 10,000 of hypothetical starting capital.")
        tour.click(window.fetch, "3. Load actual completed history; no substitute prices.")
        tour.wait(lambda: window.fetch_thread is None)
        data = window.data
        if data is None:
            raise RuntimeError(window.provenance.text())
        tour.choose(window.pattern, 1, "4. Choose the EMA idea; this is not a winning-rule search.")
        tour.click(window.run_button, "5. Test the chosen idea on the actual loaded history.")
        assert window.result is not None
        tour.choose(window.price_style, 1, "6. Switch the stock-price view to candlesticks.")
        tour.drag(window.replay, len(data.candles) - 60, "7. Drag back to inspect an earlier day.")
        captures.append(tour.finish(output, "explore.gif"))

        tour = Walkthrough(app, window, "Compare practice money with buying once and holding.")
        tour.tab(window.chart_tabs, "Your money", "1. Open Your money: rule versus holding.")
        tour.drag(
            window.replay,
            len(data.candles),
            "2. Reveal later observations and actual simulated P&L.",
        )
        tour.tab(
            window.chart_tabs,
            "Falls from a high",
            "3. Inspect drawdown, not just the final profit.",
        )
        tour.tab(
            window.chart_tabs,
            "Your money",
            "4. Same starting point and costs; losses stay visible.",
        )
        captures.append(tour.finish(output, "money.gif"))

        tour = Walkthrough(app, window, "See the measurements behind the selected trading rule.")
        tour.tab(
            window.chart_tabs,
            "See the rule",
            "1. Open See the rule for actual indicator measurements.",
        )
        tour.drag(
            window.replay,
            len(data.candles) - 55,
            "2. Inspect only the measurements revealed by this day.",
        )
        tour.drag(
            window.replay,
            len(data.candles),
            "3. Scrub forward; rule decisions are not earlier fills.",
        )
        captures.append(tour.finish(output, "rule.gif"))

        tour = Walkthrough(app, window, "Learn the idea before looking at a simulated return.")
        tour.click(window.pattern_help, "1. Explain pattern opens the selected native lesson.")
        tour.row(
            window.lesson_list, 0, "2. Choose SMA: meaning, household example and failure modes."
        )
        tour.tab(
            window.lesson_tabs,
            "Exact rules and source",
            "3. Read the actual formula and its source.",
        )
        tour.row(window.lesson_list, 3, "4. Choose Donchian; each idea has its own exact rule.")
        tour.tab(window.lesson_tabs, "Explain it simply", "5. Return to the beginner explanation.")
        captures.append(tour.finish(output, "learn.gif"))

        tour = Walkthrough(app, window, "Apply a lesson to real history without changing Explore.")
        tour.click(window.lesson_demo, "1. Click See a real-market demo.")
        picker = dialog(MarketDemoWindow)
        tour.bind(picker, full=False)
        tour.record()
        tour.hold()
        tour.click(picker.use_loaded, "2. Use the explicitly dated captured Explore dataset.")
        demo = dialog(SimulationWindow)
        tour.bind(demo)
        tour.record()
        tour.hold()
        assert demo.learning and demo.experiment is not None
        tour.click(demo.next_signal, "3. Next signal reveals the next recorded target change.")
        tour.click(
            demo.next_trade, "4. Next trade shows a later simulated fill, not a live opportunity."
        )
        charts = demo.equity_chart.parentWidget()
        while not isinstance(charts, QTabWidget):
            if charts is None:
                raise RuntimeError("Missing native demo chart tabs.")
            charts = charts.parentWidget()
        tour.tab(
            charts,
            "Your money",
            "5. Compare this lesson with holding; no profitable interval was picked.",
        )
        tour.click(demo.finish, "6. Show the complete marked result, including unsold stock.")
        captures.append(tour.finish(output, "real-market-demo.gif"))
        demo.close()
        picker.close()
        tour.process()

        tour = Walkthrough(
            app, window, "Run the selected Explore strategy between your chosen dates."
        )
        tour.tab(window.tabs, "Explore", "1. Return to Explore; Simulate is beside Test idea.")
        tour.click(window.simulate_button, "2. Open the independent Simulate window.")
        simulation = dialog(SimulationWindow)
        tour.bind(simulation)
        tour.record()
        tour.hold()
        tour.click(simulation.start, "3. Start/end dates are bounded by the actual loaded history.")
        QTest.keyClick(simulation.start, Qt.Key.Key_Up)
        tour.record(250)
        tour.click(
            simulation.run_button, "4. Start simulation; warmup stays inside the chosen range."
        )
        assert simulation.experiment is not None
        tour.drag(
            simulation.replay,
            simulation.replay.maximum() - 70,
            "5. Reveal the date range: buy/sell markers and trade rows appear causally.",
        )
        tour.click(simulation.step, "6. Next day advances one actual observed session.")
        charts = simulation.equity_chart.parentWidget()
        while not isinstance(charts, QTabWidget):
            if charts is None:
                raise RuntimeError("Missing native simulation chart tabs.")
            charts = charts.parentWidget()
        tour.tab(charts, "Your money", "7. View the money graph for the same simulation.")
        tour.click(
            simulation.finish,
            "8. Final profit/loss is shown in INR and percent, after modelled costs.",
        )
        captures.append(tour.finish(output, "simulate.gif"))
        simulation.close()
        tour.process()

        tour = Walkthrough(
            app, window, "Read The Intelligent Investor with original practical notes."
        )
        tour.tab(window.tabs, "Learn the patterns", "1. Open Learn the patterns.")
        tour.tab(
            window.learning_sections,
            "The Intelligent Investor",
            "2. Switch from technical strategies to the book.",
        )
        tour.row(
            window.book.chapters,
            4,
            "3. Chapter 5 explains defensive investing and equal-money purchases.",
        )
        tour.click(window.book.demo_button, "4. Open this chapter's real-history practical.")
        picker = dialog(MarketDemoWindow)
        tour.bind(picker, full=False)
        tour.record()
        tour.click(picker.use_loaded, "5. Explicitly reuse the actual captured stock history.")
        practical = dialog(BookHistoryDemo)
        tour.bind(practical)
        tour.record()
        tour.click(
            practical.finish, "6. Inspect scheduled monthly purchases; not a buy recommendation."
        )
        tour.hold(2000)
        assert practical.purchases.count() > 0
        practical.close()
        picker.close()
        tour.process()
        tour.bind(window)
        tour.tab(
            window.book,
            "Fundamental workbook",
            "7. Research current facts separately from historical simulations.",
        )
        tour.click(
            window.book.copy_stock,
            "8. Use Explore stock copies the identity, not invented company facts.",
        )
        tour.click(
            window.book.calculate,
            "9. An empty workbook refuses calculation; research evidence must come first.",
        )
        assert not window.book.report_html
        assert "Cannot calculate" in window.book.results.toPlainText()
        captures.append(tour.finish(output, "intelligent-investor.gif"))

        tour = Walkthrough(app, window, "Dictionary: simple meanings and everyday examples.")
        tour.tab(
            window.tabs,
            "Dictionary",
            "1. Open Dictionary; new terminal concepts are searchable too.",
        )
        tour.enter(
            window.glossary_search, "drawdown", "2. Search drawdown: a fall from an earlier high."
        )
        assert window.glossary_list.count() > 0
        tour.hold()
        tour.enter(
            window.glossary_search,
            "slippage",
            "3. Search slippage: the difference from an expected price.",
        )
        assert window.glossary_list.count() > 0
        tour.hold()
        tour.enter(
            window.glossary_search, "watchlist", "4. Search the new Market tools vocabulary."
        )
        assert window.glossary_list.count() > 0
        tour.hold()
        captures.append(tour.finish(output, "dictionary.gif"))

        tools = window.market_tools
        tour = Walkthrough(app, window, "Learn useful terminal tools without a brokerage account.")
        tour.tab(window.tabs, "Market tools", "1. Open Market tools: real history, pretend money.")
        tour.click(
            tools.capture_button,
            "2. Capture Explore history; this does not make a hidden network request.",
        )
        assert tools.data is data and tools.replay_index == 0
        tour.row(
            tools.navigation, 1, "3. Watchlist shows only the revealed session, not a live quote."
        )
        tour.enter(
            tools.jump_to,
            "230",
            "4. Choose an observation to reveal, preserving every intervening paper day.",
        )
        tour.click(
            button(tools, "Advance to"),
            "5. Advance to observation 230; the local paper clock cannot rewind.",
        )
        tour.row(tools.navigation, 2, "6. Open Charts for the currently revealed prefix.")
        tour.choose(tools.chart_mode, 1, "7. Choose Candles from the real chart controls.")
        tour.choose(
            tools.study, 1, "8. Add the shared SMA study; annotations are not trading signals."
        )
        captures.append(tour.finish(output, "market-tools.gif"))

        tour = Walkthrough(
            app, window, "Queue a paper instruction, then observe its later opening fill."
        )
        tour.row(tools.navigation, 4, "1. Open Paper orders & holdings; no broker is connected.")
        tour.click(tools.submit_order, "2. Queue a one-unit Buy; queued is NOT filled.")
        assert tools.account.orders[-1].status == "Pending"
        tour.click(
            tools.next_day, "3. Advance to the next observed opening; costs and holdings update."
        )
        assert tools.account.orders[-1].status == "Filled" and tools.account.units > 0
        tour.choose(tools.side, 1, "4. Choose Sell to close the owned paper unit.")
        tour.click(tools.submit_order, "5. Queue the Sell after the revealed close.")
        tour.click(
            tools.next_day, "6. Advance again: inspect realised P&L, including both-side costs."
        )
        assert tools.account.orders[-1].status == "Filled" and tools.account.units == 0
        captures.append(tour.finish(output, "paper-orders.gif"))

        tour = Walkthrough(
            app, window, "Manual learning labs are assumptions, not downloaded prices."
        )
        tour.row(
            tools.navigation,
            5,
            "1. Open Risk & allocation: plan with explicitly hypothetical inputs.",
        )
        tour.enter(
            tools.risk_percent,
            "2",
            "2. Set an illustrative 2% risk budget; not a guaranteed loss cap.",
        )
        tour.click(
            button(tools, "Calculate risk and quantity"),
            "3. Calculate cost-aware whole-unit sizing.",
        )
        tour.row(
            tools.navigation, 6, "4. Open Depth & options labs; neither panel is a live data feed."
        )
        tour.choose(tools.option_kind, 1, "5. Compare a bought put's manual expiry arithmetic.")
        tour.click(
            button(tools, "Calculate expiry scenarios"),
            "6. Read expiry outcomes and premium risk, not a trade signal.",
        )
        captures.append(tour.finish(output, "manual-labs.gif"))

        receipt = {
            "captured_at": datetime.now(INDIA).isoformat(),
            "application_version": __version__,
            "source_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "source_dirty": bool(
                subprocess.check_output(
                    ["git", "status", "--porcelain"], cwd=ROOT, text=True
                ).strip()
            ),
            "capture_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "source": data.source,
            "symbol": data.symbol,
            "exchange": data.exchange,
            "currency": data.currency,
            "fetched_at": data.fetched_at.isoformat(),
            "first_observation": str(data.candles[0].session),
            "last_observation": str(data.candles[-1].session),
            "observations": len(data.candles),
            "requested_end": requested_end.isoformat(),
            "provider_warnings": list(data.warnings),
            "price_basis": data.price_basis,
            "platform": app.platformName(),
            "width": Walkthrough.width,
            "height": Walkthrough.height + Walkthrough.footer,
            "motion": (
                "Scripted native Qt clicks/keys/drags; accelerated, captioned history scrubbing."
            ),
            "pointer": "Rendered overlay and click ripples; no operating-system pointer control.",
            "composition": (
                "Owned dialogs centered over the owned main window; caption footer added."
            ),
            "isolation": "Offscreen owned QApplication and temporary process-local Yahoo cache.",
            "branding": "Existing decorative logo/meme unchanged; not product walkthroughs.",
            "captures": captures,
        }
        (output / "gif-captures.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        print(
            f"Captured {len(captures)} walkthroughs from {len(data.candles)} actual observations."
        )
    finally:
        window.close()
        window.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--brand", action="store_true", help="Build original vector and GIF artwork."
    )
    parser.add_argument(
        "--gallery", action="store_true", help="Fetch actual history and capture native GUI GIFs."
    )
    parser.add_argument(
        "--gallery-dir",
        type=Path,
        default=IMAGES,
        help="Output directory for reviewed walkthrough candidates; branding is unchanged.",
    )
    parser.add_argument(
        "--end",
        type=date.fromisoformat,
        help="Explicit final requested history date (YYYY-MM-DD), recorded in provenance.",
    )
    parser.add_argument("--gallery-cache", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not (args.brand or args.gallery):
        parser.error("Choose --brand and/or --gallery; only --gallery retrieves market history.")
    if args.gallery and args.gallery_cache is None:
        # Windows can retain worker-thread SQLite handles until process exit.
        # Let the owning parent clean only its temporary cache after that exit.
        with TemporaryDirectory(prefix="stonks-readme-cache-") as cache:
            subprocess.run(
                [sys.executable, str(Path(__file__)), *sys.argv[1:], "--gallery-cache", cache],
                check=True,
            )
        return
    app = QApplication([])
    if sys.platform == "win32" and app.platformName() == "offscreen":
        for name in ("segoeui.ttf", "times.ttf") if args.brand else ("segoeui.ttf",):
            font = Path(os.environ["WINDIR"]) / "Fonts" / name
            if QFontDatabase.addApplicationFont(str(font)) < 0:
                raise RuntimeError(f"Could not load installed font: {font}")
    if args.brand:
        build_brand()
    if args.gallery:
        import yfinance as yf

        yf.set_tz_cache_location(str(args.gallery_cache))
        build_gallery(app, args.end, args.gallery_dir.resolve())


if __name__ == "__main__":
    main()
