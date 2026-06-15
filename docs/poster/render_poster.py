#!/usr/bin/env python3
"""Render poster.html to a PNG using Chrome headless.

Usage:
    uv run render-poster
    uv run render-poster --width 1680 --height 1600
    uv run render-poster --output docs/poster/poster.png
"""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Annotated

import typer

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

POSTER_HTML = Path(__file__).parent / "poster.html"
DEFAULT_OUTPUT = Path(__file__).parent / "poster.png"


def _find_chrome() -> str | None:
    for name in ("google-chrome", "chromium-browser", "chromium", "google-chrome-stable"):
        path = shutil.which(name)
        if path:
            return path
    return None


def render_poster(
    html: Annotated[Path, typer.Option(help="Input HTML file")] = POSTER_HTML,
    output: Annotated[Path, typer.Option("-o", "--output", help="Output PNG path")] = DEFAULT_OUTPUT,
    width: Annotated[int, typer.Option(help="Viewport width (px)")] = 1680,
    height: Annotated[int, typer.Option(help="Viewport height (px)")] = 1680,
) -> None:
    """Render the poster HTML to a PNG image using Chrome headless."""
    chrome = _find_chrome()
    if not chrome:
        raise typer.BadParameter(
            "No Chrome/Chromium found. Install google-chrome or chromium-browser."
        )

    html_uri = html.resolve().as_uri()
    out = output.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        chrome,
        "--headless",
        f"--screenshot={out}",
        f"--window-size={width},{height}",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        html_uri,
    ]

    log.info("Rendering %s → %s (%dx%d)", html.name, out.name, width, height)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if not out.exists():
        log.error("Chrome stderr: %s", result.stderr)
        raise typer.Exit(code=1)

    size_kb = out.stat().st_size / 1024
    log.info("Done: %s (%.0f KB)", out, size_kb)


render_poster_cmd = typer.Typer(callback=render_poster, invoke_without_command=True, no_args_is_help=False)

if __name__ == "__main__":
    render_poster_cmd()
