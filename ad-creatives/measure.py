#!/usr/bin/env python3
"""Measure every creative's text against the width it actually gets.

The artboards are published without ever being rendered here, so a headline
that wraps one line further than assumed silently pushes the text column into
the phone screenshot. This measures the real strings in the real faces.
"""
import io
import re
import urllib.parse
import urllib.request

from PIL import ImageFont

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}


def google_ttf(family, weight):
    """PIL cannot open woff2, so pull the ttf the legacy UA gets served."""
    css_url = (f"https://fonts.googleapis.com/css2?family={urllib.parse.quote_plus(family)}"
               f":wght@{weight}&display=swap")
    legacy = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    css = urllib.request.urlopen(urllib.request.Request(css_url, headers=legacy), timeout=30).read().decode()
    url = re.findall(r"url\((https://[^)]+\.ttf)\)", css)[0]
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()


BALOO = google_ttf("Baloo 2", 700)
NUNITO = google_ttf("Nunito", 600)

ART_W = 1080
PAD_X = 76           # the ad column's horizontal padding
HEAD_W = ART_W - 2 * PAD_X   # 928
SUB_W = 780          # the sub paragraph's max-width


def lines_needed(text, font_bytes, size, avail):
    """How many lines this string wraps to, and its widest run."""
    font = ImageFont.truetype(io.BytesIO(font_bytes), size)
    words, cur, count, widest = text.split(), "", 1, 0
    for w in words:
        trial = f"{cur} {w}".strip()
        width = font.getlength(trial)
        if width > avail and cur:
            widest = max(widest, font.getlength(cur))
            cur, count = w, count + 1
        else:
            cur = trial
    widest = max(widest, font.getlength(cur))
    return count, round(widest)


HEADLINES = [
    ("A line 1", "Menej „Kúpiš mi to?“", 84),
    ("A line 2", "Viac „Našetril som si.“", 84),
    ("B line 1", "Nemusíš sa", 96),
    ("B line 2", "pýtať.", 96),
    ("C line 1", "Nechceš mu splniť", 70),
    ("C line 2", "každý sen.", 70),
    ("C line 3", "Chceš ho naučiť,", 70),
    ("C line 4", "ako si ho splniť.", 70),
    ("D line 1", "Pre deti, ktorým", 84),
    ("D line 2", "rutina nejde sama.", 84),
]

SUBS = [
    ("A", "Amos učí deti zarobiť si vreckové a šetriť na to, po čom túžia.", 39),
    ("B", "Amos zadá úlohu, skontroluje fotku a vyplatí vreckové. Naťahovanie preberá za teba.", 39),
    ("C", "Plní úlohy, sleduje svoj pokrok a učí sa, že veci majú hodnotu.", 39),
    ("D", "Vždy len jedna úloha, okamžitá odmena a pravidlá, ktoré sa nemenia.", 39),
]

print(f"HEADLINES — available {HEAD_W}px")
for label, text, size in HEADLINES:
    n, w = lines_needed(text, BALOO, size, HEAD_W)
    flag = "  <-- WRAPS" if n > 1 else ""
    print(f"  {label:10} {size}px  {w:>4}px  {n} line(s){flag}   {text}")

print(f"\nSUBS — available {SUB_W}px")
for label, text, size in SUBS:
    n, w = lines_needed(text, NUNITO, size, SUB_W)
    print(f"  {label:10} {size}px  {w:>4}px  {n} line(s)   {text}")
