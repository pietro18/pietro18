#!/usr/bin/env python3
"""Generate the .dc.html artboards for the Amos Kids Meta campaign.

Two single-image ads (Feed 4:5 + Story 9:16, two copy variants) and a
five-card carousel.

Fonts are inlined as base64 because the canvas exporter does not embed Google
Fonts. Headlines use Baloo 2 rather than the app's Fredoka: Google serves no
Fredoka subset containing č, ď, ľ, ň, ŕ or ť, so Slovak headlines set in
Fredoka fall back to a system font mid-word.
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

DISPLAY = "'Baloo 2', 'Trebuchet MS', sans-serif"
BODY = "'Nunito', 'Trebuchet MS', sans-serif"

# Each face is subsetted to the whole Slovak alphabet, so no unicode-range
# splitting is needed and no glyph can silently fall back.
FONT_FACES = """
    @font-face {{ font-family: 'Baloo 2'; font-style: normal; font-weight: 700;
      font-display: block; src: url(data:font/woff2;base64,{baloo2}) format('woff2'); }}
    @font-face {{ font-family: 'Nunito'; font-style: normal; font-weight: 600;
      font-display: block; src: url(data:font/woff2;base64,{nunito600}) format('woff2'); }}
    @font-face {{ font-family: 'Nunito'; font-style: normal; font-weight: 700;
      font-display: block; src: url(data:font/woff2;base64,{nunito700}) format('woff2'); }}
""".format(baloo2=FONTS["baloo-2700"], nunito600=FONTS["nunito600"], nunito700=FONTS["nunito700"])

BACKDROP = f"""
  <div style="position: absolute; top: -18%; left: -12%; width: 760px; height: 760px; border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.16) 0%, rgba(255,255,255,0) 70%);"></div>
  <div style="position: absolute; bottom: -22%; right: -18%; width: 900px; height: 900px; border-radius: 50%; background: radial-gradient(circle, rgba(30,220,182,0.20) 0%, rgba(30,220,182,0) 68%);"></div>"""


def shell(width, height, inner):
    """The frame every artboard shares: brand gradient, glow, inlined fonts."""
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
<div style="position: relative; width: {width}px; height: {height}px; overflow: hidden; background: linear-gradient(158deg, {PURPLE_DEEP} 0%, {PURPLE_MID} 46%, {PURPLE_LIGHT} 100%); font-family: {BODY};">
{BACKDROP}
{inner}
</div>
</x-dc>
</body>
</html>
"""


def badge(text):
    return f"""    <div style="display: flex; align-items: center; gap: 14px; padding: 15px 30px; border-radius: 999px; background: {TEAL}; color: #05372C; font-size: 27px; font-weight: 700;">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#05372C" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M12 3l2.6 5.6 6.1.8-4.5 4.2 1.2 6-5.4-3-5.4 3 1.2-6L3.3 9.4l6.1-.8z"></path>
      </svg>
      {text}
    </div>"""


def cta(text, size=40):
    return f"""    <div style="display: flex; align-items: center; gap: 18px; padding: 27px 54px; border-radius: 999px; background: #ffffff; color: {PURPLE_DEEP}; font-family: {DISPLAY}; font-size: {size}px; font-weight: 700; box-shadow: 0 18px 40px rgba(23,4,58,0.32);">
      {text}
      <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="{PURPLE_DEEP}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M5 12h13"></path>
        <path d="M12 5l7 7-7 7"></path>
      </svg>
    </div>"""


def logo(width=244):
    return f'    <img src="amos-logo-white.png" alt="Amos.kids" style="width: {width}px; height: auto;">'


def headline(plain, accent, size=96):
    return f"""    <h1 style="margin: 0; font-family: {DISPLAY}; font-weight: 700; font-size: {size}px; line-height: 1.06; letter-spacing: -0.015em; color: #ffffff;">{plain}<br><span style="color: {AMBER};">{accent}</span></h1>"""


def struck_bubble(text, size=42):
    """The nagging question as a struck-through speech bubble.

    A tester read the old „…?“ / „Naposledy.“ pair as two unrelated lines: the
    quotation marks alone did not say who was speaking, and the ellipsis did
    not say the asking stops. The bubble names the speaker and the strikethrough
    carries "not any more" without spending words on either.
    """
    tail = ('<div style="position: absolute; left: 76px; bottom: -15px; width: 34px; height: 34px; '
            'background: #ffffff; transform: rotate(45deg);"></div>')
    return f"""    <div style="position: relative; display: inline-block; padding: 22px 40px; border-radius: 32px; background: #ffffff;">
      <span style="font-family: {BODY}; font-size: {size}px; font-weight: 700; color: #4B3A63; text-decoration: line-through; text-decoration-thickness: 5px; text-decoration-color: #E5484D;">{text}</span>
      {tail}
    </div>"""


def phone(src, top, width):
    return f"""  <img src="{src}" alt="Ukážka aplikácie Amos.kids" style="position: absolute; left: 50%; top: {top}px; width: {width}px; margin-left: -{width // 2}px; border-radius: 46px; box-shadow: 0 48px 90px rgba(23,4,58,0.55);">"""


# --------------------------------------------------------------------------
# Single-image ads
# --------------------------------------------------------------------------

def ad(*, width, height, pad_top, gap, phone_top, phone_width,
       phone_src, badge_text, head_html, sub, cta_text, phone_shift=0):
    inner = f"""{phone(phone_src, phone_top + phone_shift, phone_width)}

  <div style="position: relative; display: flex; flex-direction: column; align-items: center; gap: {gap}px; padding: {pad_top}px 76px 0; text-align: center;">

{logo()}

{badge(badge_text)}

{head_html}

    <p style="margin: 0; max-width: 780px; font-size: 39px; font-weight: 600; line-height: 1.38; color: rgba(255,255,255,0.9); text-wrap: pretty;">{sub}</p>

{cta(cta_text)}

  </div>"""
    return shell(width, height, inner)


# Both hooks are pains the app's own landing copy names: the endless "buy me
# that" and the endless reminding. Variant B used to be a benefit ("learn the
# value of money") — a vitamin, not a painkiller.
VARIANTS = {
    "A": dict(
        badge_text="Zadarmo pre prvých 333 rodín",
        head_html=headline("Už žiadne", "„Kúpiš mi to?“"),
        sub="Dieťa si na svoje veci zarobí samo — cez bežné úlohy doma.",
        cta_text="Chcem to skúsiť",
        phone_src="tasks-rewards.jpg",
    ),
    "B": dict(
        badge_text="Zadarmo pre prvých 333 rodín",
        head_html=struck_bubble("Urobil si si úlohy?") + "\n"
                  + headline("Nemusíš sa", "pýtať."),
        sub="Amos zadá úlohu, skontroluje fotku a vyplatí vreckové. Naťahovanie preberá za teba.",
        cta_text="Chcem to skúsiť",
        phone_src="parent-overview.jpg",
        phone_shift=40,  # the bubble makes this column taller than variant A's
    ),
}

# The text column runs ~545px of children plus gaps plus pad_top; phone_top
# clears that by enough for the CTA's drop shadow (~58px) to miss the phone.
FEED = dict(width=1080, height=1350, pad_top=74, gap=34, phone_top=848, phone_width=600)
# Story keeps everything inside the ~250px safe zones, with slack for Reels'
# deeper top chrome.
STORY = dict(width=1080, height=1920, pad_top=304, gap=40, phone_top=1092, phone_width=660)


# --------------------------------------------------------------------------
# Carousel — 5 cards, swiped left to right
# --------------------------------------------------------------------------

def card(*, step, head, body_text, phone_src=None, closing=False):
    """One carousel card. Cards 2-4 carry a screenshot; 1 and 5 are all type."""
    if closing:
        block = f"""  <div style="position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 40px; padding: 0 92px; text-align: center;">
{logo(280)}
    <h2 style="margin: 0; font-family: {DISPLAY}; font-weight: 700; font-size: 82px; line-height: 1.08; color: #ffffff;">{head}</h2>
    <p style="margin: 0; font-size: 38px; font-weight: 600; line-height: 1.4; color: rgba(255,255,255,0.9); text-wrap: pretty;">{body_text}</p>
{cta("Chcem to skúsiť", 42)}
    <p style="margin: 0; font-size: 27px; font-weight: 600; color: rgba(255,255,255,0.72);">Bez platobnej karty · Bez záväzkov</p>
  </div>"""
        return shell(1080, 1350, block)

    if phone_src is None:
        block = f"""  <div style="position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 46px; padding: 0 88px; text-align: center;">
{logo(244)}
{struck_bubble(head, 46)}
    <h2 style="margin: 0; font-family: {DISPLAY}; font-weight: 700; font-size: 104px; line-height: 1.04; letter-spacing: -0.015em; color: #ffffff;">{body_text}</h2>
    <p style="margin: 0; font-size: 28px; font-weight: 600; color: rgba(255,255,255,0.66);">Potiahni ďalej →</p>
  </div>"""
        return shell(1080, 1350, block)

    block = f"""{phone(phone_src, 742, 560)}

  <div style="position: relative; display: flex; flex-direction: column; align-items: center; gap: 30px; padding: 96px 88px 0; text-align: center;">
    <div style="display: flex; align-items: center; justify-content: center; width: 76px; height: 76px; border-radius: 50%; background: {AMBER}; color: #4A2A00; font-family: {DISPLAY}; font-size: 42px; font-weight: 700;">{step}</div>
    <h2 style="margin: 0; font-family: {DISPLAY}; font-weight: 700; font-size: 76px; line-height: 1.08; letter-spacing: -0.01em; color: #ffffff;">{head}</h2>
    <p style="margin: 0; max-width: 800px; font-size: 36px; font-weight: 600; line-height: 1.38; color: rgba(255,255,255,0.88); text-wrap: pretty;">{body_text}</p>
  </div>"""
    return shell(1080, 1350, block)


CARDS = [
    dict(step=0, head="Urobil si si úlohy?", body_text="Nemusíš sa pýtať."),
    dict(step=1, head="Zadáš úlohu s odmenou",
         body_text="Vyber si zo šablón alebo si vytvor vlastnú. Odmenu v eurách určuješ ty.",
         phone_src="tasks-rewards.jpg"),
    dict(step=2, head="Dieťa pošle fotku, AI ju skontroluje",
         body_text="Pravidlá sú každý deň rovnaké. Nemusíš byť rozhodca a nemusíte sa hádať.",
         phone_src="parent-overview.jpg"),
    dict(step=3, head="Odmena ide na sen, ktorý si vybralo samo",
         body_text="Bicykel, chrániče, lístok na hokej. Nie body pre body — naozajstné peniaze.",
         phone_src="goals-savings.jpg"),
    dict(step=4, head="Zadarmo navždy pre prvých 333 rodín",
         body_text="Prvých 333 rodín na Slovensku si prémiové funkcie zamkne zadarmo natrvalo.",
         closing=True),
]


# --------------------------------------------------------------------------

TARGETS = {}
for name, frame, variant in (("Main.dc.html", FEED, "A"), ("FeedB.dc.html", FEED, "B"),
                             ("StoryA.dc.html", STORY, "A"), ("StoryB.dc.html", STORY, "B")):
    TARGETS[name] = ad(**frame, **VARIANTS[variant])

for i, spec in enumerate(CARDS, start=1):
    TARGETS[f"Card{i}.dc.html"] = card(**spec)

for filename, html in TARGETS.items():
    (HERE / filename).write_text(html, encoding="utf-8")
    print("wrote", filename)

GAP_X, GAP_Y = 160, 220
canvas = {
    "artboards": [
        {"file": "Main.dc.html", "title": "Feed 4:5 — A · „Kúpiš mi to?“", "x": 0, "y": 0, "w": 1080, "h": 1350},
        {"file": "FeedB.dc.html", "title": "Feed 4:5 — B · Naposledy", "x": 1240, "y": 0, "w": 1080, "h": 1350},
        {"file": "StoryA.dc.html", "title": "Story 9:16 — A", "x": 2480, "y": 0, "w": 1080, "h": 1920},
        {"file": "StoryB.dc.html", "title": "Story 9:16 — B", "x": 3720, "y": 0, "w": 1080, "h": 1920},
    ] + [
        {"file": f"Card{i}.dc.html", "title": f"Carousel {i}/5", "x": (i - 1) * (1080 + GAP_X),
         "y": 1920 + GAP_Y, "w": 1080, "h": 1350}
        for i in range(1, 6)
    ],
    "annotations": [
        {
            "id": "campaign-note",
            "x": 4960,
            "y": 0,
            "w": 470,
            "text": (
                "Meta kampaň — 100 € / 6 dní\n\n"
                "Odkaz vo všetkých reklamách:\n"
                "https://amos.finance\n"
                "(funnel s Pixelom 302713312832266\n"
                "a Lead eventom pri registrácii)\n\n"
                "Feed 4:5 → FB/IG Feed\n"
                "Story 9:16 → Stories/Reels\n"
                "Carousel 1-5 → jedna reklama, 5 kariet\n\n"
                "Export: Export → PNG na každom artboarde.\n\n"
                "Pozor pri úprave textu: podnadpis nechaj\n"
                "do ~76 znakov, inak sa zalomí do 3 riadkov\n"
                "a v 4:5 naruší telefón.\n\n"
                "Over, či je ponuka „prvých 333 rodín“\n"
                "stále aktuálna — je prevzatá z textov\n"
                "na amos.kids."
            ),
        }
    ],
    "launch": {"view": "canvas"},
}
(HERE / "canvas.json").write_text(json.dumps(canvas, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote canvas.json")
