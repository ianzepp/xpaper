"""Assemble newspaper PDFs from a loaded edition (Letter or Tabloid themes)."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    FrameBreak,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
)

from . import layout as L
from .schema import load_edition
from .styles import make_styles, register_fonts

THEMES = ("tabloid-typewriter", "letter")
DEFAULT_THEME = "tabloid-typewriter"


def render_edition(
    edition_dir: Path | str,
    output: Path | str,
    *,
    theme: str = DEFAULT_THEME,
) -> Path:
    """Render *edition_dir*/edition.yaml to *output* PDF. Returns output path."""
    edition_dir = Path(edition_dir)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    theme = (theme or DEFAULT_THEME).strip().lower()
    if theme not in THEMES:
        raise ValueError(f"Unknown theme {theme!r}; choose from {THEMES}")

    data = load_edition(edition_dir)
    if theme == "tabloid-typewriter":
        from .tabloid import render_tabloid

        return render_tabloid(data, output)

    return _render_letter(data, output)


def _render_letter(data: dict, output: Path) -> Path:
    """Legacy Triplicate-inspired Letter B&W layout."""
    register_fonts()
    styles = make_styles()
    cache_dir = data["cache_dir"]
    cache_dir.mkdir(parents=True, exist_ok=True)

    meta = data["meta"]
    doc = BaseDocTemplate(
        str(output),
        pagesize=letter,
        leftMargin=L.MARGIN_X,
        rightMargin=L.MARGIN_X,
        topMargin=0.25 * inch,
        bottomMargin=L.MARGIN_B,
        title=meta["title"],
        author=str(meta["author"]),
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="Front", frames=L.front_frames(), onPage=L.make_folio_front(data)),
            PageTemplate(id="Inside", frames=L.inside_frames(), onPage=L.make_folio_inside(data)),
        ]
    )

    fg = L.front_geom()
    ig = L.inside_geom()
    front = data["front"]
    inside = data["inside"]
    briefs = list(inside["briefs"] or [])
    while len(briefs) < 4:
        briefs.append(
            {
                "kicker": "",
                "hed": "",
                "byline": "",
                "image": None,
                "caption": "",
                "body": [],
                "hed_style": "HedS",
                "body_style": "Micro",
                "photo_max_h": None,
                "after": None,
                "colophon": None,
            }
        )

    story = [
        L.build_lead(styles, front["lead"], fg["lead_w"], fg["height"], cache_dir),
        FrameBreak(),
        L.build_ear(styles, data["index"], fg["rail_w"], fg["ear_h"]),
        FrameBreak(),
        L.build_fly(styles, front["fly"], fg["rail_w"], fg["fly_h"], cache_dir),
        FrameBreak(),
        L.build_rail_lower(
            styles,
            front["sidebar"],
            front["quote_box"],
            fg["rail_w"],
            fg["lower_h"],
            cache_dir,
        ),
        NextPageTemplate("Inside"),
        PageBreak(),
        L.build_feature(styles, inside["feature"], ig["left_w"], ig["upper_h"], cache_dir),
        FrameBreak(),
        L.build_rail_story(styles, inside["rail"], ig["rail_w"], ig["upper_h"], cache_dir),
        FrameBreak(),
        L.build_brief(styles, briefs[0], ig["brief_ws"][0], ig["lower_h"], cache_dir),
        FrameBreak(),
        L.build_brief(styles, briefs[1], ig["brief_ws"][1], ig["lower_h"], cache_dir),
        FrameBreak(),
        L.build_brief(styles, briefs[2], ig["brief_ws"][2], ig["lower_h"], cache_dir),
        FrameBreak(),
        L.build_brief(styles, briefs[3], ig["brief_ws"][3], ig["lower_h"], cache_dir),
    ]
    doc.build(story)
    return output
