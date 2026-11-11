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
GOLD = "#e7c66b"
GREEN = "#3ce4a0"
INK = "#061b14"


def scope_svg(
    x: float = 64,
    y: float = 64,
    flash: float = 0,
    *,
    circular: bool = True,
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
        color = GREEN if closing < opening else "#e88472"
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
            f'<path d="M-22 0H-6" stroke="{GOLD}" stroke-width="1.3" opacity=".7"/>'
            f'<path d="M-5 -1.6H2L5 0L2 1.6H-5Z" fill="#fff1ba" stroke="{GOLD}" '
            'stroke-width=".5"/></g>'
        )
    if flash:
        target += (
            f'<circle cx="{x}" cy="{y}" r="{8 + 15 * flash}" fill="none" '
            f'stroke="{GOLD}" stroke-width="1.5" opacity="{flash}"/>'
            f'<path d="M64 53v22M53 64h22M56 56l16 16M56 72l16-16" '
            f'stroke="#fff1ba" stroke-width="2" opacity="{flash}"/>'
            f'<circle cx="{x}" cy="{y}" r="4" fill="#fff1ba" opacity="{flash}"/>'
        )
    shape = (
        '<circle cx="64" cy="64" r="58"/>'
        if circular
        else '<rect x="5" y="5" width="118" height="118"/>'
    )
    surface = (
        f'<circle cx="64" cy="64" r="59" fill="url(#glass)" stroke="{GOLD}" stroke-width="1.5"/>'
        if circular
        else f'<rect x="5" y="5" width="118" height="118" fill="url(#glass)" '
        f'stroke="{GOLD}" stroke-width="1.5"/>'
    )
    bezel = (
        f'<circle cx="64" cy="64" r="59" fill="none" stroke="{GOLD}" stroke-width="1.5"/>'
        f'<circle cx="64" cy="64" r="55.5" fill="none" stroke="{GREEN}" '
        'stroke-width=".5" stroke-opacity=".5"/>'
        if circular
        else ""
    )
    grid = (
        "M4 32h120M4 48h120M4 64h120M4 80h120M4 96h120"
        "M16 20v88M32 20v88M48 20v88M64 20v88M80 20v88M96 20v88M112 20v88"
        if circular
        else "".join(f"M5 {position}h118M{position} 5v118" for position in range(16, 113, 16))
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="352" height="352" '
        'viewBox="0 0 128 128">'
        "<title>StonksSniper circular candlestick scope</title>"
        "<desc>A gold reticle targets the center of an illustrated candlestick chart. "
        "The animation searches a square, fires a bullet and cuts to an equally wide circle. "
        "Decorative branding, not market data.</desc>"
        f'<defs><clipPath id="scope">{shape}</clipPath>'
        '<radialGradient id="glass"><stop stop-color="#103e2b"/>'
        f'<stop offset="1" stop-color="{INK}"/></radialGradient></defs>'
        f'{surface}<g clip-path="url(#scope)">'
        f'<path d="{grid}" '
        f'fill="none" stroke="{GREEN}" stroke-opacity=".10" stroke-width=".5"/>'
        f'{candles}<g transform="translate({x - 64:.3f} {y - 64:.3f})" '
        f'fill="none" stroke="{GOLD}" stroke-width="1.2">'
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


def render_svg(svg: str, size: int, *, circular: bool = True) -> Image.Image:
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
    if circular:
        clip.addEllipse(QRectF(4.25 * scale, 4.25 * scale, 119.5 * scale, 119.5 * scale))
    else:
        clip.addRect(QRectF(4.25 * scale, 4.25 * scale, 119.5 * scale, 119.5 * scale))
    painter.setClipPath(clip)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    return image_from_qt(image)


def save_gif(
    frames: list[Image.Image], path: Path, durations: list[int], *, transparent: bool = False
) -> None:
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
                        scope_svg(x + (tx - x) * progress, y + (ty - y) * progress, circular=False),
                        352,
                        circular=False,
                    )
                )
                durations.append((50, 70, 40, 90)[step - 1])
            x, y = tx, ty
    for step in range(1, 9):
        progress = 1 - (1 - step / 8) ** 3
        frames.append(
            render_svg(
                scope_svg(x + (64 - x) * progress, y + (64 - y) * progress, circular=False),
                352,
                circular=False,
            )
        )
        durations.append(70 if step < 8 else 450)
    for step in range(7):
        frames.append(render_svg(scope_svg(circular=False, bullet=step / 6), 352, circular=False))
        durations.append(60)
    for step in range(6):
        frames.append(
            render_svg(scope_svg(flash=1 - step / 6, circular=False), 352, circular=False)
        )
        durations.append(60)
    frames.append(render_svg(scope_svg(), 352))
    durations.append(1800)
    save_gif(frames, ASSETS / "logo.gif", durations, transparent=True)
    IMAGES.mkdir(parents=True, exist_ok=True)
    banner = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="144" '
        'viewBox="0 0 960 144"><defs>'
        '<linearGradient id="money"><stop stop-color="#08291b"/>'
        '<stop offset=".5" stop-color="#145133"/><stop offset="1" stop-color="#08291b"/>'
        '</linearGradient></defs><rect x="1" y="1" width="958" height="142" '
        f'fill="url(#money)" stroke="{GOLD}"/>'
        f'<path d="M24 28h80M856 28h80M24 116h80M856 116h80" stroke="{GOLD}" '
        'stroke-opacity=".6"/>'
        '<text x="480" y="78" text-anchor="middle" font-family="Segoe UI, sans-serif" '
        f'font-size="58" font-weight="700" letter-spacing="3" fill="{GOLD}">'
        'STONKSSNIPER</text><text x="480" y="113" text-anchor="middle" '
        f'font-family="Segoe UI, sans-serif" font-size="16" fill="{GREEN}" '
        'letter-spacing="2">LEARN THE IDEA. TEST IT ON REAL HISTORY.</text></svg>'
    )
    (IMAGES / "readme-banner.svg").write_text(banner, encoding="utf-8")
    for name, title, subtitle in (
        ("start", "Run the latest source", "Windows / Python / setup"),
        ("guide", "Understand the tool", "Simple lessons / rules / real data"),
        ("download", "Download prototype", "v0.1.0 / Python package"),
    ):
        button = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="86" '
            'viewBox="0 0 300 86"><defs>'
            '<linearGradient id="face" x2="0" y2="1">'
            '<stop stop-color="#1d5b39"/><stop offset="1" stop-color="#0b3020"/>'
            "</linearGradient></defs>"
            '<rect x="1" y="7" width="298" height="78" fill="#a08336"/>'
            f'<rect x="1" y="1" width="298" height="78" fill="url(#face)" stroke="{GOLD}"/>'
            f'<path d="M2 2h296" stroke="#fff0b0" stroke-opacity=".45"/>'
            '<text x="150" y="34" text-anchor="middle" font-family="Segoe UI, sans-serif" '
            f'font-size="18" font-weight="650" fill="{GOLD}">{escape(title)}</text>'
            '<text x="150" y="59" text-anchor="middle" font-family="Segoe UI, sans-serif" '
            f'font-size="12" fill="#b9d8bd">{escape(subtitle)}</text></svg>'
        )
        (IMAGES / f"button-{name}.svg").write_text(button, encoding="utf-8")
    print("Built matching square/circle logo, erratic search, bullet shot and centered still.")


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
