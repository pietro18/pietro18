#!/usr/bin/env python3
"""Render each artboard to a ready-to-upload PNG.

The canvas can only be shared inside the organisation because it declares
PNG/PDF export, so anyone outside it needs the files themselves. These are
rendered from the very same .dc.html sources the canvas carries, so what ships
is what the canvas shows.
"""
import pathlib
import re
import shutil

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
OUT = HERE / "png"
STAGE = HERE / ".export-stage"

# filename -> (width, height, exported name)
ARTBOARDS = {
    "Main.dc.html": (1080, 1350, "feed-4x5-A-nasetril-som-si"),
    "FeedB.dc.html": (1080, 1350, "feed-4x5-B-nemusis-sa-pytat"),
    "FeedC.dc.html": (1080, 1350, "feed-4x5-C-ako-si-ho-splnit"),
    "FeedD.dc.html": (1080, 1350, "feed-4x5-D-rutina-nejde-sama"),
    "StoryA.dc.html": (1080, 1920, "story-9x16-A-nasetril-som-si"),
    "StoryB.dc.html": (1080, 1920, "story-9x16-B-nemusis-sa-pytat"),
    "StoryC.dc.html": (1080, 1920, "story-9x16-C-ako-si-ho-splnit"),
    "StoryD.dc.html": (1080, 1920, "story-9x16-D-rutina-nejde-sama"),
    "Card1.dc.html": (1080, 1350, "carousel-1-nemusis-sa-pytat"),
    "Card2.dc.html": (1080, 1350, "carousel-2-zadas-ulohu"),
    "Card3.dc.html": (1080, 1350, "carousel-3-amos-skontroluje"),
    "Card4.dc.html": (1080, 1350, "carousel-4-sen"),
    "Card5.dc.html": (1080, 1350, "carousel-5-333-rodin"),
}

STYLE_RE = re.compile(r"<helmet>\s*(<style>.*?</style>)\s*</helmet>", re.S)
BODY_RE = re.compile(r"</helmet>(.*?)</x-dc>", re.S)


def standalone(dc_html: str) -> str:
    """Strip the Design Component wrapper, keeping the markup and the fonts."""
    style = STYLE_RE.search(dc_html).group(1)
    body = BODY_RE.search(dc_html).group(1)
    return (f'<!doctype html><html><head><meta charset="utf-8">{style}'
            f'<style>html,body{{margin:0;padding:0}}</style></head><body>{body}</body></html>')


def main():
    OUT.mkdir(exist_ok=True)
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir()
    # Images are referenced by bare filename, so they must sit beside the page.
    for img in ("tasks-rewards.jpg", "goals-savings.jpg", "parent-overview.jpg",
                "amos-logo-white.png"):
        shutil.copy(HERE / img, STAGE / img)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        for source, (w, h, name) in ARTBOARDS.items():
            page_file = STAGE / f"{name}.html"
            page_file.write_text(standalone((HERE / source).read_text(encoding="utf-8")),
                                 encoding="utf-8")

            page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            page.goto(page_file.as_uri())
            # Fonts are inlined as base64, so this only waits on layout and images.
            page.wait_for_load_state("networkidle")
            page.evaluate("document.fonts.ready")
            page.screenshot(path=str(OUT / f"{name}.png"), clip={"x": 0, "y": 0,
                                                                 "width": w, "height": h})
            page.close()
            print(f"{name}.png  {w}x{h}")
        browser.close()

    shutil.rmtree(STAGE)


if __name__ == "__main__":
    main()
