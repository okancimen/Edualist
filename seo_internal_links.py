#!/usr/bin/env python3
"""Add contextual internal links to blog post body content.

Strategy:
- Protect <script>, <style>, existing <a> tags from modification
- Link first occurrence of key terms within blog post body
- Never link a post to itself
"""
import os, re

BASE = '/Users/okancimen/Edualist/httpdocs/blog'

# (term_pattern, link_href, link_title) — href relative from any blog post
# TR terms
TR_LINKS = [
    (r'IB program[ıi]', '../ib-alevel-amerikan-mufredat-karsilastirma/', 'IB, A-Level ve AP müfredat karşılaştırması'),
    (r'IB müfredat[ıi]', '../ib-alevel-amerikan-mufredat-karsilastirma/', 'IB, A-Level ve AP müfredat karşılaştırması'),
    (r'Uluslararası Bakalorya', '../ib-alevel-amerikan-mufredat-karsilastirma/', 'IB, A-Level ve AP müfredat karşılaştırması'),
    (r'KHDA derecelend', '../dubai-en-iyi-uluslararasi-okullar/', "Dubai'nin en iyi uluslararası okulları"),
    (r'üçüncü kültür çocuğu', '../ucuncu-kultur-cocugu-tck-rehberi/', 'Üçüncü Kültür Çocuğu (TCK) rehberi'),
    (r'\bTCK\b', '../ucuncu-kultur-cocugu-tck-rehberi/', 'Üçüncü Kültür Çocuğu (TCK) rehberi'),
    (r'EAL desteğ', '../oglumun-ingilizcesi-iyiydi/', 'Akademik İngilizce ve EAL desteği'),
    (r'EAL program', '../oglumun-ingilizcesi-iyiydi/', 'Akademik İngilizce ve EAL desteği'),
    (r'okul mülakatı', '../uluslararasi-okul-mulakatı-nasil-gecilir/', 'Uluslararası okul mülakatı hazırlık rehberi'),
    (r'mülakat hazırlığ', '../uluslararasi-okul-mulakatı-nasil-gecilir/', 'Uluslararası okul mülakatı hazırlık rehberi'),
    (r'yaşam maliyeti', '../yurtdisi-egitim-maliyet-karsilastirma/', 'Yurt dışı eğitim maliyet karşılaştırması'),
    (r'lise dönemindeki? (uyum|adaptasyon|geçiş)', '../lise-yurt-disi-tasinma-adaptasyon/', 'Lise döneminde yurt dışına taşınma'),
]

# EN terms
EN_LINKS = [
    (r'IB programme', '../ib-alevel-amerikan-mufredat-karsilastirma/', 'IB, A-Level and AP curriculum comparison'),
    (r'International Baccalaureate', '../ib-alevel-amerikan-mufredat-karsilastirma/', 'IB, A-Level and AP curriculum comparison'),
    (r'KHDA rating', '../dubai-en-iyi-uluslararasi-okullar/', "Dubai's best international schools"),
    (r'Third Culture Kid', '../ucuncu-kultur-cocugu-tck-rehberi/', 'Third Culture Kid (TCK) guide'),
    (r'\bTCK\b', '../ucuncu-kultur-cocugu-tck-rehberi/', 'Third Culture Kid (TCK) guide'),
    (r'EAL support', '../oglumun-ingilizcesi-iyiydi/', 'Academic English and EAL support'),
    (r'EAL programme', '../oglumun-ingilizcesi-iyiydi/', 'Academic English and EAL support'),
    (r'school interview', '../uluslararasi-okul-mulakatı-nasil-gecilir/', 'International school interview preparation'),
    (r'cost of living', '../yurtdisi-egitim-maliyet-karsilastirma/', 'International education cost comparison'),
]

def protect_blocks(html):
    """Replace protected regions with placeholders."""
    blocks = []
    def save(m):
        idx = len(blocks)
        blocks.append(m.group(0))
        return f'\x00BLOCK{idx:04d}\x00'
    # Order matters: scripts first (they can contain <a>), then anchors
    html = re.sub(r'<script[\s\S]*?</script>', save, html, flags=re.I)
    html = re.sub(r'<style[\s\S]*?</style>', save, html, flags=re.I)
    html = re.sub(r'<a[\s\S]*?</a>', save, html, flags=re.I)
    return html, blocks

def restore_blocks(html, blocks):
    for idx, block in enumerate(blocks):
        html = html.replace(f'\x00BLOCK{idx:04d}\x00', block)
    return html

def apply_links(html, link_rules, slug):
    html, blocks = protect_blocks(html)
    added = []
    for pattern, href, title in link_rules:
        # Skip if this link points to the current post
        target_slug = href.strip('./')
        if target_slug in slug:
            continue
        compiled = re.compile(f'({pattern})', re.IGNORECASE)
        # Only replace first occurrence
        new_html, n = compiled.subn(
            lambda m: f'<a href="{href}" title="{title}">{m.group(1)}</a>',
            html, count=1
        )
        if n:
            html = new_html
            added.append(pattern)
    html = restore_blocks(html, blocks)
    return html, added

ok = 0
for slug in sorted(os.listdir(BASE)):
    path = os.path.join(BASE, slug, 'index.html')
    if not os.path.isfile(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Apply TR and EN link rules
    html, tr_added = apply_links(html, TR_LINKS, slug)
    html, en_added = apply_links(html, EN_LINKS, slug)
    all_added = tr_added + en_added

    if all_added:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"OK {slug}: +{len(all_added)} links ({', '.join(all_added[:3])}{'...' if len(all_added)>3 else ''})")
        ok += 1
    else:
        print(f"-- {slug}: no new links")

print(f"\nDone — {ok} posts updated")
