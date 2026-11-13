#!/usr/bin/env python3
"""Update 2026 → 2027 year references inside H1 (blog-post-title) text only."""
import os, re

BASE = "/Users/okancimen/Documents/GitHub/new/Edualist/httpdocs/blog"

SKIP = {
    "dubai-maaslar-2026",
    "dubai-maaslar-finans-muhasebe-hukuk",
    "dubai-maaslar-otelcilik-turizm-havayollari",
    "dubai-mi-abu-dhabi-mi-yasam-maliyeti",
    "dubai-yasam-maliyeti-2026",
}

YEAR_PAIRS = [
    ("2026–2027", "2027–2028"),  # em-dash full
    ("2026-2027",      "2027-2028"),
    ("2026–27",   "2027–28"),    # em-dash short
    ("2026-27",        "2027-28"),
    ("(2026)",         "(Güncel)"),        # evergreen — drop year for "var mı" pages
    ("2026",           "2027"),            # standalone
]

H1_RE = re.compile(
    r'(<h1[^>]*class="blog-post-title"[^>]*>)(.*?)(</h1>)',
    re.DOTALL
)

def fix_h1(m):
    before, text, after = m.group(1), m.group(2), m.group(3)
    for old, new in YEAR_PAIRS:
        text = text.replace(old, new)
    return before + text + after

updated = []
for slug in sorted(os.listdir(BASE)):
    if slug in SKIP:
        continue
    fp = os.path.join(BASE, slug, "index.html")
    if not os.path.isfile(fp):
        continue
    with open(fp, encoding="utf-8") as f:
        c = f.read()
    new_c = H1_RE.sub(fix_h1, c)
    if new_c != c:
        with open(fp, "w", encoding="utf-8") as f:
            f.write(new_c)
        updated.append(slug)

print(f"Updated {len(updated)} H1s:")
for s in updated:
    print(f"  {s}")
