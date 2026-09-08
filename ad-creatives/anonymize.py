#!/usr/bin/env python3
"""Anonymise the real children in the parent-overview screenshot.

The raw screenshot shows two real kids' faces and first names. Faces are
replaced with flat initial avatars — the pattern every app uses when a profile
has no photo, so it reads as product UI rather than as censorship — and the
names are replaced with placeholders.

Runs on the 2x upscale so the redrawn text stays crisp.
"""
import pathlib

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = pathlib.Path(__file__).parent
SCRATCH = pathlib.Path("/tmp/claude-0/-home-user-pietro18/3fa764af-69c5-5f05-9ba0-c3fd7794b95c/scratchpad")
S = 2  # working scale

# Stand-in identities. Initials must match the names.
# Radii measured from the source: they must reach the selection ring's inner
# edge, or a rim of the original photo survives around the replacement.
KIDS = [
    dict(name="Adam", initial="A", fill="#7B2AE8", cx=142.5, cy=136, r=26, selected=True),
    dict(name="Nina", initial="N", fill="#1EDCB6", cx=205.5, cy=135, r=26, selected=False),
]
NAME_BAND = (167, 178)          # y range of the names under the avatars
PRIPRAV_LINE = (79, 241, 214, 253)  # "Priprav Lukas na Amos"
PRIPRAV_TEXT = "Priprav Adam na Amos"


def load_font(weight, size):
    """nunito_0.ttf / nunito_1.ttf were fetched as the 600 and 700 weights."""
    for path in sorted(SCRATCH.glob("nunito_*.ttf")):
        font = ImageFont.truetype(str(path), size)
        name = (font.getname()[1] or "").lower()
        if weight == 700 and "bold" in name:
            return font
        if weight == 600 and "semibold" in name:
            return font
    # Fall back to whichever we have rather than dropping to a bitmap face.
    return ImageFont.truetype(str(sorted(SCRATCH.glob("nunito_*.ttf"))[0]), size)


src = Image.open(HERE.parent / "marketing-assets" / "parent-overview.png").convert("RGB")
w, h = src.size
im = src.resize((w * S, h * S), Image.LANCZOS)
draw = ImageDraw.Draw(im)

# The plate colours the screenshot actually uses, sampled from the source.
card_white = src.getpixel((160, 182))
lavender = src.getpixel((90, 262))
name_selected = "#7C3AED"
name_plain = "#374151"

SS = 4  # supersample the circles so their edges stay smooth

for kid in KIDS:
    cx, cy, r = kid["cx"] * S, kid["cy"] * S, kid["r"] * S

    # Wipe the photo, keeping the selection ring that sits outside it.
    disc = Image.new("L", (int(r * 2 * SS), int(r * 2 * SS)), 0)
    ImageDraw.Draw(disc).ellipse([0, 0, disc.width - 1, disc.height - 1], fill=255)
    disc = disc.resize((int(r * 2), int(r * 2)), Image.LANCZOS)
    im.paste(kid["fill"], (int(cx - r), int(cy - r)), disc)

    initial_font = load_font(700, int(r * 1.05))
    box = draw.textbbox((0, 0), kid["initial"], font=initial_font)
    draw.text(
        (cx - (box[2] - box[0]) / 2 - box[0], cy - (box[3] - box[1]) / 2 - box[1]),
        kid["initial"], font=initial_font, fill="#FFFFFF",
    )

    # Repaint the name strip, then set the replacement name centred on the avatar.
    top, bottom = NAME_BAND[0] * S, NAME_BAND[1] * S
    draw.rectangle([cx - int(r * 1.6), top, cx + int(r * 1.6), bottom], fill=card_white)
    name_font = load_font(700, int(9.5 * S))
    box = draw.textbbox((0, 0), kid["name"], font=name_font)
    draw.text(
        (cx - (box[2] - box[0]) / 2 - box[0], top - box[1] + 1),
        kid["name"], font=name_font,
        fill=name_selected if kid["selected"] else name_plain,
    )

# The prompt card repeats the child's name.
x0, y0, x1, y1 = [v * S for v in PRIPRAV_LINE]
draw.rectangle([x0 - 2, y0 - 2, x1 + 6, y1 + 2], fill=lavender)
line_font = load_font(700, int(10 * S))
box = draw.textbbox((0, 0), PRIPRAV_TEXT, font=line_font)
draw.text((x0, y0 - box[1] - 1), PRIPRAV_TEXT, font=line_font, fill="#1F2937")

im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=95, threshold=2))
im.save(HERE / "parent-overview.jpg", "JPEG", quality=68, optimize=True, progressive=True)
print("wrote parent-overview.jpg", im.size)

im.crop((110 * S, 85 * S, 340 * S, 275 * S)).resize((230 * 3, 190 * 3), Image.LANCZOS) \
  .save(SCRATCH / "anon_check.png")
print("wrote verification crop")
