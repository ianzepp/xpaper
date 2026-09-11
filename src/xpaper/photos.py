"""Full-bleed column photos and left runaround helpers."""

from __future__ import annotations

from pathlib import Path

from reportlab.platypus import Image, Paragraph, Spacer, Table, TableStyle


def photo(
    path: Path,
    width: float,
    max_h: float | None = None,
    *,
    h_align: str = "LEFT",
    cache_dir: Path | None = None,
):
    """Force drawWidth to `width`; optional max_h via centered PIL crop."""
    if not path or not Path(path).exists():
        return Spacer(1, 2)
    path = Path(path)
    img = Image(str(path))
    iw, ih = float(img.imageWidth), float(img.imageHeight)
    if iw <= 0 or ih <= 0:
        return Spacer(1, 2)
    scale = width / iw
    dw, dh = width, ih * scale
    if max_h is not None and dh > max_h:
        try:
            from PIL import Image as PILImage

            with PILImage.open(path) as pil:
                pil = pil.convert("L")
                target_aspect = width / max_h
                src_aspect = iw / ih
                if src_aspect > target_aspect:
                    new_w = ih * target_aspect
                    left = (iw - new_w) / 2
                    box = (int(left), 0, int(left + new_w), int(ih))
                else:
                    new_h = iw / target_aspect
                    top = (ih - new_h) / 2
                    box = (0, int(top), int(iw), int(top + new_h))
                cropped = pil.crop(box)
                cdir = cache_dir or path.parent
                cdir.mkdir(parents=True, exist_ok=True)
                cache = cdir / f".crop_{path.stem}_{int(width)}x{int(max_h)}.jpg"
                if not cache.exists() or cache.stat().st_mtime < path.stat().st_mtime:
                    cropped.save(cache, quality=88)
                img = Image(str(cache))
                dw, dh = width, max_h
        except Exception:
            scale = min(width / iw, max_h / ih)
            dw, dh = iw * scale, ih * scale
    img.drawWidth = dw
    img.drawHeight = dh
    img.hAlign = h_align
    return img


def photo_unit(
    path: Path,
    width: float,
    caption_html: str,
    styles,
    max_h: float | None = None,
    cache_dir: Path | None = None,
):
    """Image + caption stacked; caption locked to image width."""
    img = photo(path, width, max_h, h_align="LEFT", cache_dir=cache_dir)
    cap = Paragraph(caption_html or "", styles["Caption"])
    unit = Table([[img], [cap]], colWidths=[width])
    unit.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (0, 0), 1),
                ("BOTTOMPADDING", (0, 1), (0, 1), 2),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    unit.hAlign = "LEFT"
    return [unit]


def runaround(
    path: Path,
    col_w: float,
    caption_html: str,
    text_flowables,
    styles,
    *,
    img_frac: float = 0.48,
    gap: float = 6,
    max_h: float | None = None,
    cache_dir: Path | None = None,
):
    """Left-aligned photo (~40–55% col) + text beside via 2-col Table."""
    img_w = col_w * img_frac
    text_w = col_w - img_w - gap
    left = photo_unit(path, img_w, caption_html, styles, max_h=max_h, cache_dir=cache_dir)[0]
    right = Table([[f] for f in list(text_flowables)], colWidths=[text_w])
    right.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    tbl = Table([[left, right]], colWidths=[img_w + gap, text_w])
    tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), gap),
                ("RIGHTPADDING", (1, 0), (1, 0), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    tbl.hAlign = "LEFT"
    return tbl
