#!/usr/bin/env python3
"""Fetch Fredoka + Nunito subsetted to the full Slovak alphabet.

Google's stock `latin-ext` subset of Fredoka is missing č, ľ, ň and ť, so those
letters fell back to a system font in the headlines. Asking for an explicit
`text=` subset returns one file per weight that really does carry them.
"""
import base64
import io
import json
import re
import urllib.parse
import urllib.request

from fontTools.ttLib import TTFont

# Everything Slovak copy can need, so edits in the canvas editor still render.
CHARSET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    "ÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽáäčďéíĺľňóôŕšťúýž"
    "ÖÜöüÇç"  # occasional loanwords
    " .,!?:;-–—_„“”‘’\"'()[]{}/%€$+&@#*=<>©®…°×"
)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
TARGETS = [("Baloo 2", 700), ("Nunito", 600), ("Nunito", 700)]


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()


out = {}
for family, weight in TARGETS:
    css_url = (f"https://fonts.googleapis.com/css2?family={urllib.parse.quote_plus(family)}:wght@{weight}"
               f"&text={urllib.parse.quote(CHARSET)}")
    css = fetch(css_url).decode()
    urls = re.findall(r"url\((https://[^)]+)\)", css)
    if not urls:
        raise SystemExit(f"no font url returned for {family} {weight}")

    data = fetch(urls[0])
    font = TTFont(io.BytesIO(data), lazy=True)
    covered = set()
    for table in font["cmap"].tables:
        covered |= set(table.cmap.keys())
    font.close()

    missing = [c for c in CHARSET if c != " " and ord(c) not in covered]
    if missing:
        raise SystemExit(f"{family} {weight} is still missing: {''.join(missing)}")

    key = f"{family.lower().replace(chr(32), chr(45))}{weight}"
    out[key] = base64.b64encode(data).decode()
    print(f"{key}: {len(data)} bytes, {len(covered)} glyphs, full Slovak coverage")

json.dump(out, open("fonts.b64.json", "w"))
print("wrote fonts.b64.json")
