#!/usr/bin/env python3
"""Fix meta descriptions over 155 chars and add hero image preload."""
import re

FIXES = [
    {
        'file': '/Users/okancimen/Edualist/httpdocs/index.html',
        'old_desc': 'Yurt dışı okul seçimi, uluslararası eğitim danışmanlığı ve öğrenci koçluğu. Türk aileler için okul kaydı, müfredat seçimi, TCK rehberi ve relocation desteği. Özlem Çimen – 20+ yıl deneyim.',
        'new_desc': 'Türk aileler için yurt dışı okul seçimi ve uluslararası eğitim danışmanlığı. Özlem Çimen — Dubai bazlı eğitimci, 5 ülkede expatriyat anne, 20+ yıl deneyim.',
        'old_twitter_desc': None,
        'new_twitter_desc': None,
    },
    {
        'file': '/Users/okancimen/Edualist/httpdocs/en/index.html',
        'old_desc': 'Edualist helps families navigate international school admissions in Dubai and abroad. Expert guidance by Özlem Çimen — 20+ years in education, expat parent across 5 countries.',
        'new_desc': 'International school consulting for Turkish families in Dubai & abroad. Expert guidance by Özlem Çimen — 20+ years in education, expat mother of two.',
        'old_twitter_desc': None,
        'new_twitter_desc': None,
    },
]

for fix in FIXES:
    path = fix['file']
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    old = fix['old_desc']
    new = fix['new_desc']

    if old in html:
        html = html.replace(old, new, 1)
        print(f"OK meta desc: {path.split('httpdocs/')[-1]} ({len(old)}→{len(new)} chars)")
    else:
        print(f"NOT FOUND: {path.split('httpdocs/')[-1]}")
        continue

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

# Also fix twitter:description on root (reuse og:description which is fine)
# Check current length of all blog post meta descriptions
import os
BASE = '/Users/okancimen/Edualist/httpdocs/blog'
long = []
for slug in os.listdir(BASE):
    fpath = os.path.join(BASE, slug, 'index.html')
    if not os.path.isfile(fpath):
        continue
    with open(fpath) as f:
        content = f.read()
    m = re.search(r'name="description" content="([^"]+)"', content)
    if m:
        desc = m.group(1)
        if len(desc) > 160:
            long.append((slug, len(desc), desc[:80] + '...'))

if long:
    print(f"\nBlog posts with long meta description (>{160}):")
    for slug, length, preview in long:
        print(f"  {slug}: {length} chars — {preview}")
else:
    print("\nAll blog post meta descriptions are within limit.")
