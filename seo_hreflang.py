#!/usr/bin/env python3
"""Add hreflang tags to all blog posts and blog/index.html."""
import os, re

BASE = '/Users/okancimen/Edualist/httpdocs/blog'

def get_canonical(html):
    m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    return m.group(1) if m else None

def build_hreflang(url):
    return (
        f'  <link rel="alternate" hreflang="tr" href="{url}">\n'
        f'  <link rel="alternate" hreflang="en" href="{url}">\n'
        f'  <link rel="alternate" hreflang="x-default" href="{url}">'
    )

def process(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    if 'hreflang' in html:
        return 'SKIP'

    canonical = get_canonical(html)
    if not canonical:
        return 'NO_CANONICAL'

    tags = build_hreflang(canonical)
    # Insert right after canonical tag line
    html = re.sub(
        r'(<link rel="canonical"[^>]+>)',
        r'\1\n' + tags,
        html, count=1
    )
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return 'OK'

# Blog/index.html
result = process(os.path.join(BASE, 'index.html'))
print(f"blog/index.html — {result}")

# All 21 blog posts
for slug in sorted(os.listdir(BASE)):
    path = os.path.join(BASE, slug, 'index.html')
    if not os.path.isfile(path):
        continue
    result = process(path)
    print(f"{slug} — {result}")
