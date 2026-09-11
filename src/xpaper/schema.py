"""Load and normalize edition.yaml into a render-ready dict."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def _as_list(val: Any) -> list[str]:
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x) for x in val]
    return [str(val)]


def _resolve_image(edition_dir: Path, rel: str | None) -> Path | None:
    if not rel:
        return None
    p = Path(rel)
    if not p.is_absolute():
        p = edition_dir / p
    return p


def load_edition(edition_dir: Path) -> dict[str, Any]:
    """Read edition.yaml from *edition_dir* and resolve image paths."""
    edition_dir = Path(edition_dir).resolve()
    yaml_path = edition_dir / "edition.yaml"
    if not yaml_path.exists():
        raise FileNotFoundError(f"No edition.yaml in {edition_dir}")
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError("edition.yaml must be a mapping at the top level")

    mast = dict(raw.get("masthead") or {})
    mast.setdefault("title", "THE X PAPER")
    mast.setdefault("eyebrow", "Morning Dispatch")
    mast.setdefault("subtitle", "Morning Edition")
    mast.setdefault("date_long", "")
    mast.setdefault("vol", "Vol. I")
    mast.setdefault("price", "Free")
    mast.setdefault("window", "")
    mast.setdefault("handle", "")
    mast.setdefault("tagline", "All the tweets fit to set in type.")
    mast.setdefault("folio_name", mast["title"])
    mast.setdefault("inside_section", "National Affairs / Briefs & Diversions")
    mast.setdefault("author", mast.get("handle") or "xpaper")

    index = []
    for item in raw.get("index") or []:
        if isinstance(item, dict):
            index.append({"page": str(item.get("page", "")), "hed": str(item.get("hed", ""))})
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            index.append({"page": str(item[0]), "hed": str(item[1])})

    def story(block: dict | None, *, default_hed_style: str = "HedL") -> dict:
        b = dict(block or {})
        body = _as_list(b.get("body"))
        body_run = _as_list(b.get("body_runaround"))
        # If body_runaround omitted but image2 present, put last body grafs in runaround
        image = _resolve_image(edition_dir, b.get("image"))
        image2 = _resolve_image(edition_dir, b.get("image2"))
        return {
            "kicker": str(b.get("kicker") or ""),
            "hed": str(b.get("hed") or ""),
            "deck": str(b.get("deck") or ""),
            "byline": str(b.get("byline") or ""),
            "image": image,
            "caption": str(b.get("caption") or ""),
            "image2": image2,
            "caption2": str(b.get("caption2") or ""),
            "pull": str(b.get("pull") or ""),
            "pull_attr": str(b.get("pull_attr") or ""),
            "body": body,
            "body_runaround": body_run,
            "jump": str(b.get("jump") or ""),
            "quote": str(b.get("quote") or ""),
            "cite": str(b.get("cite") or ""),
            "note": str(b.get("note") or ""),
            "hero_max_h": b.get("hero_max_h", b.get("photo_max_h")),
            "runaround_max_h": b.get("runaround_max_h", 118),
            "runaround_frac": float(b.get("runaround_frac", 0.48)),
            "photo_max_h": b.get("photo_max_h"),
            "hed_style": str(b.get("hed_style") or default_hed_style),
            "body_style": str(b.get("body_style") or "Body"),
            "after": b.get("after"),
            "colophon": b.get("colophon"),
        }

    pages = raw.get("pages") or {}
    front = pages.get("front") or {}
    inside = pages.get("inside") or {}

    briefs = []
    for br in inside.get("briefs") or []:
        s = story(br, default_hed_style="HedS")
        s["body_style"] = str(br.get("body_style") or "Micro")
        briefs.append(s)

    return {
        "edition_dir": edition_dir,
        "cache_dir": edition_dir / ".xpaper-cache",
        "masthead": mast,
        "index": index,
        "front": {
            "lead": story(front.get("lead"), default_hed_style="HedXL"),
            "fly": story(front.get("fly"), default_hed_style="HedL"),
            "sidebar": story(front.get("sidebar"), default_hed_style="BoxHed"),
            "quote_box": story(front.get("quote_box"), default_hed_style="HedS"),
        },
        "inside": {
            "feature": story(inside.get("feature"), default_hed_style="HedL"),
            "rail": story(inside.get("rail"), default_hed_style="HedM"),
            "briefs": briefs,
        },
        "meta": {
            "title": f"{mast['title']} — {mast.get('subtitle', '')} — {mast.get('date_long', '')}".strip(" —"),
            "author": mast["author"],
        },
    }
