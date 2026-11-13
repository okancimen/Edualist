#!/usr/bin/env python3
"""Thumbnail for dubai-maaslar-saglik — Dubai healthcare salaries."""
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


def make_saglik():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)

    sky_h = int(H * 0.72)

    # Warm Dubai twilight sky — deeper blue-purple tones for a medical/calm feel
    sky_gradient(d, sky_h, (18, 48, 105), (165, 115, 55))

    # Desert ground
    d.rectangle([0, sky_h, W, H], fill=(185, 148, 95))
    d.rectangle([0, sky_h, W, sky_h + 16], fill=(155, 118, 68))

    # ── Dubai skyline silhouette (background) ─────────────────────────────────
    bld = (18, 32, 65)

    # Burj Khalifa — slim tapered spire, right of centre
    bk_cx = int(W * 0.72)
    bk_base = sky_h
    bk_top = int(H * 0.04)
    d.polygon([
        (bk_cx - 24, bk_base),
        (bk_cx - 15, int(H * 0.42)),
        (bk_cx - 8,  int(H * 0.22)),
        (bk_cx - 3,  int(H * 0.10)),
        (bk_cx,      bk_top),
        (bk_cx + 3,  int(H * 0.10)),
        (bk_cx + 8,  int(H * 0.22)),
        (bk_cx + 15, int(H * 0.42)),
        (bk_cx + 24, bk_base),
    ], fill=bld)
    d.rectangle([bk_cx - 36, int(H * 0.55), bk_cx + 36, bk_base], fill=bld)
    d.rectangle([bk_cx - 28, int(H * 0.44), bk_cx + 28, int(H * 0.56)], fill=bld)

    # Background towers
    towers = [
        (int(W * 0.52), int(H * 0.40), 36, bk_base),
        (int(W * 0.60), int(H * 0.46), 30, bk_base),
        (int(W * 0.80), int(H * 0.38), 40, bk_base),
        (int(W * 0.87), int(H * 0.44), 32, bk_base),
        (int(W * 0.93), int(H * 0.40), 44, bk_base),
    ]
    for (tx, ty, tw, tb) in towers:
        d.rectangle([tx, ty, tx + tw, tb], fill=bld)
        d.rectangle([tx - 2, ty - 4, tx + tw + 2, ty], fill=bld)

    # ── Hospital building (foreground, left-centre) ───────────────────────────
    hosp_c = (35, 60, 110)       # dark navy-blue hospital
    hosp_x  = int(W * 0.08)
    hosp_y  = int(H * 0.34)
    hosp_w  = int(W * 0.30)
    hosp_h2 = sky_h - hosp_y

    # Main building body
    d.rectangle([hosp_x, hosp_y, hosp_x + hosp_w, sky_h], fill=hosp_c)

    # Entrance portico (slightly wider, lower section)
    por_w = int(hosp_w * 0.42)
    por_x = hosp_x + (hosp_w - por_w) // 2
    d.rectangle([por_x, int(H * 0.55), por_x + por_w, sky_h], fill=(28, 50, 95))

    # Windows (small lit rectangles)
    win_c = (200, 220, 255)
    for row in range(3):
        wy = hosp_y + 18 + row * 28
        for col in range(5):
            wx = hosp_x + 14 + col * (hosp_w - 28) // 4
            d.rectangle([wx, wy, wx + 16, wy + 14], fill=win_c)

    # Entrance doors
    d.rectangle([por_x + 12, int(H * 0.62), por_x + 28, sky_h], fill=(150, 190, 240))
    d.rectangle([por_x + por_w - 28, int(H * 0.62), por_x + por_w - 12, sky_h], fill=(150, 190, 240))

    # ── Large medical cross on hospital facade ────────────────────────────────
    cross_cx = hosp_x + hosp_w // 2
    cross_cy = int(H * 0.26)
    cross_r  = 32   # half arm-length
    cross_t  = 12   # arm thickness half

    # White glow halo behind cross
    halo_r = cross_r + 10
    d.ellipse([cross_cx - halo_r, cross_cy - halo_r, cross_cx + halo_r, cross_cy + halo_r],
              fill=(255, 255, 255, 180) if hasattr(d, 'ellipse_rgba') else (230, 240, 255))

    # Red medical cross
    cross_red = (210, 32, 42)
    # Horizontal bar
    d.rectangle([cross_cx - cross_r, cross_cy - cross_t,
                 cross_cx + cross_r, cross_cy + cross_t], fill=cross_red)
    # Vertical bar
    d.rectangle([cross_cx - cross_t, cross_cy - cross_r,
                 cross_cx + cross_t, cross_cy + cross_r], fill=cross_red)

    # White border on cross for visibility
    brd = 3
    for rect, fill in [
        ([cross_cx - cross_r - brd, cross_cy - cross_t - brd,
          cross_cx + cross_r + brd, cross_cy + cross_t + brd], (255, 255, 255)),
        ([cross_cx - cross_r, cross_cy - cross_t,
          cross_cx + cross_r, cross_cy + cross_t], cross_red),
        ([cross_cx - cross_t - brd, cross_cy - cross_r - brd,
          cross_cx + cross_t + brd, cross_cy + cross_r + brd], (255, 255, 255)),
        ([cross_cx - cross_t, cross_cy - cross_r,
          cross_cx + cross_t, cross_cy + cross_r], cross_red),
    ]:
        d.rectangle(rect, fill=fill)

    # ── Stethoscope element (bottom-left corner) ──────────────────────────────
    # Simplified: arc for the tubing + two earpieces + diaphragm circle
    steth_c = (50, 160, 190)   # medical teal
    # Main arc of tubing
    arc_cx = int(W * 0.08)
    arc_cy = int(H * 0.84)
    arc_r  = 48
    # Draw arc as polygon approximation
    arc_pts = []
    for ang in range(0, 200, 8):
        rad = math.radians(ang)
        arc_pts.append((arc_cx + int(arc_r * math.cos(rad)),
                        arc_cy + int(arc_r * math.sin(rad))))
    if len(arc_pts) > 1:
        for i in range(len(arc_pts) - 1):
            d.line([arc_pts[i], arc_pts[i+1]], fill=steth_c, width=5)

    # Diaphragm (chest piece) — circle at arc end
    diap_x = arc_cx + arc_r + 2
    diap_y = arc_cy - 6
    d.ellipse([diap_x - 14, diap_y - 14, diap_x + 14, diap_y + 14],
              fill=steth_c)
    d.ellipse([diap_x - 8, diap_y - 8, diap_x + 8, diap_y + 8],
              fill=(220, 240, 255))

    # ── UAE flag (bottom-right) ────────────────────────────────────────────────
    fw, fh = 82, 55
    fx = W - fw - 18
    fy = H - fh - 18

    d.rectangle([fx - 2, fy - 2, fx + fw + 2, fy + fh + 2], fill=(255, 255, 255))

    stripe_h = fh // 3
    d.rectangle([fx, fy,                  fx + fw, fy + stripe_h    ], fill=(0, 115, 60))
    d.rectangle([fx, fy + stripe_h,       fx + fw, fy + 2 * stripe_h], fill=(255, 255, 255))
    d.rectangle([fx, fy + 2 * stripe_h,   fx + fw, fy + fh          ], fill=(25, 25, 25))

    red_w = fw // 4
    d.rectangle([fx, fy, fx + red_w, fy + fh], fill=(195, 30, 50))

    return img


img = make_saglik()
img.save(f'{OUT}/thumb-dubai-maaslar-saglik.webp', 'WEBP', quality=90)
print("Saved thumb-dubai-maaslar-saglik.webp")

img.resize((640, 360), Image.LANCZOS).save(f'{OUT}/thumb-dubai-maaslar-saglik-640.webp', 'WEBP', quality=88)
print("Saved thumb-dubai-maaslar-saglik-640.webp")

print("Done!")
