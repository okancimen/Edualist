#!/usr/bin/env python3
"""Thumbnail for dubai-maaslar-insaat-mimarlik — Dubai construction & architecture."""
from PIL import Image, ImageDraw
import math

W, H = 800, 450
OUT = '/Users/okancimen/Documents/GitHub/new/Edualist/httpdocs/assets/blog'


def sky_gradient(draw, sky_h, top, bot):
    for y in range(sky_h):
        t = y / sky_h
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))


def make_insaat():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)

    sky_h = int(H * 0.72)

    # Warm golden Dubai sunset sky
    sky_gradient(d, sky_h, (22, 55, 115), (200, 145, 60))

    # Desert ground (sand)
    d.rectangle([0, sky_h, W, H], fill=(185, 148, 95))
    # Ground shadow strip
    d.rectangle([0, sky_h, W, sky_h + 18], fill=(160, 120, 70))

    # ── Dubai skyline silhouette ───────────────────────────────────────────────
    bld = (22, 38, 72)

    # Burj Khalifa (center, tallest) — tapered spire
    bk_cx = int(W * 0.52)
    bk_base = sky_h
    bk_top = int(H * 0.03)
    # Main taper
    d.polygon([
        (bk_cx - 28, bk_base),
        (bk_cx - 18, int(H * 0.42)),
        (bk_cx - 10, int(H * 0.22)),
        (bk_cx - 4,  int(H * 0.10)),
        (bk_cx,      bk_top),
        (bk_cx + 4,  int(H * 0.10)),
        (bk_cx + 10, int(H * 0.22)),
        (bk_cx + 18, int(H * 0.42)),
        (bk_cx + 28, bk_base),
    ], fill=bld)
    # Setbacks (wider base sections)
    d.rectangle([bk_cx - 42, int(H * 0.55), bk_cx + 42, bk_base], fill=bld)
    d.rectangle([bk_cx - 35, int(H * 0.44), bk_cx + 35, int(H * 0.56)], fill=bld)

    # Left cluster — wide commercial towers
    towers_left = [
        (int(W * 0.08), int(H * 0.38), 48, bk_base),
        (int(W * 0.16), int(H * 0.44), 38, bk_base),
        (int(W * 0.23), int(H * 0.33), 44, bk_base),
        (int(W * 0.30), int(H * 0.46), 36, bk_base),
        (int(W * 0.37), int(H * 0.40), 42, bk_base),
    ]
    for (tx, ty, tw, tb) in towers_left:
        d.rectangle([tx, ty, tx + tw, tb], fill=bld)
        # Flat top detail
        d.rectangle([tx - 2, ty - 4, tx + tw + 2, ty], fill=bld)

    # Right cluster
    towers_right = [
        (int(W * 0.63), int(H * 0.41), 42, bk_base),
        (int(W * 0.70), int(H * 0.35), 46, bk_base),
        (int(W * 0.77), int(H * 0.48), 38, bk_base),
        (int(W * 0.83), int(H * 0.43), 44, bk_base),
        (int(W * 0.90), int(H * 0.38), 48, bk_base),
    ]
    for (tx, ty, tw, tb) in towers_right:
        d.rectangle([tx, ty, tx + tw, tb], fill=bld)
        d.rectangle([tx - 2, ty - 4, tx + tw + 2, ty], fill=bld)

    # ── Construction crane (left of Burj Khalifa) ─────────────────────────────
    crane_c = (220, 100, 30)   # orange/amber crane
    mast_x = int(W * 0.30)
    mast_top = int(H * 0.06)
    mast_bot = sky_h

    # Mast (vertical tower)
    d.rectangle([mast_x - 5, mast_top, mast_x + 5, mast_bot], fill=crane_c)

    # Diagonal bracing on mast
    seg = (mast_bot - mast_top) // 7
    for i in range(7):
        y0 = mast_top + i * seg
        y1 = y0 + seg
        if i % 2 == 0:
            d.line([(mast_x - 5, y0), (mast_x + 5, y1)], fill=crane_c, width=2)
        else:
            d.line([(mast_x + 5, y0), (mast_x - 5, y1)], fill=crane_c, width=2)

    # Jib (long horizontal arm — extends right)
    jib_y = mast_top + 12
    jib_end = mast_x + 160
    d.rectangle([mast_x - 5, jib_y - 6, jib_end, jib_y + 6], fill=crane_c)

    # Counter-jib (shorter, left side)
    counter_end = mast_x - 60
    d.rectangle([counter_end, jib_y - 5, mast_x + 5, jib_y + 5], fill=crane_c)
    # Counterweight
    d.rectangle([counter_end, jib_y - 10, counter_end + 22, jib_y + 18], fill=(160, 70, 20))

    # Pendant cables from jib tip
    d.line([(mast_x + 5, mast_top + 2), (jib_end, jib_y - 6)], fill=crane_c, width=2)
    d.line([(mast_x + 5, mast_top + 2), (counter_end, jib_y - 6)], fill=crane_c, width=2)

    # Hook cable (hanging load line)
    hook_x = mast_x + 110
    hook_top = jib_y + 6
    hook_bot = int(H * 0.55)
    d.line([(hook_x, hook_top), (hook_x, hook_bot)], fill=(180, 80, 20), width=2)
    # Hook shape
    d.arc([hook_x - 8, hook_bot, hook_x + 8, hook_bot + 14], start=0, end=180, fill=(180, 80, 20), width=3)

    # ── Second crane (far right, smaller) ─────────────────────────────────────
    c2x = int(W * 0.88)
    c2top = int(H * 0.14)
    c2bot = sky_h
    d.rectangle([c2x - 4, c2top, c2x + 4, c2bot], fill=crane_c)
    # Jib left only (pointing left)
    c2jib_y = c2top + 10
    c2jib_end = c2x - 95
    d.rectangle([c2jib_end, c2jib_y - 5, c2x + 4, c2jib_y + 5], fill=crane_c)
    d.line([(c2x, c2top), (c2jib_end, c2jib_y - 5)], fill=crane_c, width=2)
    c2hook_x = c2x - 55
    d.line([(c2hook_x, c2jib_y + 5), (c2hook_x, int(H * 0.58))], fill=(180, 80, 20), width=2)

    # ── Blueprint grid overlay (bottom-left corner) ───────────────────────────
    bp_c = (0, 90, 180)
    # Blueprint rectangle
    bp_x, bp_y = 18, int(H * 0.78)
    bp_w, bp_h = 130, 65
    d.rectangle([bp_x, bp_y, bp_x + bp_w, bp_y + bp_h], fill=(0, 48, 110))
    # Grid lines
    step = 14
    for gx in range(bp_x, bp_x + bp_w, step):
        d.line([(gx, bp_y), (gx, bp_y + bp_h)], fill=(40, 120, 220), width=1)
    for gy in range(bp_y, bp_y + bp_h, step):
        d.line([(bp_x, gy), (bp_x + bp_w, gy)], fill=(40, 120, 220), width=1)
    # Simple floor plan outline on grid
    pl_c = (140, 210, 255)
    d.rectangle([bp_x + 10, bp_y + 12, bp_x + 65, bp_y + 52], outline=pl_c, width=2)
    d.rectangle([bp_x + 65, bp_y + 20, bp_x + 115, bp_y + 52], outline=pl_c, width=2)
    d.line([(bp_x + 10, bp_y + 32), (bp_x + 65, bp_y + 32)], fill=pl_c, width=2)

    # ── UAE flag (bottom-right) ────────────────────────────────────────────────
    fw, fh = 82, 55
    fx = W - fw - 18
    fy = H - fh - 18

    d.rectangle([fx - 2, fy - 2, fx + fw + 2, fy + fh + 2], fill=(255, 255, 255))

    # 3 horizontal stripes: green, white, black
    stripe_h = fh // 3
    d.rectangle([fx, fy,                  fx + fw, fy + stripe_h    ], fill=(0, 115, 60))
    d.rectangle([fx, fy + stripe_h,       fx + fw, fy + 2 * stripe_h], fill=(255, 255, 255))
    d.rectangle([fx, fy + 2 * stripe_h,   fx + fw, fy + fh          ], fill=(25, 25, 25))

    # Red vertical band on left (1/4 of flag width)
    red_w = fw // 4
    d.rectangle([fx, fy, fx + red_w, fy + fh], fill=(195, 30, 50))

    return img


img = make_insaat()
img.save(f'{OUT}/thumb-dubai-maaslar-insaat.webp', 'WEBP', quality=90)
print("Saved thumb-dubai-maaslar-insaat.webp")

img.resize((640, 360), Image.LANCZOS).save(f'{OUT}/thumb-dubai-maaslar-insaat-640.webp', 'WEBP', quality=88)
print("Saved thumb-dubai-maaslar-insaat-640.webp")

print("Done!")
