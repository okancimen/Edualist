#!/usr/bin/env python3
from PIL import Image, ImageDraw
import math

W, H = 800, 450


def sky_gradient(draw, sky_h, top, bot):
    for y in range(sky_h):
        t = y / sky_h
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))


def make_isvicre():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)

    sky_h = int(H * 0.62)

    # Sky: deep navy blue → light sky blue
    sky_gradient(d, sky_h, (28, 62, 130), (148, 208, 242))

    # Snow ground
    d.rectangle([0, sky_h, W, H], fill=(232, 241, 250))

    # Background ridge (faded, to simulate distance)
    d.polygon([
        (0, sky_h), (0, int(H * 0.40)),
        (int(W * 0.08), int(H * 0.22)), (int(W * 0.15), int(H * 0.33)),
        (int(W * 0.24), int(H * 0.21)), (int(W * 0.36), int(H * 0.31)),
        (int(W * 0.42), int(H * 0.39)), (int(W * 0.58), int(H * 0.39)),
        (int(W * 0.64), int(H * 0.31)), (int(W * 0.76), int(H * 0.21)),
        (int(W * 0.85), int(H * 0.33)), (int(W * 0.92), int(H * 0.22)),
        (W, int(H * 0.40)), (W, sky_h)
    ], fill=(185, 206, 228))

    # Matterhorn (iconic asymmetric peak, slightly right of center)
    # Left face brighter, right face in shadow
    mh_px = int(W * 0.49)
    mh_py = int(H * 0.04)

    # Full Matterhorn shape (light face = left/north)
    d.polygon([
        (mh_px, mh_py),
        (int(W * 0.41), int(H * 0.33)),
        (int(W * 0.30), sky_h),
        (int(W * 0.72), sky_h),
        (int(W * 0.67), int(H * 0.30)),
        (int(W * 0.60), int(H * 0.25)),
    ], fill=(215, 226, 240))

    # Shadow face (right/south face — darker)
    d.polygon([
        (mh_px, mh_py),
        (int(W * 0.60), int(H * 0.25)),
        (int(W * 0.67), int(H * 0.30)),
        (int(W * 0.72), sky_h),
        (int(W * 0.55), sky_h),
        (int(W * 0.52), int(H * 0.22)),
    ], fill=(162, 180, 205))

    # Left foreground peak
    d.polygon([
        (0, sky_h), (0, int(H * 0.46)),
        (int(W * 0.10), int(H * 0.18)),
        (int(W * 0.22), int(H * 0.38)),
        (int(W * 0.30), sky_h)
    ], fill=(205, 218, 235))

    # Right foreground peak
    d.polygon([
        (int(W * 0.70), sky_h),
        (int(W * 0.78), int(H * 0.30)),
        (int(W * 0.88), int(H * 0.17)),
        (W, int(H * 0.46)),
        (W, sky_h)
    ], fill=(205, 218, 235))

    # Pine trees
    tree_c = (32, 80, 48)
    for i, tx in enumerate(range(-5, W + 5, 27)):
        th = 38 - (i % 3) * 6
        ty = int(H * 0.73)
        d.polygon([(tx + 13, ty - th), (tx, ty), (tx + 26, ty)], fill=tree_c)

    # Swiss cross emblem floating in sky
    ex, ey = int(W * 0.50), int(H * 0.14)
    er = 24
    d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(205, 28, 40))
    ca, cl = 6, 16
    d.rectangle([ex - cl, ey - ca, ex + cl, ey + ca], fill=(255, 255, 255))
    d.rectangle([ex - ca, ey - cl, ex + ca, ey + cl], fill=(255, 255, 255))

    # Swiss flag (bottom-right) — Swiss flag is square
    fs = 52
    fx2, fy2 = W - fs - 18, H - fs - 18
    d.rectangle([fx2 - 2, fy2 - 2, fx2 + fs + 2, fy2 + fs + 2], fill=(255, 255, 255))
    d.rectangle([fx2, fy2, fx2 + fs, fy2 + fs], fill=(210, 28, 40))
    fw5 = fs // 5
    fl = int(fs * 0.6)
    cx2, cy2 = fx2 + fs // 2, fy2 + fs // 2
    d.rectangle([cx2 - fl // 2, cy2 - fw5 // 2, cx2 + fl // 2, cy2 + fw5 // 2], fill=(255, 255, 255))
    d.rectangle([cx2 - fw5 // 2, cy2 - fl // 2, cx2 + fw5 // 2, cy2 + fl // 2], fill=(255, 255, 255))

    return img


def make_abd():
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)

    sky_h = int(H * 0.65)

    # Sky: dark navy → light blue
    sky_gradient(d, sky_h, (28, 58, 128), (132, 200, 240))

    # Ground: dark green grass
    d.rectangle([0, sky_h, W, H], fill=(32, 85, 55))

    # Water strip (harbor around Statue of Liberty)
    water_y = int(H * 0.80)
    d.rectangle([int(W * 0.05), water_y, int(W * 0.95), H], fill=(38, 95, 148))

    # NYC skyline silhouette (right side)
    bld_c = (28, 48, 88)
    buildings = [
        (0.54, 0.48, 0.022),
        (0.57, 0.41, 0.028),
        (0.60, 0.44, 0.020),
        (0.63, 0.35, 0.016),  # Empire State
        (0.65, 0.43, 0.025),
        (0.69, 0.40, 0.022),
        (0.72, 0.50, 0.030),
        (0.76, 0.43, 0.025),
        (0.80, 0.51, 0.034),
        (0.85, 0.45, 0.022),
        (0.89, 0.47, 0.030),
        (0.93, 0.41, 0.070),
    ]
    for (xf, yf, wf) in buildings:
        bx = int(W * xf)
        by = int(H * yf)
        bw = int(W * wf)
        d.rectangle([bx, by, bx + bw, sky_h], fill=bld_c)

    # Statue of Liberty
    lib_cx = int(W * 0.34)
    lib_base = sky_h - 2
    sil_c = (28, 50, 95)

    # Island base
    d.ellipse([lib_cx - 55, lib_base - 14, lib_cx + 55, lib_base + 8], fill=sil_c)

    # Stepped pedestal
    d.rectangle([lib_cx - 28, lib_base - 58, lib_cx + 28, lib_base - 12], fill=sil_c)
    d.rectangle([lib_cx - 22, lib_base - 78, lib_cx + 22, lib_base - 56], fill=sil_c)

    # Body (tapered robe)
    body_top = lib_base - 155
    d.polygon([
        (lib_cx - 18, lib_base - 78),
        (lib_cx - 11, body_top),
        (lib_cx + 11, body_top),
        (lib_cx + 18, lib_base - 78),
    ], fill=sil_c)

    # Right arm raised holding torch
    arm_bx = lib_cx + 8
    arm_by = body_top + 22
    arm_tx = lib_cx + 40
    arm_ty = body_top - 38
    d.polygon([
        (arm_bx, arm_by),
        (arm_bx + 7, arm_by + 8),
        (arm_tx + 8, arm_ty + 8),
        (arm_tx, arm_ty),
    ], fill=sil_c)

    # Torch handle
    tx = arm_tx + 3
    ty = arm_ty
    d.rectangle([tx - 4, ty - 22, tx + 4, ty], fill=sil_c)
    # Flame
    d.polygon([
        (tx, ty - 32),
        (tx - 7, ty - 22),
        (tx + 7, ty - 22),
    ], fill=(255, 160, 30))

    # Head
    hcx, hcy = lib_cx, body_top - 14
    hr = 12
    d.ellipse([hcx - hr, hcy - hr, hcx + hr, hcy + hr], fill=sil_c)

    # Crown — 7 spike rays
    for ang in range(-54, 60, 18):
        rad = math.radians(ang - 90)
        sx = hcx + int(hr * math.cos(rad))
        sy = hcy + int(hr * math.sin(rad))
        ex2 = hcx + int((hr + 14) * math.cos(rad))
        ey2 = hcy + int((hr + 14) * math.sin(rad))
        px = int(3 * math.cos(rad + math.pi / 2))
        py = int(3 * math.sin(rad + math.pi / 2))
        d.polygon([(sx - px, sy - py), (ex2, ey2), (sx + px, sy + py)], fill=sil_c)

    # US Flag (bottom-right)
    fw, fh = 82, 55
    fx = W - fw - 18
    fy = H - fh - 18

    # White border
    d.rectangle([fx - 2, fy - 2, fx + fw + 2, fy + fh + 2], fill=(255, 255, 255))

    # 13 stripes
    sh = fh // 13
    for i in range(13):
        sc = (210, 30, 40) if i % 2 == 0 else (255, 255, 255)
        d.rectangle([fx, fy + i * sh, fx + fw, fy + (i + 1) * sh], fill=sc)

    # Blue canton
    cw = int(fw * 0.42)
    ch = sh * 7
    d.rectangle([fx, fy, fx + cw, fy + ch], fill=(38, 55, 130))

    # Stars (simplified dots on canton)
    star_c = (255, 255, 255)
    for row in range(9):
        n = 6 if row % 2 == 0 else 5
        x_off = 0 if row % 2 == 0 else int((cw - 8) / 10)
        for col in range(n):
            sx2 = fx + 4 + x_off + int(col * (cw - 8) / 5)
            sy2 = fy + 3 + int(row * (ch - 6) / 8)
            d.ellipse([sx2 - 2, sy2 - 2, sx2 + 2, sy2 + 2], fill=star_c)

    return img


out = '/Users/okancimen/Documents/GitHub/new/Edualist/httpdocs/assets/blog'

isvicre = make_isvicre()
isvicre.save(f'{out}/thumb-isvicre.webp', 'WEBP', quality=90)
print("Saved thumb-isvicre.webp")

abd = make_abd()
abd.save(f'{out}/thumb-abd.webp', 'WEBP', quality=90)
print("Saved thumb-abd.webp")

isvicre.resize((640, 360), Image.LANCZOS).save(f'{out}/thumb-isvicre-640.webp', 'WEBP', quality=88)
print("Saved thumb-isvicre-640.webp")

abd.resize((640, 360), Image.LANCZOS).save(f'{out}/thumb-abd-640.webp', 'WEBP', quality=88)
print("Saved thumb-abd-640.webp")

print("Done!")
