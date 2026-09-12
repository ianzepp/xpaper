"""US Tabloid 11×17 typewriter house style (locked X Paper look).

Cream stock + Special Elite everywhere, photo runaround lead, packed rail,
shared-baseline dateline band. Driven by edition.yaml via schema.load_edition.
"""

from __future__ import annotations

import random
import re
from pathlib import Path
from typing import Any

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    FrameBreak,
    HRFlowable,
    KeepInFrame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)

from .photos import photo_unit, runaround

TABLOID = (11 * inch, 17 * inch)  # 792 x 1224 pt

CREAM = HexColor("#F5F1E8")
INK = HexColor("#1A1A1A")
MUTED = HexColor("#333333")
RULE = HexColor("#222222")

PACKAGE_ROOT = Path(__file__).resolve().parent
FONTS_DIR = PACKAGE_ROOT / "fonts"
ASSETS_DIR = PACKAGE_ROOT / "assets"
GRAIN_ASSET = ASSETS_DIR / "paper-grain-tabloid.jpg"

_FONT_REGISTERED = False

_EM_DASH_RE = re.compile(r"[—–―]| -{2,} ")


def register_special_elite(fonts_dir: Path | None = None) -> None:
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return
    path = (fonts_dir or FONTS_DIR) / "SpecialElite-Regular.ttf"
    if not path.exists():
        raise FileNotFoundError(f"Missing bundled font: {path}")
    pdfmetrics.registerFont(TTFont("SpecialElite", str(path)))
    _FONT_REGISTERED = True


def house_copy(text: str) -> str:
    """Normalize copy to locked house style: no em/en dashes; use .."""
    if not text:
        return ""
    t = str(text)
    t = t.replace("—", "..").replace("–", "..").replace("―", "..")
    t = re.sub(r"\s*-{2,}\s*", " .. ", t)
    t = t.replace("→", "->")
    # Collapse accidental ".... " from double replacement of already-.. text
    t = re.sub(r"\.{3,}", "..", t)
    return t




def _tabloid_max_h(raw, default: float) -> float:
    """Ignore Letter-era tiny max_h values; tabloid needs larger photos."""
    if raw is None:
        return float(default)
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return float(default)
    # Letter layouts often use ~90–190 pt; bump if clearly letter-scaled
    if v < 200:
        return float(default)
    return v

def escape(text: str) -> str:
    t = house_copy(text)
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_styles() -> dict[str, ParagraphStyle]:
    return {
        "kicker": ParagraphStyle(
            "TT_Kicker", fontName="SpecialElite", fontSize=8, leading=10,
            textColor=INK, spaceAfter=2,
        ),
        "hed": ParagraphStyle(
            "TT_Hed", fontName="SpecialElite", fontSize=15.5, leading=18.5,
            textColor=INK, spaceAfter=5,
        ),
        "deck": ParagraphStyle(
            "TT_Deck", fontName="SpecialElite", fontSize=9.5, leading=12.5,
            textColor=MUTED, spaceAfter=3,
        ),
        "byline": ParagraphStyle(
            "TT_Byline", fontName="SpecialElite", fontSize=7.5, leading=9.5,
            textColor=MUTED, spaceAfter=7,
        ),
        "body": ParagraphStyle(
            "TT_Body", fontName="SpecialElite", fontSize=9, leading=12.5,
            textColor=INK, alignment=TA_LEFT, spaceAfter=6, firstLineIndent=12,
        ),
        "body_first": ParagraphStyle(
            "TT_BodyFirst", fontName="SpecialElite", fontSize=9, leading=12.5,
            textColor=INK, alignment=TA_LEFT, spaceAfter=6, firstLineIndent=0,
        ),
        "caption": ParagraphStyle(
            "TT_Caption", fontName="SpecialElite", fontSize=7, leading=9,
            textColor=MUTED, spaceBefore=2, spaceAfter=3,
        ),
        "pull": ParagraphStyle(
            "TT_Pull", fontName="SpecialElite", fontSize=10.5, leading=14,
            textColor=INK, alignment=TA_LEFT, leftIndent=10, rightIndent=10,
            spaceBefore=2, spaceAfter=1,
        ),
        "pull_attr": ParagraphStyle(
            "TT_PullAttr", fontName="SpecialElite", fontSize=7.5, leading=9.5,
            textColor=MUTED, leftIndent=10, spaceAfter=6,
        ),
        "jump": ParagraphStyle(
            "TT_Jump", fontName="SpecialElite", fontSize=7.5, leading=9.5,
            textColor=MUTED, spaceBefore=6, spaceAfter=2,
        ),
        "rail_kicker": ParagraphStyle(
            "TT_RailKicker", fontName="SpecialElite", fontSize=7, leading=9,
            textColor=INK, spaceAfter=2,
        ),
        "rail_hed": ParagraphStyle(
            "TT_RailHed", fontName="SpecialElite", fontSize=10, leading=12.5,
            textColor=INK, spaceAfter=3,
        ),
        "rail_byline": ParagraphStyle(
            "TT_RailByline", fontName="SpecialElite", fontSize=6.5, leading=8,
            textColor=MUTED, spaceAfter=4,
        ),
        "rail_body": ParagraphStyle(
            "TT_RailBody", fontName="SpecialElite", fontSize=7.5, leading=10.5,
            textColor=INK, alignment=TA_LEFT, spaceAfter=4, firstLineIndent=0,
        ),
        "rail_caption": ParagraphStyle(
            "TT_RailCaption", fontName="SpecialElite", fontSize=6, leading=7.5,
            textColor=MUTED, spaceBefore=1, spaceAfter=4,
        ),
        "brief_kicker": ParagraphStyle(
            "TT_BriefKicker", fontName="SpecialElite", fontSize=7, leading=9,
            textColor=INK, spaceAfter=1,
        ),
        "brief_hed": ParagraphStyle(
            "TT_BriefHed", fontName="SpecialElite", fontSize=9, leading=11,
            textColor=INK, spaceAfter=2,
        ),
        "brief_body": ParagraphStyle(
            "TT_BriefBody", fontName="SpecialElite", fontSize=7, leading=9.5,
            textColor=INK, alignment=TA_LEFT, spaceAfter=3,
        ),
        "note": ParagraphStyle(
            "TT_Note", fontName="SpecialElite", fontSize=6.5, leading=8,
            textColor=MUTED, spaceBefore=6,
        ),
        "section": ParagraphStyle(
            "TT_Section", fontName="SpecialElite", fontSize=8, leading=10,
            textColor=INK, alignment=TA_CENTER, spaceAfter=6,
        ),
    }


def _date_line(mast: dict) -> str:
    parts = [
        mast.get("date_long") or "",
        mast.get("subtitle") or "",
        mast.get("vol") or "",
        mast.get("price") or "",
    ]
    cleaned = []
    for p in parts:
        p = house_copy(str(p)).strip()
        if not p:
            continue
        if p.lower().startswith("price:") is False and "free" in p.lower() and "price" not in p.lower():
            # keep as-is; edition may already say "Price: Free"
            pass
        cleaned.append(p)
    # Dedupe adjacent empties; join with middot
    return "  ·  ".join(cleaned)


def draw_masthead(c: canvas.Canvas, width: float, top: float, mast: dict, left_label: str) -> float:
    """Draw masthead + dateline band. Returns y of the band bottom rule."""
    c.setFillColor(INK)
    c.setFont("SpecialElite", 9)
    eyebrow = house_copy(mast.get("eyebrow") or "")
    c.drawCentredString(width / 2, top, eyebrow)

    title = house_copy(mast.get("title") or "THE X PAPER")
    size = 36
    c.setFont("SpecialElite", size)
    total_w = c.stringWidth(title, "SpecialElite", size)
    x = (width - total_w) / 2
    rng = random.Random(7)
    y_base = top - 38
    for ch in title:
        jy = rng.uniform(-0.7, 0.7)
        jx = rng.uniform(-0.35, 0.35)
        c.drawString(x + jx, y_base + jy, ch)
        x += c.stringWidth(ch, "SpecialElite", size) + rng.uniform(-0.4, 0.55)

    c.setFont("SpecialElite", 9)
    tagline = house_copy(mast.get("tagline") or "All the tweets fit to set in type.")
    c.drawCentredString(width / 2, top - 56, tagline)

    # Double rule above the dateline band
    y = top - 66
    left_x = 0.7 * inch
    right_x = width - 0.7 * inch
    c.setStrokeColor(RULE)
    c.setLineWidth(0.9)
    c.line(left_x, y, right_x, y - 0.4)
    c.setLineWidth(0.3)
    c.line(0.68 * inch, y - 3.0, width - 0.72 * inch, y - 2.4)

    # Taller band so Special Elite descenders clear the bottom rule.
    # Left / center / right share one baseline, optically centered in the band.
    band_top = y - 3.0
    band_h = 26.0
    bottom_rule_y = band_top - band_h
    font_size = 8
    mid_y = (band_top + bottom_rule_y) / 2.0
    baseline = mid_y - font_size * 0.35

    c.setFillColor(INK)
    c.setFont("SpecialElite", font_size)
    c.drawString(left_x, baseline, house_copy(left_label)[:48] or "Front page")
    c.drawCentredString(width / 2, baseline, _date_line(mast))
    c.drawRightString(right_x, baseline, "IN THIS EDITION")

    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.line(left_x, bottom_rule_y, right_x, bottom_rule_y - 0.5)
    return bottom_rule_y



def fit(flowables, width, height):
    return KeepInFrame(width, height, list(flowables), mode="shrink", hAlign="LEFT", vAlign="TOP")

def _rail_items(front: dict) -> list[dict]:
    """Pack fly + sidebar + quote_box into rail slots (skip empties)."""
    items = []
    for key in ("fly", "sidebar", "quote_box"):
        block = front.get(key) or {}
        if block.get("hed") or block.get("body") or block.get("quote"):
            items.append(block)
    return items


def _lead_flowables(st, lead: dict, col_w: float, cache_dir: Path):
    story = []
    # Kicker lives in the masthead dateline band (left); story starts at hed.
    if lead.get("hed"):
        story.append(Paragraph(escape(lead["hed"]), st["hed"]))
    if lead.get("deck"):
        story.append(Paragraph(escape(lead["deck"]), st["deck"]))
    if lead.get("byline"):
        story.append(Paragraph(escape(lead["byline"]), st["byline"]))

    bodies = list(lead.get("body") or [])
    # Prefer image for runaround; image2 is alternate if present
    photo = lead.get("image") or lead.get("image2")
    caption = lead.get("caption") or lead.get("caption2") or ""
    wrap_paras = []
    if bodies:
        wrap_paras.append(Paragraph(escape(bodies[0]), st["body_first"]))
    if len(bodies) > 1:
        wrap_paras.append(Paragraph(escape(bodies[1]), st["body"]))
    rest = bodies[2:]

    if photo and Path(photo).exists() and wrap_paras:
        # Adapt photo_unit/runaround to expect styles dict with Caption key
        styles_bridge = {"Caption": st["caption"]}
        story.append(
            runaround(
                Path(photo),
                col_w,
                escape(caption),
                wrap_paras,
                styles_bridge,
                img_frac=float(lead.get("runaround_frac") or 0.47),
                gap=10,
                max_h=_tabloid_max_h(lead.get("runaround_max_h") or lead.get("hero_max_h"), 3.2 * inch),
                cache_dir=cache_dir,
            )
        )
    else:
        story.extend(wrap_paras)

    if lead.get("pull"):
        story.append(
            HRFlowable(
                width="40%", thickness=0.45, color=RULE,
                spaceBefore=2, spaceAfter=5, hAlign="LEFT",
            )
        )
        story.append(Paragraph(escape(lead["pull"]), st["pull"]))
        if lead.get("pull_attr"):
            story.append(Paragraph(escape(lead["pull_attr"]), st["pull_attr"]))
        story.append(
            HRFlowable(
                width="40%", thickness=0.45, color=RULE,
                spaceBefore=0, spaceAfter=6, hAlign="LEFT",
            )
        )
    for para in rest:
        story.append(Paragraph(escape(para), st["body"]))
    if lead.get("jump"):
        story.append(Paragraph(escape(lead["jump"]), st["jump"]))
    return story


def _one_rail_block(st, brief: dict, rail_w: float, cache_dir: Path):
    block = []
    if brief.get("kicker"):
        block.append(Paragraph(escape(brief["kicker"]), st["rail_kicker"]))
    if brief.get("hed"):
        block.append(Paragraph(escape(brief["hed"]), st["rail_hed"]))
    if brief.get("byline"):
        block.append(Paragraph(escape(brief["byline"]), st["rail_byline"]))

    photo = brief.get("image")
    if photo and Path(photo).exists():
        styles_bridge = {"Caption": st["rail_caption"]}
        img_w = max(rail_w - 4, 40)
        block.extend(
            photo_unit(
                Path(photo),
                img_w,
                escape(brief.get("caption") or ""),
                styles_bridge,
                max_h=_tabloid_max_h(brief.get("photo_max_h"), 1.6 * inch),
                cache_dir=cache_dir,
            )
        )
    for para in brief.get("body") or []:
        block.append(Paragraph(escape(para), st["rail_body"]))
    if brief.get("quote"):
        block.append(Paragraph(f"“{escape(brief['quote'])}”", st["rail_body"]))
    if brief.get("cite"):
        block.append(Paragraph(escape(brief["cite"]), st["rail_byline"]))
    return block


def _rail_flowables(st, items: list[dict], rail_w: float, cache_dir: Path):
    story = []
    for i, brief in enumerate(items):
        story.extend(_one_rail_block(st, brief, rail_w, cache_dir))
        if i < len(items) - 1:
            story.append(
                HRFlowable(
                    width="100%", thickness=0.35, color=RULE,
                    spaceBefore=10, spaceAfter=10, hAlign="CENTER",
                )
            )
    return story


def _brief_cell(st, brief: dict, w: float, cache_dir: Path):
    bits = []
    if brief.get("kicker"):
        bits.append(Paragraph(escape(brief["kicker"]), st["brief_kicker"]))
    if brief.get("hed"):
        bits.append(Paragraph(escape(brief["hed"]), st["brief_hed"]))
    if brief.get("byline"):
        bits.append(Paragraph(escape(brief["byline"]), st["rail_byline"]))
    photo = brief.get("image")
    if photo and Path(photo).exists():
        styles_bridge = {"Caption": st["rail_caption"]}
        bits.extend(
            photo_unit(
                Path(photo),
                max(w - 6, 40),
                escape(brief.get("caption") or ""),
                styles_bridge,
                max_h=_tabloid_max_h(brief.get("photo_max_h"), 90),
                cache_dir=cache_dir,
            )
        )
    for para in (brief.get("body") or [])[:2]:
        bits.append(Paragraph(escape(para), st["brief_body"]))
    if not bits:
        bits.append(Paragraph("..", st["brief_body"]))
    return bits


def _inside_lead(st, feature: dict, col_w: float, cache_dir: Path):
    """Page-2 feature: full-width photo optional, then body."""
    story = []
    if feature.get("kicker"):
        story.append(Paragraph(escape(feature["kicker"]), st["kicker"]))
    if feature.get("hed"):
        story.append(Paragraph(escape(feature["hed"]), st["hed"]))
    if feature.get("deck"):
        story.append(Paragraph(escape(feature["deck"]), st["deck"]))
    if feature.get("byline"):
        story.append(Paragraph(escape(feature["byline"]), st["byline"]))

    bodies = list(feature.get("body") or [])
    photo = feature.get("image")
    caption = feature.get("caption") or ""
    wrap = []
    if bodies:
        wrap.append(Paragraph(escape(bodies[0]), st["body_first"]))
    if len(bodies) > 1:
        wrap.append(Paragraph(escape(bodies[1]), st["body"]))
    rest = bodies[2:]

    if photo and Path(photo).exists() and wrap:
        styles_bridge = {"Caption": st["caption"]}
        story.append(
            runaround(
                Path(photo),
                col_w,
                escape(caption),
                wrap,
                styles_bridge,
                img_frac=0.45,
                gap=10,
                max_h=2.8 * inch,
                cache_dir=cache_dir,
            )
        )
    else:
        story.extend(wrap)

    if feature.get("pull"):
        story.append(
            HRFlowable(width="40%", thickness=0.45, color=RULE, spaceBefore=2, spaceAfter=5, hAlign="LEFT")
        )
        story.append(Paragraph(escape(feature["pull"]), st["pull"]))
        if feature.get("pull_attr"):
            story.append(Paragraph(escape(feature["pull_attr"]), st["pull_attr"]))
        story.append(
            HRFlowable(width="40%", thickness=0.45, color=RULE, spaceBefore=0, spaceAfter=6, hAlign="LEFT")
        )
    for para in rest:
        story.append(Paragraph(escape(para), st["body"]))
    return story


def render_tabloid(data: dict[str, Any], output: Path) -> Path:
    """Render locked US Tabloid typewriter PDF from a loaded edition dict."""
    register_special_elite()
    st = make_styles()
    cache_dir = Path(data["cache_dir"])
    cache_dir.mkdir(parents=True, exist_ok=True)
    mast = data["masthead"]
    front = data["front"]
    inside = data["inside"]
    lead = front["lead"]
    rail_items = _rail_items(front)
    briefs = [b for b in (inside.get("briefs") or []) if b.get("hed") or b.get("body")]
    feature = inside.get("feature") or {}
    rail_story = inside.get("rail") or {}

    page_w, page_h = TABLOID
    left = 0.65 * inch
    right = 0.65 * inch
    bottom = 0.55 * inch
    # Content top sits below deepened dateline band (~1.85")
    top_content = page_h - 1.85 * inch
    gutter = 14
    content_w = page_w - left - right
    main_w = content_w * 0.67
    rail_w = content_w - main_w - gutter
    # Reserve a briefs band on page 1 when we have briefs
    briefs_band_h = 2.35 * inch if briefs else 0
    frame_h = top_content - bottom - (briefs_band_h + 8 if briefs_band_h else 0)
    briefs_bottom = bottom
    main_bottom = bottom + (briefs_band_h + 8 if briefs_band_h else 0)

    grain = GRAIN_ASSET if GRAIN_ASSET.exists() else None
    left_label = house_copy(lead.get("kicker") or "Front page")

    main_frame = Frame(
        left, main_bottom, main_w, frame_h,
        id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, showBoundary=0,
    )
    rail_frame = Frame(
        left + main_w + gutter, main_bottom, rail_w, frame_h,
        id="rail", leftPadding=8, rightPadding=0, topPadding=0, bottomPadding=0, showBoundary=0,
    )
    frames_front = [main_frame, rail_frame]
    if briefs_band_h:
        # Up to 3 brief columns across the bottom band
        n = min(3, max(1, len(briefs)))
        gap_b = 10
        cell_w = (content_w - gap_b * (n - 1)) / n
        for i in range(n):
            frames_front.append(
                Frame(
                    left + i * (cell_w + gap_b),
                    briefs_bottom,
                    cell_w,
                    briefs_band_h,
                    id=f"brief_{i}",
                    leftPadding=2,
                    rightPadding=2,
                    topPadding=4,
                    bottomPadding=0,
                    showBoundary=0,
                )
            )

    # Inside page: feature + rail, full height (no briefs band; leftover briefs go here if any)
    inside_h = top_content - bottom
    inside_main = Frame(
        left, bottom, main_w, inside_h,
        id="inside_main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, showBoundary=0,
    )
    inside_rail = Frame(
        left + main_w + gutter, bottom, rail_w, inside_h,
        id="inside_rail", leftPadding=8, rightPadding=0, topPadding=0, bottomPadding=0, showBoundary=0,
    )

    class StockDoc(BaseDocTemplate):
        def __init__(self, filename, **kw):
            self._grain = grain
            self._mast = mast
            self._left_label = left_label
            BaseDocTemplate.__init__(self, filename, **kw)
            self.addPageTemplates(
                [
                    PageTemplate(id="Front", frames=frames_front, onPage=self._on_front),
                    PageTemplate(id="Inside", frames=[inside_main, inside_rail], onPage=self._on_inside),
                ]
            )

        def _paint_stock(self, c: canvas.Canvas):
            c.saveState()
            if self._grain and Path(self._grain).exists():
                c.drawImage(
                    str(self._grain), 0, 0,
                    width=page_w, height=page_h,
                    preserveAspectRatio=False, mask="auto",
                )
            else:
                c.setFillColor(CREAM)
                c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

        def _on_front(self, c: canvas.Canvas, doc):
            self._paint_stock(c)
            draw_masthead(c, page_w, page_h - 0.42 * inch, self._mast, self._left_label)
            rail_x = left + main_w + gutter / 2
            c.setStrokeColor(RULE)
            c.setLineWidth(0.45)
            c.line(rail_x, main_bottom + 4, rail_x, top_content - 4)
            if briefs_band_h:
                by = main_bottom - 4
                c.setLineWidth(0.6)
                c.line(left, by, page_w - right, by)
            c.setFillColor(MUTED)
            c.setFont("SpecialElite", 7)
            folio = house_copy(self._mast.get("folio_name") or self._mast.get("title") or "THE X PAPER")
            c.drawString(left, 0.38 * inch, f"{folio}  ·  tabloid typewriter  ·  11x17")
            c.drawRightString(page_w - right, 0.38 * inch, "A1")
            c.restoreState()

        def _on_inside(self, c: canvas.Canvas, doc):
            self._paint_stock(c)
            # Slimmer inside head: title + date on one line, then rule
            c.setFillColor(INK)
            c.setFont("SpecialElite", 11)
            title = house_copy(self._mast.get("title") or "THE X PAPER")
            c.drawString(left, page_h - 0.48 * inch, title)
            c.setFont("SpecialElite", 8)
            c.drawRightString(page_w - right, page_h - 0.48 * inch, _date_line(self._mast))
            c.setStrokeColor(RULE)
            c.setLineWidth(0.7)
            c.line(left, page_h - 0.58 * inch, page_w - right, page_h - 0.58 * inch)
            # Use same deepened top for content alignment via top_content
            # Draw a second band line matching front geometry
            c.setLineWidth(0.4)
            c.line(left, top_content + 6, page_w - right, top_content + 6)
            rail_x = left + main_w + gutter / 2
            c.setLineWidth(0.45)
            c.line(rail_x, bottom + 4, rail_x, top_content - 4)
            c.setFillColor(MUTED)
            c.setFont("SpecialElite", 7)
            folio = house_copy(self._mast.get("folio_name") or self._mast.get("title") or "THE X PAPER")
            c.drawString(left, 0.38 * inch, f"{folio}  ·  tabloid typewriter  ·  11x17")
            c.drawRightString(page_w - right, 0.38 * inch, "2")
            c.restoreState()

    meta = data["meta"]
    doc = StockDoc(
        str(output),
        pagesize=TABLOID,
        title=meta.get("title") or "THE X PAPER",
        author=str(meta.get("author") or "xpaper"),
    )

    story: list = []
    story.append(fit(_lead_flowables(st, lead, main_w, cache_dir), main_w - 2, frame_h - 2))
    story.append(FrameBreak())
    # Prefer 2–3 rail items for a packed look
    story.append(
        fit(_rail_flowables(st, rail_items[:3], rail_w - 8, cache_dir), rail_w - 4, frame_h - 2)
    )

    if briefs_band_h:
        n = min(3, max(1, len(briefs)))
        cell_w = (content_w - 10 * (n - 1)) / n
        for i in range(n):
            story.append(FrameBreak())
            story.append(
                fit(_brief_cell(st, briefs[i], cell_w, cache_dir), cell_w - 4, briefs_band_h - 6)
            )
        leftover_briefs = briefs[n:]
    else:
        leftover_briefs = briefs

    # Page 2 if we have feature / rail / leftover briefs
    need_inside = bool(
        feature.get("hed") or feature.get("body") or rail_story.get("hed") or leftover_briefs
    )
    if need_inside:
        story.append(NextPageTemplate("Inside"))
        story.append(PageBreak())
        inside_bits = list(_inside_lead(st, feature, main_w, cache_dir))
        if leftover_briefs:
            inside_bits.append(Spacer(1, 8))
            inside_bits.append(Paragraph(escape("Also in this edition"), st["kicker"]))
            for b in leftover_briefs:
                inside_bits.append(Paragraph(escape(b.get("hed") or ""), st["rail_hed"]))
                for para in (b.get("body") or [])[:1]:
                    inside_bits.append(Paragraph(escape(para), st["body"]))
        story.append(fit(inside_bits, main_w - 2, inside_h - 2))
        story.append(FrameBreak())
        inside_rail_items = []
        if rail_story.get("hed") or rail_story.get("body"):
            inside_rail_items.append(rail_story)
        if len(rail_items) > 3:
            inside_rail_items.extend(rail_items[3:])
        if not inside_rail_items and leftover_briefs:
            inside_rail_items = leftover_briefs[:2]
        story.append(
            fit(
                _rail_flowables(st, inside_rail_items, rail_w - 8, cache_dir),
                rail_w - 4,
                inside_h - 2,
            )
        )

    doc.build(story)
    return output
