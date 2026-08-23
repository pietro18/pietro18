#!/usr/bin/env python3
"""Generate the .dc.html artboards for the Amos Kids Meta ad creatives.

Fonts are inlined as base64 @font-face so PNG export keeps the real brand
type (Google Fonts are not embedded by the canvas exporter).
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
FONTS = json.load(open(HERE / "fonts.b64.json"))

# Brand values lifted from the app's own src/index.css and header gradient.
PURPLE_DEEP = "#5B18D9"
PURPLE_MID = "#7B2AE8"
PURPLE_LIGHT = "#A65EE6"
AMBER = "#FFC94D"
TEAL = "#1EDCB6"
INK = "#1F2937"

FONT_FACES = """
    @font-face {{
      font-family: 'Fredoka'; font-style: normal; font-weight: 600 700;
      font-display: block;
      src: url(data:font/woff2;base64,{fredoka_latinext}) format('woff2');
      unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;
    }}
    @font-face {{
      font-family: 'Fredoka'; font-style: normal; font-weight: 600 700;
      font-display: block;
      src: url(data:font/woff2;base64,{fredoka_latin}) format('woff2');
      unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
    }}
    @font-face {{
      font-family: 'Nunito'; font-style: normal; font-weight: 600 700;
      font-display: block;
      src: url(data:font/woff2;base64,{nunito_latinext}) format('woff2');
      unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;
    }}
    @font-face {{
      font-family: 'Nunito'; font-style: normal; font-weight: 600 700;
      font-display: block;
      src: url(data:font/woff2;base64,{nunito_latin}) format('woff2');
      unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
    }}
""".format(**FONTS)


def artboard(*, width, height, pad_top, phone_top, phone_width, phone_src,
             badge, head_plain, head_accent, sub, cta, gap):
    """One ad artboard. Everything is inline-styled so it stays editable."""
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <style>
{FONT_FACES}
    body {{ margin: 0; }}
    a {{ color: {AMBER}; }}
    a:hover {{ color: #ffd977; }}
  </style>
</helmet>
<div style="position: relative; width: {width}px; height: {height}px; overflow: hidden; background: linear-gradient(158deg, {PURPLE_DEEP} 0%, {PURPLE_MID} 46%, {PURPLE_LIGHT} 100%); font-family: 'Nunito', 'Trebuchet MS', sans-serif;">

  <div style="position: absolute; top: -18%; left: -12%; width: 760px; height: 760px; border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.16) 0%, rgba(255,255,255,0) 70%);"></div>
  <div style="position: absolute; bottom: -22%; right: -18%; width: 900px; height: 900px; border-radius: 50%; background: radial-gradient(circle, rgba(30,220,182,0.20) 0%, rgba(30,220,182,0) 68%);"></div>

  <img src="{phone_src}" alt="Amos Kids" style="position: absolute; left: 50%; top: {phone_top}px; width: {phone_width}px; margin-left: -{phone_width // 2}px; border-radius: 46px; box-shadow: 0 48px 90px rgba(23,4,58,0.55);">

  <div style="position: relative; display: flex; flex-direction: column; align-items: center; gap: {gap}px; padding: {pad_top}px 76px 0; text-align: center;">

    <img src="amos-logo-white.png" alt="Amos.kids" style="width: 244px; height: auto;">

    <div style="display: flex; align-items: center; gap: 14px; padding: 15px 30px; border-radius: 999px; background: {TEAL}; color: #05372C; font-size: 27px; font-weight: 700; letter-spacing: 0.01em;">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#05372C" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M12 3l2.6 5.6 6.1.8-4.5 4.2 1.2 6-5.4-3-5.4 3 1.2-6L3.3 9.4l6.1-.8z"></path>
      </svg>
      {badge}
    </div>

    <h1 style="margin: 0; font-family: 'Fredoka', 'Trebuchet MS', sans-serif; font-weight: 700; font-size: 96px; line-height: 1.06; letter-spacing: -0.015em; color: #ffffff; text-wrap: balance;">{head_plain}<br><span style="color: {AMBER};">{head_accent}</span></h1>

    <p style="margin: 0; max-width: 780px; font-size: 39px; font-weight: 600; line-height: 1.38; color: rgba(255,255,255,0.9); text-wrap: pretty;">{sub}</p>

    <div style="display: flex; align-items: center; gap: 18px; padding: 27px 54px; border-radius: 999px; background: #ffffff; color: {PURPLE_DEEP}; font-family: 'Fredoka', 'Trebuchet MS', sans-serif; font-size: 40px; font-weight: 700; box-shadow: 0 18px 40px rgba(23,4,58,0.32);">
      {cta}
      <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="{PURPLE_DEEP}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M5 12h13"></path>
        <path d="M12 5l7 7-7 7"></path>
      </svg>
    </div>

  </div>
</div>
</x-dc>
</body>
</html>
"""


VARIANTS = {
    "A": dict(
        badge="Hľadáme prvých testerov",
        head_plain="Už žiadne",
        head_accent="„Kúpiš mi to?“",
        sub="Deti si na svoje veci zarobia samy — cez bežné úlohy doma.",
        cta="Vyskúšať zadarmo",
        phone_src="tasks-rewards.jpg",
    ),
    "B": dict(
        badge="Hľadáme prvých testerov",
        head_plain="Naučte deti",
        head_accent="hodnotu peňazí",
        sub="Vy zadáte úlohu, dieťa ju splní a šetrí si na svoj cieľ.",
        cta="Vyskúšať zadarmo",
        phone_src="goals-savings.jpg",
    ),
}

# Feed 4:5 — text block on top, phone bleeding off the bottom edge.
FEED = dict(width=1080, height=1350, pad_top=74, gap=34, phone_top=796, phone_width=600)
# Story 9:16 — everything that matters inside the ~250px safe zones.
STORY = dict(width=1080, height=1920, pad_top=262, gap=40, phone_top=1044, phone_width=660)

TARGETS = {
    "Main.dc.html": (FEED, "A"),
    "FeedB.dc.html": (FEED, "B"),
    "StoryA.dc.html": (STORY, "A"),
    "StoryB.dc.html": (STORY, "B"),
}

for filename, (frame, variant) in TARGETS.items():
    (HERE / filename).write_text(artboard(**frame, **VARIANTS[variant]), encoding="utf-8")
    print("wrote", filename)

canvas = {
    "artboards": [
        {"file": "Main.dc.html", "title": "Feed 4:5 — A", "x": 0, "y": 0, "w": 1080, "h": 1350},
        {"file": "FeedB.dc.html", "title": "Feed 4:5 — B", "x": 1240, "y": 0, "w": 1080, "h": 1350},
        {"file": "StoryA.dc.html", "title": "Story 9:16 — A", "x": 0, "y": 1560, "w": 1080, "h": 1920},
        {"file": "StoryB.dc.html", "title": "Story 9:16 — B", "x": 1240, "y": 1560, "w": 1080, "h": 1920},
    ],
    "annotations": [
        {
            "id": "campaign-note",
            "x": 2440,
            "y": 0,
            "w": 460,
            "text": "Meta kampaň — 100 € / 6 dní\n\nA = painkiller hook, B = benefit hook.\nOba vedú na family-finance-trail.lovable.app\n(Pixel 302713312832266, Lead event pri signupe).\n\nFeed 4:5 → FB/IG Feed\nStory 9:16 → Stories/Reels\n\nExport: Export → PNG na každom artboarde.",
        }
    ],
    "launch": {"view": "canvas"},
}
(HERE / "canvas.json").write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote canvas.json")
