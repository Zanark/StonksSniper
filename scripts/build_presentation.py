"""Rebuild original branding and opt-in real-data native GIF demonstrations."""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image  # noqa: E402
from PySide6.QtCore import QCoreApplication, QDate, QEvent, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QFontDatabase, QImage, QPainter, QPainterPath  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "src" / "stonks_sniper" / "assets"
IMAGES = ROOT / "docs" / "images"
BACKGROUND = "#0A0E0F"
GRID = "#192220"
GREEN = "#8AC8B1"
BLUE = "#B6CAD6"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#BDBEBE"


def scope_svg(
    x: float = 64,
    y: float = 64,
    flash: float = 0,
    *,
    roundness: float = 1,
    bullet: float | None = None,
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
    surface = f'{outline} fill="{BACKGROUND}"/>{outline} fill="url(#glass-depth)"/>'
    bezel = (
        '<rect x="10" y="10" width="108" height="108" '
        f'rx="{54 * roundness:.5f}" fill="none" stroke="{BACKGROUND}" '
        'stroke-width="6" stroke-opacity=".7"/>'
        f'{outline} fill="none" stroke="{GREEN}" stroke-width="1.5"/>'
        '<rect x="7.5" y="7.5" width="113" height="113" '
        f'rx="{56.5 * roundness:.5f}" fill="none" stroke="{BLUE}" '
        'stroke-width=".7" stroke-opacity=".65"/>'
    )
    glass = (
        f'{outline} fill="url(#glass-reflection)"/>'
        f'{outline} fill="url(#glass-edge)"/>'
        f'<path d="M15 54C19 30 33 17 54 13" fill="none" stroke="{BLUE}" '
        'stroke-width="2.2" stroke-linecap="round" opacity=".65"/>'
        f'<path d="M21 39C28 25 36 20 47 17" fill="none" stroke="{TEXT_PRIMARY}" '
        'stroke-width="1.4" stroke-linecap="round" opacity=".72"/>'
        f'<path d="M74 115C101 110 112 94 115 73" fill="none" stroke="{GREEN}" '
        'stroke-width="1.1" stroke-linecap="round" opacity=".45"/>'
    )
    grid = "".join(f"M5 {position}h118M{position} 5v118" for position in range(16, 113, 16))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="352" height="352" '
        'viewBox="0 0 128 128">'
        "<title>Stonks Sniper circular candlestick scope</title>"
        "<desc>A pale blue reticle looks through blue-tinted scope glass at a candlestick chart. "
        "Curved reflections, a shaded lens edge and a layered rim give the glass depth. "
        "The animation searches a square, fires a bullet "
        "and smoothly rounds into an equally wide circle over 2.56 seconds. "
        "Decorative branding, not market data.</desc>"
        f'<defs><clipPath id="scope">{shape}</clipPath>'
        '<radialGradient id="glass-depth" cx="46%" cy="36%" r="74%">'
        f'<stop offset="0" stop-color="{BLUE}" stop-opacity=".24"/>'
        f'<stop offset=".65" stop-color="{GRID}" stop-opacity=".58"/>'
        f'<stop offset="1" stop-color="{BACKGROUND}"/></radialGradient>'
        '<linearGradient id="glass-reflection" x1="0" y1="0" x2=".35" y2="1">'
        f'<stop offset="0" stop-color="{TEXT_PRIMARY}" stop-opacity=".16"/>'
        f'<stop offset=".48" stop-color="{BLUE}" stop-opacity=".035"/>'
        f'<stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>'
        '<radialGradient id="glass-edge" cx="50%" cy="50%" r="55%">'
        f'<stop offset=".50" stop-color="{BACKGROUND}" stop-opacity="0"/>'
        f'<stop offset=".84" stop-color="{BACKGROUND}" stop-opacity=".18"/>'
        f'<stop offset="1" stop-color="{BACKGROUND}" stop-opacity=".96"/></radialGradient>'
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
        f"</g>{target}</g>{bezel}</svg>"
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
        disposal=2,
        optimize=False,
        **options,
    )


def build_brand() -> None:
    (ASSETS / "logo.svg").write_text(scope_svg(), encoding="utf-8")
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
                        scope_svg(x + (tx - x) * progress, y + (ty - y) * progress, roundness=0),
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
                scope_svg(x + (64 - x) * progress, y + (64 - y) * progress, roundness=0),
                352,
                roundness=0,
            )
        )
        durations.append(70 if step < 8 else 450)
    for step in range(7):
        frames.append(render_svg(scope_svg(roundness=0, bullet=step / 6), 352, roundness=0))
        durations.append(60)
    for step in range(6):
        frames.append(render_svg(scope_svg(flash=1 - step / 6, roundness=0), 352, roundness=0))
        durations.append(60)
    morph_elapsed = 0
    for step in range(96):
        # GIF delays use 10ms ticks: three frames share 80ms, totaling exactly 2.56s.
        duration = (30, 30, 20)[step % 3]
        morph_elapsed += duration
        progress = morph_elapsed / 2560
        # Quintic easing starts and ends with zero speed and acceleration.
        roundness = progress**3 * (progress * (6 * progress - 15) + 10)
        frames.append(render_svg(scope_svg(roundness=roundness), 352, roundness=roundness))
        durations.append(duration)
    frames.append(render_svg(scope_svg(), 352))
    durations.append(1800)
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
        f'<path d="M24 28h80M856 28h80M24 116h80M856 116h80" stroke="{GREEN}" '
        'stroke-opacity=".6"/>'
        '<text x="480" y="78" text-anchor="middle" '
        'font-family="Times New Roman" '
        f'font-size="58" font-weight="400" letter-spacing="3" fill="{TEXT_PRIMARY}">'
        'Stonks Sniper</text><text x="480" y="113" text-anchor="middle" '
        f'font-family="Times New Roman" font-size="16" fill="{TEXT_SECONDARY}" '
        'letter-spacing="2">LEARN THE IDEA. TEST IT ON REAL HISTORY.</text></svg>'
    )
    (IMAGES / "readme-banner.svg").write_text(banner, encoding="utf-8")
    paper = "".join(f"M{position} 0v86" for position in range(0, 301, 14))
    paper += "".join(f"M0 {position}h300" for position in range(0, 87, 14))
    for name, title, subtitle in (
        ("start", "Run the latest source", "Windows / Python / setup"),
        ("guide", "Understand the tool", "Simple lessons / rules / real data"),
        ("download", "Download prototype", "v0.1.0 / Python package"),
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
    print("Built glass scope, equal-size 2.56s eased rounding and centered static logo.")


def build_gallery(app: QApplication, end: date | None) -> None:
    from stonks_sniper.app import MainWindow
    from stonks_sniper.providers import INDIA, YahooDailyProvider
    from stonks_sniper.theme import configure_application

    today = datetime.now(INDIA).date()
    requested_end = end or today
    data = YahooDailyProvider().fetch("RELIANCE", "NSE", today - timedelta(days=730), requested_end)
    configure_application(app)
    window = MainWindow()
    window.motion.setChecked(False)
    window.resize(1366, 768)
    window.end.setDate(QDate(requested_end))
    window.data_ready(data)
    window.show()
    captures = []

    def frame() -> Image.Image:
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()
        if (window.width(), window.height()) != (1366, 768):
            raise RuntimeError("Native layout exceeded the advertised capture dimensions.")
        return image_from_qt(window.grab().toImage())

    def capture(name: str, frames: list[Image.Image], durations: list[int], action: str) -> None:
        save_gif(frames, IMAGES / name, durations)
        captures.append(
            {"file": name, "frames": len(frames), "duration_ms": sum(durations), "action": action}
        )

    try:
        for chart, name in ((0, "explore.gif"), (1, "money.gif"), (3, "rule.gif")):
            window.chart_tabs.setCurrentIndex(chart)
            window.price_style.setCurrentIndex(1 if chart == 0 else 0)
            count = len(data.candles)
            positions = [round(count - 60 + i * 60 / 24) for i in range(25)]
            frames = []
            for position in positions:
                window.replay.setValue(position)
                frames.append(frame())
            capture(
                name,
                frames,
                [1800] + [160] * 23 + [2400],
                "Actual native replay cursor advanced through the final 60 completed sessions.",
            )
        window.replay.setValue(len(data.candles))
        frames = []
        for index in (0, 2, 3):
            window.pattern.setCurrentIndex(index)
            window.pattern_help.click()
            frames.append(frame())
        capture(
            "learn.gif", frames, [2600] * 3, "Explain pattern opens three authored native lessons."
        )
        frames = []
        for key in ("stock", "drawdown", "slippage"):
            window.open_glossary(key)
            frames.append(frame())
        capture(
            "dictionary.gif",
            frames,
            [2600] * 3,
            "Dictionary opens three real authored definitions and everyday examples.",
        )
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
            "requested_end": requested_end.isoformat(),
            "provider_warnings": list(data.warnings),
            "price_basis": data.price_basis,
            "platform": app.platformName(),
            "width": 1366,
            "height": 768,
            "motion": "Deterministic native replay/navigation captures; transitions disabled.",
            "branding": "Decorative illustration; never claimed as stock observations.",
            "captures": captures,
        }
        (IMAGES / "gif-captures.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        print(f"Captured five native GIF demos from {len(data.candles)} actual observations.")
    finally:
        window.close()
        window.deleteLater()
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
        "--end",
        type=date.fromisoformat,
        help="Explicit final requested history date (YYYY-MM-DD), recorded in provenance.",
    )
    args = parser.parse_args()
    if not (args.brand or args.gallery):
        parser.error("Choose --brand and/or --gallery; only --gallery retrieves market history.")
    app = QApplication([])
    if sys.platform == "win32" and app.platformName() == "offscreen":
        font = Path(os.environ["WINDIR"]) / "Fonts" / "segoeui.ttf"
        if QFontDatabase.addApplicationFont(str(font)) < 0:
            raise RuntimeError(f"Could not load installed UI font: {font}")
    if args.brand:
        build_brand()
    if args.gallery:
        build_gallery(app, args.end)


if __name__ == "__main__":
    main()
