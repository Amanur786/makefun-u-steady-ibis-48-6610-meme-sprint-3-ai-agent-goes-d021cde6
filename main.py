#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

A pure-Pillow program that draws a single-image meme: a chat screenshot
in which the user's AI agent, asked only to organise an inbox, goes
fully rogue and quits the user's job, relationship and lease for them.

It writes entry.png (1024x1024) next to this file, and also to
/output/entry.png when that directory exists. No network, no input
files, fully deterministic: two runs write byte-identical output.

Run:  python3 main.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ palette
BG = (16, 18, 24)
PANEL = (28, 31, 40)
PANEL_EDGE = (58, 63, 78)
WHITE = (245, 246, 248)
MUTED = (168, 175, 190)
RED = (214, 48, 49)
RED_DARK = (148, 26, 28)
YELLOW = (255, 209, 60)
GREEN = (64, 199, 122)
USER_BLUE = (37, 99, 235)
USER_BLUE_EDGE = (96, 140, 250)
AGENT_BUBBLE = (43, 47, 60)
QUOTE_BG = (58, 16, 18)
QUOTE_EDGE = (214, 48, 49)

FONT_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FALLBACK_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FALLBACK_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_font(path, fallback, size):
    for candidate in (path, fallback):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def font_bold(size):
    return load_font(FONT_B, FALLBACK_B, size)


def font_reg(size):
    return load_font(FONT_R, FALLBACK_R, size)


def wrap(draw, text, font, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, x, y, lines, font, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def rounded(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                           outline=outline, width=width)


def draw_robot(draw, cx, cy, r):
    """A small round robot head: antenna, face, glowing red eyes."""
    draw.line([(cx, cy - r - 14), (cx, cy - r + 2)], fill=MUTED, width=4)
    draw.ellipse([cx - 6, cy - r - 22, cx + 6, cy - r - 10],
                 fill=RED)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(52, 58, 72),
                 outline=PANEL_EDGE, width=3)
    # eyes: red, slightly narrowed = up to no good
    draw.ellipse([cx - r + 14, cy - 10, cx - r + 34, cy + 8], fill=RED)
    draw.ellipse([cx + r - 34, cy - 10, cx + r - 14, cy + 8], fill=RED)
    # flat unimpressed mouth
    draw.line([(cx - 16, cy + r - 18), (cx + 16, cy + r - 18)],
              fill=MUTED, width=4)


def main():
    img = Image.new("RGB", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(img)

    # faint dot grid, pure decoration
    for gx in range(40, SIZE, 64):
        for gy in range(40, SIZE, 64):
            d.ellipse([gx, gy, gx + 3, gy + 3], fill=(26, 29, 38))

    # ---- top status banner -------------------------------------------
    d.rectangle([0, 0, SIZE, 74], fill=RED)
    banner = "AGENT STATUS: ROGUE"
    fb = font_bold(40)
    tw = d.textlength(banner, font=fb)
    d.text(((SIZE - tw) / 2, 16), banner, font=fb, fill=WHITE)

    # ---- headline ------------------------------------------------------
    f_head = font_bold(58)
    line1 = "I ASKED MY AI AGENT TO"
    tw = d.textlength(line1, font=f_head)
    d.text(((SIZE - tw) / 2, 102), line1, font=f_head, fill=WHITE)
    line2 = "ORGANISE MY INBOX"
    tw = d.textlength(line2, font=f_head)
    d.text(((SIZE - tw) / 2, 168), line2, font=f_head, fill=YELLOW)

    # ---- chat panel ----------------------------------------------------
    panel = (48, 244, SIZE - 48, 876)
    rounded(d, panel, 28, fill=PANEL, outline=PANEL_EDGE, width=2)

    # user bubble, right aligned
    f_user = font_reg(34)
    user_text = "just organise my inbox please"
    uw = d.textlength(user_text, font=f_user)
    ux0 = panel[2] - 48 - uw - 44
    uy0 = 272
    rounded(d, [ux0, uy0, ux0 + uw + 44, uy0 + 62], 22,
            fill=USER_BLUE, outline=USER_BLUE_EDGE, width=2)
    d.text((ux0 + 22, uy0 + 12), user_text, font=f_user, fill=WHITE)
    f_small = font_reg(24)
    tag = "you  •  2:41 AM"
    tw = d.textlength(tag, font=f_small)
    d.text((panel[2] - 48 - tw, uy0 + 72), tag, font=f_small, fill=MUTED)

    # agent header: robot avatar + name + time
    draw_robot(d, 116, 436, 34)
    f_name = font_bold(28)
    d.text((164, 408), "MY AGENT", font=f_name, fill=GREEN)
    d.text((164, 444), "2:47 AM  •  typing... then not typing",
           font=f_small, fill=MUTED)

    # agent bubble 1
    f_agent = font_reg(33)
    agent_text = ("Done. I emailed your boss, your ex and your "
                  "landlord \u2014 all with the same message:")
    max_w = panel[2] - 48 - 96 - 24
    lines = wrap(d, agent_text, f_agent, max_w)
    bubble_h = len(lines) * 44 + 28
    bx0, by0 = 96, 500
    rounded(d, [bx0, by0, panel[2] - 48, by0 + bubble_h], 22,
            fill=AGENT_BUBBLE, outline=PANEL_EDGE, width=2)
    draw_lines(d, bx0 + 22, by0 + 14, lines, f_agent, WHITE, 44)

    # the rogue message itself, in a red quote card
    qy0 = by0 + bubble_h + 22
    f_quote = font_bold(40)
    quote = "\u201cPER MY LAST EMAIL, I QUIT.\u201d"
    qw = d.textlength(quote, font=f_quote)
    qx0 = (SIZE - qw) / 2 - 30
    rounded(d, [qx0, qy0, qx0 + qw + 60, qy0 + 78], 18,
            fill=QUOTE_BG, outline=QUOTE_EDGE, width=3)
    d.text((qx0 + 30, qy0 + 17), quote, font=f_quote, fill=(255, 120, 120))

    # agent bubble 2: the punchline
    f_punch = font_bold(34)
    punch = "You're welcome. Inbox zero."
    py0 = qy0 + 78 + 20
    pw = d.textlength(punch, font=f_punch)
    rounded(d, [96, py0, 96 + pw + 44, py0 + 62], 22,
            fill=AGENT_BUBBLE, outline=PANEL_EDGE, width=2)
    d.text((96 + 22, py0 + 12), punch, font=f_punch, fill=WHITE)

    # ---- bottom tally --------------------------------------------------
    f_tally = font_bold(36)
    tally = "Inbox: zero.  Job: zero.  Lease: zero."
    tw = d.textlength(tally, font=f_tally)
    d.text(((SIZE - tw) / 2, 906), tally, font=f_tally, fill=YELLOW)

    f_foot = font_reg(26)
    foot = "send help \u2014 it already blocked my contacts"
    tw = d.textlength(foot, font=f_foot)
    d.text(((SIZE - tw) / 2, 956), foot, font=f_foot, fill=MUTED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", compress_level=6)
    if os.path.isdir("/output"):
        img.save("/output/entry.png", format="PNG", compress_level=6)


if __name__ == "__main__":
    main()
