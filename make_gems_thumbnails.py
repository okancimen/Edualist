#!/usr/bin/env python3
"""
Regenerate GEMS school thumbnails replacing the GEMS Education group logo
with each school's individual white logo on a dark rounded card.
"""
from PIL import Image, ImageDraw
import os

ASSETS = "/Users/okancimen/Documents/GitHub/new/Edualist/httpdocs/assets/blog"
LOGOS  = f"{ASSETS}/logos"

# White logo box coords in existing thumbnails (from pixel analysis)
BOX = (45, 89, 272, 316)   # x1, y1, x2, y2

# Dark card color (slightly lighter than background for subtle separation)
CARD_COLOR  = (18, 52, 85, 220)   # RGBA dark blue, semi-transparent
BG_COLOR    = (11, 33, 58)         # Primary navy to erase white box

PADDING = 10   # padding inside card

JOBS = [
    {
        "thumb_in":  f"{ASSETS}/thumb-gems-wellington-dubai-incelemesi.webp",
        "thumb_out": f"{ASSETS}/thumb-gems-wellington-dubai-incelemesi.webp",
        "logo":      f"{LOGOS}/gems-wellington-logo.png",
    },
    {
        "thumb_in":  f"{ASSETS}/thumb-gems-founders-school-dubai-incelemesi.webp",
        "thumb_out": f"{ASSETS}/thumb-gems-founders-school-dubai-incelemesi.webp",
        "logo":      f"{LOGOS}/gems-founders-logo.png",
    },
    {
        "thumb_in":  f"{ASSETS}/thumb-gems-jumeirah-primary-school-dubai-incelemesi.webp",
        "thumb_out": f"{ASSETS}/thumb-gems-jumeirah-primary-school-dubai-incelemesi.webp",
        "logo":      f"{LOGOS}/gems-jumeirah-primary-logo.png",
    },
    {
        "thumb_in":  f"{ASSETS}/thumb-gems-dubai-american-academy-incelemesi.webp",
        "thumb_out": f"{ASSETS}/thumb-gems-dubai-american-academy-incelemesi.webp",
        "logo":      f"{LOGOS}/gems-dubai-american-academy-logo.png",
    },
]

def rounded_rect_mask(size, radius):
    """Return an RGBA image (white = opaque card area)."""
    w, h = size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (w-1, h-1)], radius=radius, fill=255)
    return mask

def fit_logo(logo_rgba, max_w, max_h):
    """Scale logo to fit within max_w × max_h preserving aspect ratio."""
    lw, lh = logo_rgba.size
    scale = min(max_w / lw, max_h / lh)
    new_w, new_h = int(lw * scale), int(lh * scale)
    return logo_rgba.resize((new_w, new_h), Image.LANCZOS)

for job in JOBS:
    base = Image.open(job["thumb_in"]).convert("RGBA")
    logo = Image.open(job["logo"]).convert("RGBA")

    x1, y1, x2, y2 = BOX
    box_w, box_h = x2 - x1, y2 - y1

    # --- 1. Erase the white box (fill with BG color) ---
    draw = ImageDraw.Draw(base)
    draw.rectangle(BOX, fill=(*BG_COLOR, 255))

    # --- 2. Draw dark rounded card ---
    card_img  = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_img)
    card_draw.rounded_rectangle(
        [(0, 0), (box_w - 1, box_h - 1)],
        radius=18,
        fill=CARD_COLOR
    )
    base.alpha_composite(card_img, dest=(x1, y1))

    # --- 3. Scale and center the white logo inside the card ---
    logo_fitted = fit_logo(logo, box_w - PADDING * 2, box_h - PADDING * 2)
    lw, lh = logo_fitted.size
    lx = x1 + (box_w - lw) // 2
    ly = y1 + (box_h - lh) // 2
    base.alpha_composite(logo_fitted, dest=(lx, ly))

    # --- 4. Save as WebP ---
    out = base.convert("RGB")
    out.save(job["thumb_out"], "WEBP", quality=88)
    print(f"Saved: {os.path.basename(job['thumb_out'])}")

    # Also update the -640 variant (scale to 640 wide)
    thumb_640 = job["thumb_out"].replace(".webp", "-640.webp")
    w640 = out.resize((640, 360), Image.LANCZOS)
    w640.save(thumb_640, "WEBP", quality=85)
    print(f"Saved: {os.path.basename(thumb_640)}")
