# xpaper

**Morning newspaper PDF from an edition directory** — ReportLab Platypus frames
(Triplicate-inspired) plus an agent skill that scrapes X in the user’s browser,
writes `edition.yaml`, runs the CLI, and delivers the PDF in chat.

The **CLI never touches X credentials**. Scraping and rewriting are agent-side only.

## Install

```bash
pip install -e git+https://github.com/ianzepp/xpaper.git#egg=xpaper
# or from a checkout:
pip install -e .
```

Requires Python ≥ 3.11. Dependencies: `reportlab`, `pillow`, `pyyaml`.

## Quick start

```bash
# Copy the fictional sample edition
xpaper init-example ./my-edition

# Render Letter B&W PDF
xpaper render ./my-edition -o ./out.pdf
```

Or render the repo sample directly:

```bash
xpaper render examples/sample-edition -o /tmp/xpaper-smoke.pdf
```

## What you get

A **2-page Letter** newspaper in black and white:

| Page | Frames | Hierarchy |
|------|--------|-----------|
| **Front** | Lead (~2/3 width) + rail ear / fly / lower | Masthead + folio on canvas; vertical rule |
| **Inside** | Feature (~2/3) + rail + 4 briefs | Running head; band rule above briefs |

Photos are either **full-column width** (optional `max_h` crop) or **left runaround**
(~48% width + text beside via a 2-column table). All editorial copy and image
paths come from `edition.yaml` — nothing is hardcoded in the engine.

## Edition schema (overview)

```yaml
masthead:
  title: THE X PAPER
  eyebrow: ...
  subtitle: Morning Edition
  date_long: Friday, September 11, 2026
  vol: Vol. I, No. 1
  price: Free
  window: Prior eight hours
  handle: "@you"
  tagline: All the tweets fit to set in type.
  inside_section: National Affairs / Briefs & Diversions

index:
  - { page: "A1", hed: "Lead hed" }
  - { page: "2", hed: "Inside" }

pages:
  front:
    lead:      # kicker, hed, deck, byline, image, caption, body[], pull…
               # optional image2 + caption2 → runaround for body_runaround / last graf
    fly:       # secondary rail story
    sidebar:   # compact box above the quote
    quote_box: # kicker, hed, image, quote, cite
  inside:
    feature:   # page-2 lead (~2/3)
    rail:      # upper rail (e.g. microfiction)
    briefs:    # up to 4; optional after: / colophon: on a brief
```

Image paths are relative to the edition directory. See
`examples/sample-edition/edition.yaml` for a complete fictional demo.

## Agent skill

`skills/xpaper/SKILL.md` — Vivarium-style instructions for an agent that:

1. Uses the **user’s browser** to read X (no CLI login, no stored X tokens).
2. Rewrites posts into newspaper prose and saves grayscale images under `images/`.
3. Writes `edition.yaml` and runs `xpaper render …`.
4. Delivers the PDF in chat.

See also `AGENTS.md` at the repo root.

## Non-goals

- **Not** a WeasyPrint / HTML multi-column path (that prototype lived elsewhere).
- **Not** an X API client — the package does not scrape, authenticate, or store feed credentials.
- **Not** a CMS — one edition directory in, one PDF out.
- **Not** color or tabloid yet (Letter B&W only; scale later).

## Fonts

Bundled OFL fonts (Playfair Display SC, Oswald, Libre Baskerville, Archivo Narrow)
ship under `src/xpaper/fonts/`. See [FONTS.md](FONTS.md). Code is MIT; fonts remain OFL.

## License

MIT © 2026 Ian Zepp — see [LICENSE](LICENSE).
