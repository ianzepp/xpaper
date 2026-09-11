---
name: xpaper
description: >-
  Use when the user wants a morning newspaper PDF from their X (Twitter) feed,
  an xpaper edition directory, or “print the wire” / Triplicate-style Letter B&W
  layout. Agent scrapes X in the user’s browser, writes edition.yaml, runs the
  xpaper CLI, and delivers the PDF. CLI never touches X credentials.
---

# xpaper

Produce a **2-page Letter black-and-white newspaper PDF** from a short window of
the user’s X feed (or any edition directory that already has `edition.yaml`).

## Core rule

**Split of duties**

| Who | Does |
|-----|------|
| **Agent + user’s browser** | Open X while signed in as the user; collect posts/images; rewrite into newspaper prose; write `edition.yaml` + `images/` |
| **`xpaper` CLI** | Layout only: `xpaper render <edition-dir> -o out.pdf` |

Never pass X cookies, tokens, passwords, or API keys to the CLI. Never store
them in the edition directory. If X is not reachable in the browser, stop and
tell the user — do not invent a login path inside this skill.

## When to use

- “Make my X paper / morning edition / wire PDF”
- “Render this edition directory with xpaper”
- Layout questions about lead/rail/briefs frames

## Prerequisites

```sh
pip install -e .   # or: pip install -e git+https://github.com/ianzepp/xpaper.git#egg=xpaper
xpaper --help
xpaper render --help
```

## Workflow

1. **Confirm window** — e.g. prior 8 hours on Following (For You only if Following is thin). Ask if unclear.
2. **Collect in the browser** — open x.com; capture posts worth printing (skip thin one-liners). Download or screenshot images; convert to **grayscale** (Pillow `convert("L")` is fine).
3. **Rewrite** — newspaper prose; attribute claims to named posters; no invented facts beyond ordinary connective phrasing.
4. **Write edition dir**
   ```text
   edition/
     edition.yaml
     images/*.jpg
   ```
   Use `xpaper init-example ./edition` for a schema scaffold, then replace copy and images. Schema details: repo `README.md` and `examples/sample-edition/edition.yaml`.
5. **Render**
   ```sh
   xpaper render ./edition -o ./edition/out.pdf
   ```
6. **Deliver** — attach or open the PDF in chat; briefly list what made A1 vs briefs.

## Layout contract (do not fight the engine)

- **Front:** lead ~2/3 width (hero full-bleed; optional `image2` left runaround); rail = index ear + fly + sidebar/quote.
- **Inside:** feature ~2/3 + rail + up to four briefs (`after:` / `colophon:` allowed on a brief).
- Drive **all** content from YAML — do not patch Python for one user’s stories.

## Non-goals

- No X API client in this skill’s CLI path.
- No WeasyPrint/HTML equal-column layout.
- No color/tabloid in v0.1.

## Failure modes

- Missing `edition.yaml` → create from `init-example` or the sample.
- Missing fonts after a broken install → reinstall the package (fonts are package data).
- Render shrinks photos oddly → set `photo_max_h` / `hero_max_h` so KeepInFrame does not squash full-bleed images.
