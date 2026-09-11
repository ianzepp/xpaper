"""Font registration and ParagraphStyle catalog."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

INK = HexColor("#111111")
RULE = HexColor("#000000")
MUTED = HexColor("#333333")

FONTS_DIR = Path(__file__).resolve().parent / "fonts"

_FONT_MAP = {
    "PlayfairBlack": "PlayfairDisplaySC-Black.ttf",
    "PlayfairBold": "PlayfairDisplaySC-Bold.ttf",
    "OswaldBold": "Oswald-Bold.ttf",
    "OswaldSemi": "Oswald-SemiBold.ttf",
    "Baskerville": "LibreBaskerville-Regular.ttf",
    "BaskervilleBold": "LibreBaskerville-Bold.ttf",
    "BaskervilleItalic": "LibreBaskerville-Italic.ttf",
    "Archivo": "ArchivoNarrow-Regular.ttf",
    "ArchivoBold": "ArchivoNarrow-Bold.ttf",
}

_registered = False


def register_fonts(fonts_dir: Path | None = None) -> None:
    global _registered
    if _registered:
        return
    root = fonts_dir or FONTS_DIR
    for name, fname in _FONT_MAP.items():
        path = root / fname
        if not path.exists():
            raise FileNotFoundError(f"Missing bundled font: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    _registered = True


def make_styles():
    styles = getSampleStyleSheet()
    specs = [
        ("Kicker", "OswaldSemi", 6.8, 8.5, INK, 0, 1),
        ("HedXL", "OswaldBold", 15.5, 16.2, INK, 0, 2),
        ("HedL", "OswaldBold", 11.5, 12.5, INK, 0, 2),
        ("HedM", "OswaldBold", 9.5, 10.5, INK, 0, 2),
        ("HedS", "OswaldBold", 8.2, 9.2, INK, 0, 1),
        ("Deck", "BaskervilleItalic", 8.0, 10.0, INK, 0, 2),
        ("Byline", "Archivo", 6.2, 7.5, MUTED, 0, 3),
        ("Body", "Baskerville", 7.5, 9.4, INK, 0, 3),
        ("BodyIndent", "Baskerville", 7.5, 9.4, INK, 0, 3),
        ("Micro", "Baskerville", 6.7, 8.4, INK, 0, 2),
        ("Caption", "Archivo", 5.7, 7.0, MUTED, 1, 3),
        ("Pull", "BaskervilleItalic", 8.5, 10.5, INK, 2, 1),
        ("PullAttr", "Archivo", 5.8, 7.0, MUTED, 0, 4),
        ("Quote", "BaskervilleItalic", 7.0, 8.8, INK, 0, 2),
        ("Cite", "Archivo", 5.5, 6.8, MUTED, 0, 1),
        ("IndexItem", "Archivo", 6.2, 8.0, INK, 0, 0),
        ("Jump", "OswaldSemi", 6.5, 8.0, INK, 3, 0),
        ("ColophonLine", "Archivo", 6.2, 7.8, INK, 0, 0),
        ("BoxHed", "OswaldBold", 7.8, 9.0, INK, 0, 2),
    ]
    for name, font, size, leading, color, sb, sa in specs:
        kw = dict(
            name=name,
            fontName=font,
            fontSize=size,
            leading=leading,
            textColor=color,
            spaceBefore=sb,
            spaceAfter=sa,
        )
        if name in ("Body", "BodyIndent", "Micro", "Deck"):
            kw["alignment"] = TA_JUSTIFY
        if name == "BodyIndent":
            kw["firstLineIndent"] = 9
        if name == "Jump":
            kw["alignment"] = TA_RIGHT
        if name in ("Pull", "PullAttr"):
            kw["leftIndent"] = 3
            kw["rightIndent"] = 3
        styles.add(ParagraphStyle(**kw))
    return styles
