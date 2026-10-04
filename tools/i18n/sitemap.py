#!/usr/bin/env python3
"""Regenerate httpdocs/sitemap.xml from the pages' own canonical + hreflang tags,
and add the English pages to llms.txt.

Keeps lastmod/changefreq/priority from the existing sitemap; English pages
inherit them from their Turkish counterpart. Run after build.py.
"""
import os
import re
import sys
from datetime import date
from urllib.parse import unquote

sys.path.insert(0, os.path.dirname(__file__))
import pages  # noqa: E402
from build import EN2TR, ROOT, SITE, enc, file_for, norm  # noqa: E402

TODAY = date.today().isoformat()


def old_meta():
    xml = open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read()
    meta = {}
    for u in re.findall(r'<url>(.*?)</url>', xml, re.S):
        loc = unquote(re.search(r'<loc>(.*?)</loc>', u).group(1))[len(SITE):]
        meta[norm(loc)] = {k: (re.search(f'<{k}>(.*?)</{k}>', u) or [None, None])[1]
                           for k in ('lastmod', 'changefreq', 'priority')}
    return meta


def page_info(path):
    s = open(file_for(path), encoding='utf-8').read()
    head = s.split('</head>', 1)[0]
    if re.search(r'<meta\s+name="robots"\s+content="[^"]*noindex', head):
        return None
    alts = re.findall(r'<link rel="alternate" hreflang="([\w-]+)" href="([^"]+)"', head)
    title = re.search(r'<title>(.*?)</title>', head, re.S).group(1)
    return alts, title


def all_paths():
    out = []
    for root, _, files in os.walk(ROOT):
        if 'index.html' in files:
            rel = '/' + os.path.relpath(root, ROOT).replace(os.sep, '/') + '/'
            if rel not in ('/./', '/api/cron/'):
                out.append(rel)
    return out


def order_key(p):
    tr = EN2TR.get(p, p)
    group = 0 if tr == '/tr/' else 2 if tr.startswith('/blog/') else 1
    return group, tr != '/blog/', tr, p.startswith('/en/')


def sitemap():
    meta = old_meta()
    blocks = []
    for path in sorted(all_paths(), key=order_key):
        info = page_info(path)
        if not info:
            continue
        alts, _ = info
        m = meta.get(path) or meta.get(EN2TR.get(path, '')) or {}
        lines = [f'    <loc>{SITE}{enc(path)}</loc>']
        for lang, href in alts:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{lang}"{" " * (9 - len(lang))} href="{href}"/>')
        lines.append(f'    <lastmod>{m.get("lastmod") or TODAY}</lastmod>')
        lines.append(f'    <changefreq>{m.get("changefreq") or "monthly"}</changefreq>')
        lines.append(f'    <priority>{m.get("priority") or "0.7"}</priority>')
        blocks.append('  <url>\n' + '\n'.join(lines) + '\n  </url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n\n' + '\n\n'.join(blocks) + '\n\n</urlset>\n')
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8') as fh:
        fh.write(xml)
    return len(blocks)


def llms():
    for name in ('llms.txt', 'llms-full.txt'):
        f = os.path.join(ROOT, name)
        s = open(f, encoding='utf-8').read()
        for old, new in pages.REDIRECTS.items():
            s = s.replace(SITE + old, SITE + new)
        if name == 'llms.txt' and '## English Pages' not in s:
            def short(t):
                return re.sub(r' \| Edualist$', '', t)

            rows = []
            for tr, en, _, title, desc in pages.all_pairs():
                if en.startswith('/en/blog/') or en == '/en/blog/':
                    continue
                rows.append(f'- [{short(title)}]({SITE}{enc(en)})' + (f': {desc}' if desc else ''))
            posts = [f'- [{short(title)}]({SITE}{enc(en)}): {desc}'
                     for tr, en, _, title, desc in pages.all_pairs() if en.startswith('/en/blog/') and en != '/en/blog/']
            section = ('## English Pages\n\nEvery page below is the English version of a Turkish page '
                       '(linked with hreflang). Turkish pages live at the root; English pages under /en/.\n\n'
                       + '\n'.join(rows) + f'\n- [Blog (English)]({SITE}/en/blog/)\n\n'
                       '## English Blog Articles\n\n' + '\n'.join(posts) + '\n\n')
            s = s.replace('## Frequently Asked Questions', section + '## Frequently Asked Questions', 1)
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(s)


if __name__ == '__main__':
    n = sitemap()
    llms()
    print(f'sitemap: {n} urls')
