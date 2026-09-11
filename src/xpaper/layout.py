"""Page geometry, folios, and story builders (Triplicate-inspired frames)."""

from __future__ import annotations

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    Frame,
    HRFlowable,
    KeepInFrame,
    Paragraph,
)

from .photos import photo_unit, runaround
from .styles import INK, RULE

PAGE_W, PAGE_H = letter
MARGIN_X = 0.40 * inch
MARGIN_B = 0.36 * inch
GAP = 8
MAST_DEPTH = 92


def rule(space_before=1, space_after=2, weight=1):
    return HRFlowable(
        width="100%",
        thickness=weight,
        color=RULE,
        spaceBefore=space_before,
        spaceAfter=space_after,
    )


def light_rule(space_before=2, space_after=2):
    return HRFlowable(
        width="100%",
        thickness=0.4,
        color=HexColor("#666666"),
        spaceBefore=space_before,
        spaceAfter=space_after,
    )


def kicker(text: str, styles):
    return [
        Paragraph((text or "").upper(), styles["Kicker"]),
        HRFlowable(width="100%", thickness=1.15, color=RULE, spaceBefore=0, spaceAfter=2),
    ]


def fit(flowables, width, height):
    return KeepInFrame(width, height, list(flowables), mode="shrink", hAlign="LEFT", vAlign="TOP")


def front_geom():
    top = PAGE_H - MAST_DEPTH
    bottom = MARGIN_B + 8
    height = top - bottom
    usable_w = PAGE_W - 2 * MARGIN_X
    col = (usable_w - 2 * GAP) / 3
    lead_w = col * 2 + GAP
    rail_w = col
    rail_x = MARGIN_X + lead_w + GAP
    ear_h = 68
    gap_r = 5
    lower_h = height * 0.40
    fly_h = height - ear_h - lower_h - 2 * gap_r
    y_ear = top - ear_h
    y_fly = y_ear - gap_r - fly_h
    return {
        "top": top,
        "bottom": bottom,
        "height": height,
        "lead_w": lead_w,
        "rail_w": rail_w,
        "rail_x": rail_x,
        "ear_h": ear_h,
        "fly_h": fly_h,
        "lower_h": lower_h,
        "y_ear": y_ear,
        "y_fly": y_fly,
        "y_lower": bottom,
    }


def front_frames():
    g = front_geom()
    return [
        Frame(
            MARGIN_X,
            g["bottom"],
            g["lead_w"],
            g["height"],
            id="lead",
            showBoundary=0,
            leftPadding=0,
            rightPadding=3,
            topPadding=0,
            bottomPadding=0,
        ),
        Frame(
            g["rail_x"],
            g["y_ear"],
            g["rail_w"],
            g["ear_h"],
            id="rail_ear",
            showBoundary=0,
            leftPadding=2,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        ),
        Frame(
            g["rail_x"],
            g["y_fly"],
            g["rail_w"],
            g["fly_h"],
            id="rail_fly",
            showBoundary=0,
            leftPadding=2,
            rightPadding=0,
            topPadding=1,
            bottomPadding=0,
        ),
        Frame(
            g["rail_x"],
            g["y_lower"],
            g["rail_w"],
            g["lower_h"],
            id="rail_lower",
            showBoundary=0,
            leftPadding=2,
            rightPadding=0,
            topPadding=1,
            bottomPadding=0,
        ),
    ]


def inside_geom():
    top = PAGE_H - 0.28 * inch - 12
    bottom = MARGIN_B + 8
    usable_w = PAGE_W - 2 * MARGIN_X
    col = (usable_w - 2 * GAP) / 3
    left_w = col * 2 + GAP
    rail_w = col
    band_gap = 7
    total_h = top - bottom
    upper_h = total_h * 0.56
    lower_h = total_h - upper_h - band_gap
    upper_bottom = top - upper_h
    brief_gaps = 3 * 6
    weights = [0.23, 0.26, 0.26, 0.25]
    brief_ws = [usable_w * w for w in weights]
    scale = (usable_w - brief_gaps) / sum(brief_ws)
    brief_ws = [w * scale for w in brief_ws]
    xs = [MARGIN_X]
    for i in range(3):
        xs.append(xs[-1] + brief_ws[i] + 6)
    return {
        "top": top,
        "bottom": bottom,
        "upper_h": upper_h,
        "lower_h": lower_h,
        "upper_bottom": upper_bottom,
        "lower_bottom": bottom,
        "left_w": left_w,
        "rail_w": rail_w,
        "brief_ws": brief_ws,
        "xs": xs,
    }


def inside_frames():
    g = inside_geom()
    ids = ["national", "fable", "brief_0", "brief_1", "brief_2", "brief_3"]
    frames = [
        Frame(
            MARGIN_X,
            g["upper_bottom"],
            g["left_w"],
            g["upper_h"],
            id=ids[0],
            showBoundary=0,
            leftPadding=0,
            rightPadding=3,
            topPadding=0,
            bottomPadding=0,
        ),
        Frame(
            MARGIN_X + g["left_w"] + GAP,
            g["upper_bottom"],
            g["rail_w"],
            g["upper_h"],
            id=ids[1],
            showBoundary=0,
            leftPadding=3,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        ),
    ]
    pads = [
        (0, 2),
        (2, 2),
        (2, 2),
        (2, 0),
    ]
    for i in range(4):
        lp, rp = pads[i]
        frames.append(
            Frame(
                g["xs"][i],
                g["lower_bottom"],
                g["brief_ws"][i],
                g["lower_h"],
                id=ids[2 + i],
                showBoundary=0,
                leftPadding=lp,
                rightPadding=rp,
                topPadding=2,
                bottomPadding=0,
            )
        )
    return frames


def make_folio_front(edition: dict):
    mast = edition["masthead"]

    def draw(c, doc):
        top = PAGE_H - 0.22 * inch
        c.setFillColor(INK)
        c.setFont("Archivo", 6.5)
        c.drawCentredString(PAGE_W / 2, top, mast["eyebrow"].upper())
        c.setFont("PlayfairBlack", 32)
        c.drawCentredString(PAGE_W / 2, top - 32, mast["title"])
        c.setFont("Archivo", 7.5)
        c.drawCentredString(PAGE_W / 2, top - 45, mast["subtitle"].upper())
        y = top - 50
        c.setStrokeColor(RULE)
        c.setLineWidth(2.0)
        c.line(MARGIN_X, y, PAGE_W - MARGIN_X, y)
        c.setLineWidth(0.55)
        c.line(MARGIN_X, y - 2.5, PAGE_W - MARGIN_X, y - 2.5)
        y2 = y - 12
        c.setFont("Archivo", 6.2)
        c.drawString(MARGIN_X, y2, mast["vol"].upper())
        c.drawRightString(PAGE_W - MARGIN_X, y2, mast["price"].upper())
        parts = [p for p in (mast.get("date_long"), mast.get("window"), mast.get("handle")) if p]
        mid = "  ·  ".join(parts)
        c.drawCentredString(PAGE_W / 2, y2, mid.upper())
        c.setLineWidth(0.65)
        c.line(MARGIN_X, y2 - 4, PAGE_W - MARGIN_X, y2 - 4)
        folio = f"{mast.get('folio_name', mast['title'])}  ·  1"
        c.setFont("Archivo", 6.5)
        c.drawCentredString(PAGE_W / 2, 0.16 * inch, folio.upper())
        c.setLineWidth(0.5)
        c.line(MARGIN_X, 0.26 * inch, PAGE_W - MARGIN_X, 0.26 * inch)
        g = front_geom()
        vx = g["rail_x"] - GAP / 2
        c.setLineWidth(0.6)
        c.line(vx, g["bottom"], vx, g["top"])

    return draw


def make_folio_inside(edition: dict):
    mast = edition["masthead"]

    def draw(c, doc):
        y = PAGE_H - 0.28 * inch
        c.setStrokeColor(RULE)
        c.setLineWidth(1.4)
        c.line(MARGIN_X, y + 7, PAGE_W - MARGIN_X, y + 7)
        c.setFont("Archivo", 6.5)
        c.setFillColor(INK)
        bar = (
            f"{mast.get('folio_name', mast['title'])}  ·  "
            f"{mast.get('inside_section', '')}  ·  "
            f"{mast.get('date_long', '')}"
        )
        c.drawCentredString(PAGE_W / 2, y, bar)
        c.setLineWidth(0.5)
        c.line(MARGIN_X, y - 4, PAGE_W - MARGIN_X, y - 4)
        folio = f"{mast.get('folio_name', mast['title'])}  ·  2"
        c.setFont("Archivo", 6.5)
        c.drawCentredString(PAGE_W / 2, 0.16 * inch, folio.upper())
        c.line(MARGIN_X, 0.26 * inch, PAGE_W - MARGIN_X, 0.26 * inch)
        g = inside_geom()
        vx = MARGIN_X + g["left_w"] + GAP / 2
        c.setLineWidth(0.6)
        c.line(vx, g["upper_bottom"], vx, g["top"])
        by = g["upper_bottom"] - 3.5
        c.setLineWidth(1.2)
        c.line(MARGIN_X, by, PAGE_W - MARGIN_X, by)

    return draw


def _body_paras(texts, styles, *, first="Body", rest="BodyIndent"):
    out = []
    for i, t in enumerate(texts or []):
        if not t:
            continue
        style = styles[first] if i == 0 else styles[rest]
        out.append(Paragraph(t, style))
    return out


def build_lead(styles, lead, lead_w, lead_h, cache_dir):
    content_w = lead_w - 4
    flow = []
    if lead["kicker"]:
        flow.extend(kicker(lead["kicker"], styles))
    if lead["hed"]:
        hed_style = lead.get("hed_style") or "HedXL"
        flow.append(Paragraph(lead["hed"].upper(), styles[hed_style]))
    if lead["deck"]:
        flow.append(Paragraph(lead["deck"], styles["Deck"]))
    if lead["byline"]:
        flow.append(Paragraph(lead["byline"].upper(), styles["Byline"]))

    body = list(lead["body"] or [])
    body_run = list(lead["body_runaround"] or [])
    # Auto-split: if image2 and no explicit runaround body, last body graf → runaround
    if lead["image2"] and not body_run and len(body) > 2:
        body_run = [body[-1]]
        body = body[:-1]

    if lead["image"]:
        flow.extend(
            photo_unit(
                lead["image"],
                content_w,
                lead["caption"],
                styles,
                max_h=lead.get("hero_max_h") or 190,
                cache_dir=cache_dir,
            )
        )

    flow.extend(_body_paras(body, styles))

    if lead["pull"]:
        flow.append(Paragraph(f"“{lead['pull']}”", styles["Pull"]))
    if lead["pull_attr"]:
        flow.append(Paragraph(lead["pull_attr"], styles["PullAttr"]))

    if lead["image2"]:
        wrap_texts = _body_paras(body_run, styles, first="Body", rest="Body")
        if lead.get("jump"):
            wrap_texts.append(Paragraph(lead["jump"], styles["Jump"]))
        flow.append(
            runaround(
                lead["image2"],
                content_w,
                lead["caption2"],
                wrap_texts,
                styles,
                img_frac=lead.get("runaround_frac", 0.48),
                max_h=lead.get("runaround_max_h") or 118,
                cache_dir=cache_dir,
            )
        )
    elif lead.get("jump"):
        flow.append(Paragraph(lead["jump"], styles["Jump"]))

    return fit(flow, lead_w - 2, lead_h - 2)


def build_ear(styles, index, w, h):
    items = [*kicker("Inside This Edition", styles)]
    for item in index or []:
        page = item.get("page", "")
        hed = item.get("hed", "")
        items.append(Paragraph(f"<b>{page}</b>&nbsp;&nbsp;{hed}", styles["IndexItem"]))
    if len(items) == 1:
        items.append(Paragraph("—", styles["IndexItem"]))
    return fit(items, w - 2, h - 2)


def build_fly(styles, fly, rail_w, h, cache_dir):
    content_w = rail_w - 4
    flow = []
    if fly["kicker"]:
        flow.extend(kicker(fly["kicker"], styles))
    if fly["hed"]:
        flow.append(Paragraph(fly["hed"].upper(), styles[fly.get("hed_style") or "HedL"]))
    if fly["byline"]:
        flow.append(Paragraph(fly["byline"].upper(), styles["Byline"]))
    if fly["image"]:
        flow.extend(
            photo_unit(
                fly["image"],
                content_w,
                fly["caption"],
                styles,
                max_h=fly.get("photo_max_h") or 92,
                cache_dir=cache_dir,
            )
        )
    for t in fly["body"] or []:
        flow.append(Paragraph(t, styles["Micro"]))
    return fit(flow, rail_w - 2, h - 2)


def build_rail_lower(styles, sidebar, quote_box, rail_w, h, cache_dir):
    content_w = rail_w - 4
    flow = [rule(0, 2, 1.4)]
    if sidebar.get("kicker"):
        flow.append(Paragraph(sidebar["kicker"].upper(), styles["Kicker"]))
    if sidebar.get("hed"):
        flow.append(Paragraph(sidebar["hed"].upper(), styles[sidebar.get("hed_style") or "BoxHed"]))
    if sidebar.get("image"):
        flow.extend(
            photo_unit(
                sidebar["image"],
                content_w,
                sidebar.get("caption") or "",
                styles,
                max_h=sidebar.get("photo_max_h") or 44,
                cache_dir=cache_dir,
            )
        )
    for t in sidebar.get("body") or []:
        flow.append(Paragraph(t, styles["Micro"]))

    flow.append(rule(2, 3, 1.4))
    if quote_box.get("kicker"):
        flow.extend(kicker(quote_box["kicker"], styles))
    if quote_box.get("hed"):
        flow.append(Paragraph(quote_box["hed"].upper(), styles[quote_box.get("hed_style") or "HedS"]))
    if quote_box.get("image"):
        flow.extend(
            photo_unit(
                quote_box["image"],
                content_w,
                quote_box.get("caption") or "",
                styles,
                max_h=quote_box.get("photo_max_h") or 48,
                cache_dir=cache_dir,
            )
        )
    if quote_box.get("quote"):
        flow.append(Paragraph(f"“{quote_box['quote']}”", styles["Quote"]))
    if quote_box.get("cite"):
        flow.append(Paragraph(quote_box["cite"], styles["Cite"]))
    return fit(flow, rail_w - 2, h - 2)


def build_feature(styles, feature, width, height, cache_dir):
    content_w = width - 4
    flow = []
    if feature["kicker"]:
        flow.extend(kicker(feature["kicker"], styles))
    if feature["hed"]:
        flow.append(Paragraph(feature["hed"].upper(), styles[feature.get("hed_style") or "HedL"]))
    if feature["deck"]:
        flow.append(Paragraph(feature["deck"], styles["Deck"]))
    if feature["byline"]:
        flow.append(Paragraph(feature["byline"].upper(), styles["Byline"]))
    if feature["image"]:
        flow.extend(
            photo_unit(
                feature["image"],
                content_w,
                feature["caption"],
                styles,
                max_h=feature.get("photo_max_h") or 108,
                cache_dir=cache_dir,
            )
        )
    body = feature["body"] or []
    for i, t in enumerate(body):
        if i == 0:
            flow.append(Paragraph(t, styles["Body"]))
        elif i < 3:
            flow.append(Paragraph(t, styles["BodyIndent"]))
        else:
            flow.append(Paragraph(t, styles["Micro"]))
        if i == 1 and feature.get("pull"):
            flow.append(Paragraph(f"“{feature['pull']}”", styles["Pull"]))
            if feature.get("pull_attr"):
                flow.append(Paragraph(feature["pull_attr"], styles["PullAttr"]))
    if feature.get("pull") and len(body) <= 1:
        flow.append(Paragraph(f"“{feature['pull']}”", styles["Pull"]))
        if feature.get("pull_attr"):
            flow.append(Paragraph(feature["pull_attr"], styles["PullAttr"]))
    return fit(flow, width - 2, height - 2)


def build_rail_story(styles, rail, width, height, cache_dir):
    content_w = width - 4
    flow = []
    if rail["kicker"]:
        flow.extend(kicker(rail["kicker"], styles))
    if rail["hed"]:
        flow.append(Paragraph(rail["hed"].upper(), styles[rail.get("hed_style") or "HedM"]))
    if rail["byline"]:
        flow.append(Paragraph(rail["byline"].upper(), styles["Byline"]))
    if rail["image"]:
        flow.extend(
            photo_unit(
                rail["image"],
                content_w,
                rail["caption"],
                styles,
                max_h=rail.get("photo_max_h") or 120,
                cache_dir=cache_dir,
            )
        )
    for t in rail["body"] or []:
        flow.append(Paragraph(t, styles["Micro"]))
    if rail.get("note"):
        flow.append(Paragraph(rail["note"], styles["Micro"]))
    return fit(flow, width - 2, height - 2)


def build_brief(styles, brief, w, h, cache_dir):
    content_w = w - 4
    flow = []
    if brief.get("kicker"):
        flow.extend(kicker(brief["kicker"], styles))
    if brief.get("hed"):
        flow.append(Paragraph(brief["hed"].upper(), styles[brief.get("hed_style") or "HedS"]))
    if brief.get("byline"):
        flow.append(Paragraph(brief["byline"].upper(), styles["Byline"]))
    if brief.get("image"):
        flow.extend(
            photo_unit(
                brief["image"],
                content_w,
                brief.get("caption") or "",
                styles,
                max_h=brief.get("photo_max_h") or 72,
                cache_dir=cache_dir,
            )
        )
    body_style = styles[brief.get("body_style") or "Micro"]
    for t in brief.get("body") or []:
        flow.append(Paragraph(t, body_style))

    after = brief.get("after")
    if after:
        flow.append(light_rule(3, 2))
        if after.get("kicker"):
            flow.extend(kicker(after["kicker"], styles))
        for t in after.get("body") if isinstance(after.get("body"), list) else [after.get("body") or ""]:
            if t:
                flow.append(Paragraph(str(t), styles["Micro"]))

    colo = brief.get("colophon")
    if colo:
        flow.append(light_rule(2, 2))
        if colo.get("kicker"):
            flow.extend(kicker(colo["kicker"], styles))
        for line in colo.get("lines") or []:
            flow.append(Paragraph(str(line), styles["ColophonLine"]))
        flow.append(Paragraph("■", styles["ColophonLine"]))

    if not flow:
        flow.append(Paragraph("—", styles["Micro"]))
    return fit(flow, w - 2, h - 2)
