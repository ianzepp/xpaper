"""xpaper CLI — render edition directories to newspaper PDFs."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .render import DEFAULT_THEME, THEMES


def _cmd_render(args: argparse.Namespace) -> int:
    from .render import render_edition

    edition_dir = Path(args.edition_dir).resolve()
    if not (edition_dir / "edition.yaml").exists():
        print(f"error: no edition.yaml in {edition_dir}", file=sys.stderr)
        return 1
    out = Path(args.output).resolve() if args.output else edition_dir / "out.pdf"
    theme = args.theme or DEFAULT_THEME
    try:
        path = render_edition(edition_dir, out, theme=theme)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"Wrote {path} ({path.stat().st_size} bytes)  [theme={theme}]")
    return 0


def _example_source() -> Path | None:
    """Locate packaged or repo-relative examples/sample-edition."""
    here = Path(__file__).resolve()
    candidates = [
        here.parents[2] / "examples" / "sample-edition",
        here.parents[3] / "examples" / "sample-edition",
        Path.cwd() / "examples" / "sample-edition",
    ]
    for c in candidates:
        if (c / "edition.yaml").exists():
            return c
    return None


def _cmd_init_example(args: argparse.Namespace) -> int:
    dest = Path(args.dest).resolve()
    src = _example_source()
    if src is None:
        print(
            "error: could not find bundled examples/sample-edition "
            "(install from the git checkout or copy examples/ manually)",
            file=sys.stderr,
        )
        return 1
    if dest.exists() and any(dest.iterdir()) and not args.force:
        print(f"error: {dest} is not empty (pass --force to overwrite)", file=sys.stderr)
        return 1
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src / "edition.yaml", dest / "edition.yaml")
    img_src = src / "images"
    img_dest = dest / "images"
    if img_src.exists():
        if img_dest.exists():
            shutil.rmtree(img_dest)
        shutil.copytree(img_src, img_dest)
    print(f"Initialized example edition at {dest}")
    print(f"Render with: xpaper render {dest} -o out.pdf")
    print(f"  (default theme: {DEFAULT_THEME}; pass --theme letter for Letter B&W)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="xpaper",
        description=(
            "Render a newspaper PDF from an edition directory. "
            f"Default theme: {DEFAULT_THEME} (US Tabloid 11×17, Special Elite)."
        ),
    )
    p.add_argument("--version", action="version", version="%(prog)s 0.2.0")
    sub = p.add_subparsers(dest="command", required=True)

    pr = sub.add_parser("render", help="Render edition.yaml → PDF")
    pr.add_argument("edition_dir", help="Directory containing edition.yaml (+ images/)")
    pr.add_argument("-o", "--output", help="Output PDF path (default: <edition-dir>/out.pdf)")
    pr.add_argument(
        "--theme",
        choices=list(THEMES),
        default=DEFAULT_THEME,
        help=(
            f"Layout theme (default: {DEFAULT_THEME}). "
            "tabloid-typewriter = locked house style; letter = legacy Triplicate Letter B&W."
        ),
    )
    pr.set_defaults(func=_cmd_render)

    pi = sub.add_parser("init-example", help="Copy the sample edition into a directory")
    pi.add_argument("dest", nargs="?", default="sample-edition", help="Destination directory")
    pi.add_argument("--force", action="store_true", help="Overwrite non-empty destination")
    pi.set_defaults(func=_cmd_init_example)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
