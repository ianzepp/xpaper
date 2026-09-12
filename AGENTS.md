# Agents — xpaper

## Prefer

1. **Skill first:** read [`skills/xpaper/SKILL.md`](skills/xpaper/SKILL.md) before inventing a workflow.
2. **CLI for PDF only:** `xpaper render <edition-dir> -o out.pdf`. Do not put X cookies, tokens, or passwords into the CLI or `edition.yaml`.
3. **Browser for X:** scrape / screenshot / copy posts with the user’s signed-in browser session. The user owns that session; the package never does.
4. **Edition dir as contract:** all stories, captions, and image paths live in `edition.yaml` + `images/`. The engine has no baked-in personal feed.

## Commands

```bash
pip install -e .          # from this checkout
xpaper init-example ./ed  # optional scaffold
xpaper render ./ed -o ./ed/out.pdf
# default theme = tabloid-typewriter (locked house style)
xpaper render ./ed -o ./ed/out-letter.pdf --theme letter
```

## Layout reminders (house style)

- US Tabloid 11×17; Special Elite; cream + grain.
- Front: lead ~2/3 with left runaround + rail (fly, sidebar, quote) + bottom briefs.
- Inside: feature ~2/3 + rail; leftover briefs spill.
- Copy: `..` not em dashes.
- Convert images to grayscale before referencing them.

## Do not

- Hardcode a specific user’s posts into `src/xpaper/`.
- Call X APIs from this package.
- Force-push `main` or rewrite published edition PDFs without being asked.
