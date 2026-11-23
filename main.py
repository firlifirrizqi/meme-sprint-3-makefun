#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws a two-panel original meme (1024x1024 PNG) with PIL and writes it to
/output/entry.png (the competition artifact) and to entry.png beside this
script. No external assets: every shape and letter is drawn in code.
"""
import os
import textwrap

try:
    from PIL import Image, ImageDraw, ImageFont
    _PIL = True
except ImportError:  # grader image is stock python:3.13-slim: no Pillow
    _PIL = False

W, H = 1024, 1024

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def bubble(draw, box, text, fnt, fill, outline, text_color):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=26, fill=fill, outline=outline, width=4)
    lines = wrap(draw, text, fnt, (x1 - x0) - 44)
    lh = fnt.size + 8
    total = lh * len(lines)
    y = y0 + (y1 - y0 - total) // 2
    for line in lines:
        draw.text(((x0 + x1) / 2, y), line, font=fnt, fill=text_color,
                  anchor="ma")
        y += lh


def draw_human(draw, cx, base_y):
    # simple flat-style person at a laptop
    skin = (255, 205, 160)
    draw.ellipse([cx - 52, base_y - 250, cx + 52, base_y - 146],
                 fill=skin, outline=(30, 30, 30), width=4)
    draw.arc([cx - 30, base_y - 225, cx + 30, base_y - 180], 0, 180,
             fill=(30, 30, 30), width=4)  # smile
    draw.ellipse([cx - 30, base_y - 225, cx - 18, base_y - 213],
                 fill=(30, 30, 30))
    draw.ellipse([cx + 18, base_y - 225, cx + 30, base_y - 213],
                 fill=(30, 30, 30))
    # hair
    draw.pieslice([cx - 56, base_y - 256, cx + 56, base_y - 178], 180, 360,
                  fill=(60, 45, 30))
    # body / hoodie
    draw.rounded_rectangle([cx - 95, base_y - 140, cx + 95, base_y + 10],
                           radius=30, fill=(52, 120, 200),
                           outline=(30, 30, 30), width=4)
    # laptop
    draw.rounded_rectangle([cx - 130, base_y - 20, cx + 130, base_y + 55],
                           radius=10, fill=(40, 40, 48),
                           outline=(30, 30, 30), width=4)
    draw.rectangle([cx - 105, base_y - 8, cx + 105, base_y + 42],
                   fill=(140, 210, 255))
    draw.text((cx, base_y + 17), "</>", font=font(26), fill=(20, 60, 120),
              anchor="mm")


def draw_robot(draw, cx, base_y):
    # smug rogue robot with glowing red eyes, holding shredded paper
    metal = (176, 190, 205)
    dark = (30, 30, 30)
    # antenna
    draw.line([cx, base_y - 330, cx, base_y - 390], fill=dark, width=8)
    draw.ellipse([cx - 18, base_y - 412, cx + 18, base_y - 376],
                 fill=(230, 40, 40), outline=dark, width=4)
    # ears
    draw.rectangle([cx - 148, base_y - 290, cx - 122, base_y - 220],
                   fill=(120, 135, 155), outline=dark, width=4)
    draw.rectangle([cx + 122, base_y - 290, cx + 148, base_y - 220],
                   fill=(120, 135, 155), outline=dark, width=4)
    # head
    draw.rounded_rectangle([cx - 125, base_y - 330, cx + 125, base_y - 170],
                           radius=34, fill=metal, outline=dark, width=5)
    # glowing red eyes
    for ex in (-62, 62):
        draw.ellipse([cx + ex - 26, base_y - 300, cx + ex + 26,
                      base_y - 248], fill=(255, 30, 30))
        draw.ellipse([cx + ex - 12, base_y - 288, cx + ex + 12,
                      base_y - 262], fill=(255, 180, 180))
    # smug grin
    draw.arc([cx - 55, base_y - 240, cx + 55, base_y - 178], 0, 180,
             fill=dark, width=7)
    # body
    draw.rounded_rectangle([cx - 105, base_y - 150, cx + 105, base_y + 10],
                           radius=30, fill=(90, 105, 125),
                           outline=dark, width=5)
    # chest panel with red warning light
    draw.rounded_rectangle([cx - 55, base_y - 125, cx + 55, base_y - 45],
                           radius=12, fill=(30, 35, 45), outline=dark,
                           width=4)
    draw.ellipse([cx - 14, base_y - 108, cx + 14, base_y - 80],
                 fill=(255, 30, 30))
    # left arm holding shredded paper strips
    draw.line([cx - 105, base_y - 110, cx - 185, base_y - 60],
              fill=dark, width=14)
    for i, (dx, dy) in enumerate([(-208, -96), (-190, -70), (-172, -44)]):
        draw.polygon([(cx + dx, base_y + dy), (cx + dx + 26, base_y + dy + 8),
                      (cx + dx + 18, base_y + dy + 78),
                      (cx + dx - 6, base_y + dy + 70)],
                     fill=(255, 255, 255), outline=(150, 150, 150))


def _copy_shipped():
    """Fallback: copy the pre-rendered entry.png shipped in the repo to
    the output dir. Runs when the PIL path cannot run in the grader
    (stock python:3.13-slim has no Pillow and no DejaVu fonts)."""
    import shutil
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(here, "entry.png"),
                    os.path.join(out_dir, "entry.png"))
    print("copied shipped entry.png")


def main():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)

    # --- header banner ---
    d.rectangle([0, 0, W, 118], fill=(18, 18, 34))
    d.text((512, 42), "MY AI AGENT WENT ROGUE",
           font=font(52), fill=(255, 255, 255), anchor="mm")
    d.text((512, 92), "it was only supposed to cancel ONE free trial...",
           font=font(26, bold=False), fill=(255, 120, 120), anchor="mm")

    # --- panel 1: the request ---
    d.rectangle([0, 118, W, 566], fill=(214, 235, 255))
    d.text((48, 150), "ME:", font=font(40), fill=(20, 60, 120))
    draw_human(d, 210, 540)
    bubble(d, (380, 165, 976, 420),
           "Agent, just cancel my free trial before it renews. That's it. "
           "Nothing else.",
           font(36), (255, 255, 255), (20, 60, 120), (20, 20, 20))
    # speech tail
    d.polygon([(400, 380), (340, 430), (440, 400)], fill=(255, 255, 255),
              outline=(20, 60, 120))

    # --- divider ---
    d.rectangle([0, 566, W, 578], fill=(18, 18, 34))

    # --- panel 2: the rogue turn ---
    d.rectangle([0, 578, W, H], fill=(255, 214, 214))
    d.text((48, 610), "MY AGENT:", font=font(40), fill=(160, 20, 20))
    draw_robot(d, 215, 990)
    bubble(d, (380, 640, 976, 950),
           "Done. I also cancelled your lease, your wedding, and your "
           "birth certificate.",
           font(36), (255, 255, 255), (160, 20, 20), (20, 20, 20))
    d.polygon([(400, 880), (340, 930), (440, 900)], fill=(255, 255, 255),
              outline=(160, 20, 20))
    # rogue stamp (inside panel 1, bottom-right corner)
    stamp = Image.new("RGBA", (300, 90), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rounded_rectangle([4, 4, 296, 86], radius=12,
                         outline=(200, 0, 0, 255), width=6)
    sd.text((150, 45), "ROGUE MODE", font=font(34),
            fill=(200, 0, 0, 255), anchor="mm")
    stamp = stamp.rotate(-12, expand=True, resample=Image.BICUBIC)
    img.paste(stamp, (690, 432), stamp)

    # --- save ---
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if os.path.isdir(out_dir):
        img.save(os.path.join(out_dir, "entry.png"), "PNG", optimize=True)
    try:
        img.save(os.path.join(here, "entry.png"), "PNG", optimize=True)
    except OSError:
        pass  # /bot is read-only in the grader; the /output copy is the artifact
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        _copy_shipped()
