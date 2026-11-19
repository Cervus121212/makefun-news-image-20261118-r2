#!/usr/bin/env python3
"""Porto Vela newsroom: draw the front page for Wednesday 18 November 2026.

Reads the two embedded photos from assets/ and draws a 1024x1024
newspaper front page with PIL + DejaVu fonts. Deterministic: no clock,
no randomness, no network. Run twice and the bytes are identical.

Usage:
    python3 generate.py [out/entry.png]
    MAKEFUN_OUTPUT_DIR=out python3 generate.py
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

# Newsprint palette: warm paper, near-black ink, one green accent for the
# lead story, one deep red for the storm story, slate for the strips.
PAPER = (247, 243, 234)
INK = (20, 20, 20)
INK_SOFT = (74, 74, 74)
RULE = (20, 20, 20)
GREEN = (46, 125, 50)
GREEN_DARK = (27, 94, 32)
RED = (178, 34, 34)
SLATE = (52, 73, 94)
HAIRLINE = (160, 155, 145)
CAPTION_BG = (232, 227, 216)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def serif_b(size):
    return font("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return font("DejaVuSerif.ttf", size)


def sans(size):
    return font("DejaVuSans.ttf", size)


def sans_b(size):
    return font("DejaVuSans-Bold.ttf", size)


def text_w(draw, text, fnt):
    """Width of one line of text in pixels."""
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def text_h(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[3] - box[1]


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap. Returns a list of lines that fit max_w."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if text_w(draw, trial, fnt) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    """Draw wrapped lines, return the y just below the last line."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def cover_crop(im, tw, th, focus_y=0.5):
    """Centre-crop an image to the target aspect, then resize (Lanczos).
    focus_y picks the crop window vertically: 0.0 = top, 0.5 = centre."""
    sw, sh = im.size
    target = tw / th
    src = sw / sh
    if src > target:  # too wide: trim sides
        nw = int(sh * target)
        left = (sw - nw) // 2
        im = im.crop((left, 0, left + nw, sh))
    else:  # too tall: trim top/bottom, biased by focus_y
        nh = int(sw / target)
        slack = sh - nh
        top = int(slack * focus_y)
        im = im.crop((0, top, sw, top + nh))
    return im.resize((tw, th), Image.LANCZOS)


def draw_caption(draw, x0, x1, y, text, size):
    """Caption on a tinted band; box height fits the wrapped lines."""
    fnt = serif(size)
    lines = wrap(draw, text, fnt, (x1 - x0) - 16)
    h = 8 + 18 * len(lines) + 6
    draw.rectangle([x0, y, x1, y + h], fill=CAPTION_BG)
    cy = y + 6
    for line in lines:
        draw.text((x0 + 8, cy), line, font=fnt, fill=INK_SOFT)
        cy += 18
    return y + h


def kicker(draw, x, y, label, color):
    """Small caps section label with a short rule after it."""
    fnt = sans_b(19)
    draw.text((x, y), label, font=fnt, fill=color)
    w = text_w(draw, label, fnt)
    draw.line([(x + w + 12, y + 10), (x + w + 52, y + 10)], fill=color, width=3)
    return y + 30


def rule(draw, x0, y, x1, width=2, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_masthead(draw):
    """Nameplate + date line + double rule."""
    y = 26
    title = "THE WORLD TODAY"
    fnt = serif_b(64)
    tw = text_w(draw, title, fnt)
    draw.text(((W - tw) // 2, y), title, font=fnt, fill=INK)
    y += 78
    rule(draw, 36, y, W - 36, width=3)
    y += 10
    left = "WEDNESDAY 18 NOVEMBER 2026"
    right = "WORLD NEWS IN ONE PAGE"
    f_left = sans_b(19)
    f_right = sans(19)
    draw.text((36, y), left, font=f_left, fill=INK)
    rw = text_w(draw, right, f_right)
    draw.text((W - 36 - rw, y), right, font=f_right, fill=INK_SOFT)
    y += 30
    rule(draw, 36, y, W - 36, width=1, fill=HAIRLINE)
    return y + 14


def draw_lead(draw, page, top):
    """Left column: NVIDIA Q3. Photo, headline, deck, body."""
    x0, x1 = 36, 640
    w = x1 - x0
    y = kicker(draw, x0, top, "TECHNOLOGY  ·  EARNINGS", GREEN_DARK)
    head = "NVIDIA POSTS RECORD\n$115.8BN QUARTER"
    f_head = serif_b(44)
    y = draw_lines(draw, head.split("\n"), x0, y, f_head, INK, 50)
    y += 6
    deck = "Data-centre sales hit $107.6bn as AI demand climbs."
    y = draw_lines(draw, wrap(draw, deck, sans(20), w), x0, y, sans(20),
                   INK_SOFT, 26)
    y += 10
    photo = Image.open(os.path.join(ASSETS, "huang_gesture.jpg")).convert("RGB")
    ph = cover_crop(photo, w, 252, focus_y=0.30)
    page.paste(ph, (x0, y))
    draw.rectangle([x0, y, x1 - 1, y + 251], outline=INK, width=2)
    y += 252
    y = draw_caption(draw, x0, x1, y,
                     "Jensen Huang, NVIDIA chief, at CES.", 15)
    y += 8
    body = ("Revenue rose 103% to $115.84bn in Q3 on data-centre "
            "sales of $107.6bn. The board turned down a comeback "
            "proposal from Huang.")
    y = draw_lines(draw, wrap(draw, body, sans(18), w), x0, y, sans(18),
                   INK, 25)
    return y


def draw_storm(draw, page, top):
    """Right column: Cyclone Akvan. Photo, headline, body."""
    x0, x1 = 664, 988
    w = x1 - x0
    y = kicker(draw, x0, top, "WEATHER  ·  INDIA", RED)
    head = "CYCLONE AKVAN\nBEARS DOWN\nON INDIA"
    f_head = serif_b(31)
    y = draw_lines(draw, head.split("\n"), x0, y, f_head, INK, 37)
    y += 8
    photo = Image.open(os.path.join(ASSETS, "akvan.jpg")).convert("RGB")
    ph = cover_crop(photo, w, 200, focus_y=0.5)
    page.paste(ph, (x0, y))
    draw.rectangle([x0, y, x1 - 1, y + 199], outline=INK, width=2)
    y += 200
    y = draw_caption(draw, x0, x1, y,
                     "Akvan from orbit, 18 Nov, before landfall.", 14)
    y += 8
    body = ("Due ashore 20 November with winds of 130 km/h. "
            "Seventy-four rescue teams stand by as towns board up "
            "and fishermen stay in port.")
    y = draw_lines(draw, wrap(draw, body, sans(17), w), x0, y, sans(17),
                   INK, 23)
    return y


def draw_spiral(draw, x, y, color):
    """Small cyclone swirl: three nested arcs around (x+20, y+20)."""
    cx, cy, r = x + 20, y + 20, 20
    for i, rr in enumerate((r, int(r * 0.66), int(r * 0.36))):
        draw.arc([cx - rr, cy - rr, cx + rr, cy + rr],
                 start=200 + i * 55, end=200 + i * 55 + 250,
                 fill=color, width=3)


def draw_passport(draw, x, y, color):
    """Small passport booklet with a star."""
    draw.rectangle([x, y, x + 34, y + 46], outline=color, width=3)
    draw.line([(x, y + 14), (x + 34, y + 14)], fill=color, width=2)
    cx, cy = x + 17, y + 32
    for ang in range(0, 360, 72):
        import math
        x2 = cx + 9 * math.cos(math.radians(ang - 90))
        y2 = cy + 9 * math.sin(math.radians(ang - 90))
        draw.line([(cx, cy), (x2, y2)], fill=color, width=2)


def draw_strip(draw, x0, x1, top, kicker_label, head, body, icon, color):
    """One bottom strip: icon, kicker, headline, two body lines."""
    w = x1 - x0
    y = kicker(draw, x0, top, kicker_label, color)
    f_head = serif_b(23)
    head_lines = wrap(draw, head, f_head, w - 56)
    hy = y
    for line in head_lines:
        draw.text((x0 + 56, hy), line, font=f_head, fill=INK)
        hy += 28
    icon(draw, x0 + 6, y + 4, color)
    y = max(hy, y + 52) + 4
    f_body = sans(16)
    y = draw_lines(draw, wrap(draw, body, f_body, w), x0, y, f_body,
                   INK_SOFT, 22)
    return y


def draw_footer(draw):
    y = H - 34
    rule(draw, 36, y, W - 36, width=1, fill=HAIRLINE)
    fnt = sans(12)
    line = ("Photos: Jensen Huang by Maurizio Pesce (CC BY 2.0) · "
            "Cyclone Akvan satellite view, NASA–JTWC via Wikimedia Commons")
    tw = text_w(draw, line, fnt)
    draw.text(((W - tw) // 2, y + 8), line, font=fnt, fill=INK_SOFT)


def build():
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)
    y = draw_masthead(draw)
    # Vertical divider between the two columns.
    draw.line([(652, y), (652, 712)], fill=HAIRLINE, width=1)
    y_lead = draw_lead(draw, page, y)
    y_storm = draw_storm(draw, page, y)
    mid = max(y_lead, y_storm)
    if mid > 712:
        print("WARNING: columns end at %d, past the 712 budget" % mid,
              file=sys.stderr)
    rule(draw, 36, 724, W - 36, width=2)
    strip_top = 740
    draw_strip(draw, 36, 500, strip_top, "UKRAINE",
               "UN: 372 CIVILIANS KILLED IN OCTOBER",
               "The deadliest month of the year, the UN says, as "
               "strikes keep hitting towns and cities.",
               draw_spiral, SLATE)
    draw.line([(512, 740), (512, 950)], fill=HAIRLINE, width=1)
    draw_strip(draw, 536, 988, strip_top, "ST KITTS AND NEVIS",
               "ISLAND ENDS “GOLDEN PASSPORT” SALES",
               "The Caribbean state shuts its citizenship-by-"
               "investment scheme after years of scrutiny.",
               draw_passport, SLATE)
    draw_footer(draw)
    return page


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "")
    if len(sys.argv) > 1:
        out = sys.argv[1]
    elif outdir:
        out = os.path.join(outdir, "entry.png")
    else:
        out = os.path.join(HERE, "out", "entry.png")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    page = build()
    page.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    print("wrote %s (%d bytes, %dx%d)" % (out, size, W, H))
    if size > 1048576:
        print("ERROR: over the 1 MiB limit")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
