# xpaper

**Morning newspaper PDF from an edition directory** — ReportLab Platypus frames
plus an agent skill that scrapes X in the user’s browser, writes `edition.yaml`,
runs the CLI, and delivers the PDF in chat.

**Locked house style (default):** US Tabloid **11×17** (792×1224 pt), full
**Special Elite** typewriter, cream `#F5F1E8` + paper grain, left photo
runaround, packed lead + rail + briefs. No em dashes in copy — use `..`.

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

# Render (default = tabloid-typewriter house style)
xpaper render ./my-edition -o ./out.pdf

# Legacy Letter B&W (Triplicate-inspired)
xpaper render ./my-edition -o ./out-letter.pdf --theme letter
```

Or render the repo sample directly:

```bash
xpaper render examples/sample-edition -o /tmp/xpaper-smoke.pdf
```

## Themes

| Theme | Flag | Page | Look |
|-------|------|------|------|
| **tabloid-typewriter** (default) | `--theme tabloid-typewriter` | US Tabloid 11×17 | Special Elite everywhere, cream + grain, runaround lead, packed rail + bottom briefs |
| letter | `--theme letter` | Letter | Oswald/Baskerville Triplicate frames (legacy) |

### House style rules (tabloid-typewriter)

- Full Special Elite (masthead too); slight letterpress jitter on the title
- Cream stock `#F5F1E8` with subtle paper grain
- Lead photo as **left runaround** (~45–50%), text on the right
- Dateline band: left / center / right on **one shared baseline**; bottom rule clears descenders
- Pages feel **packed**: lead + rail (2–3 items) + bottom briefs band when copy exists
- Copy: no em dashes — write `..` instead

## What you get (default theme)

A **1–2 page Tabloid** newspaper:

| Page | Frames | Hierarchy |
|------|--------|-----------|
| **A1** | Lead (~2/3) + rail (fly / sidebar / quote) + optional 3-brief band | Typewriter masthead + shared-baseline dateline |
| **2** | Feature (~2/3) + rail | Slim running head; leftover briefs spill here |

Photos are **left runaround** on the lead/feature (or full-column on rail/briefs).
All editorial copy and image paths come from `edition.yaml`.

## Edition schema (overview)

```yaml
masthead:
  title: THE X PAPER
  eyebrow: ...
  subtitle: Morning Edition
  date_long: Saturday, September 12, 2026
  vol: Vol. I, No. 12
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
               # image is the runaround photo in tabloid theme
    fly:       # secondary rail story
    sidebar:   # compact rail item
    quote_box: # kicker, hed, image, quote, cite
  inside:
    feature:   # page-2 lead (~2/3)
    rail:      # upper rail
    briefs:    # bottom band on A1 (up to 3) + spill to page 2
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

- **Not** a WeasyPrint / HTML multi-column path.
- **Not** an X API client — the package does not scrape, authenticate, or store feed credentials.
- **Not** a CMS — one edition directory in, one PDF out.

## Fonts

Bundled fonts ship under `src/xpaper/fonts/` (Special Elite + legacy Oswald /
Playfair / Baskerville / Archivo). Paper grain under `src/xpaper/assets/`.
See [FONTS.md](FONTS.md). Code is MIT; fonts remain under their own licenses.

## License

MIT © 2026 Ian Zepp — see [LICENSE](LICENSE).
