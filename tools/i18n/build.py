#!/usr/bin/env python3
"""One-off migration: split the bilingual (JS-toggled) pages into separate
Turkish and English pages.

  * Turkish pages are rewritten in place (same URLs).
  * English pages are written under httpdocs/en/ using the slugs in pages.py.

Run from the repo root:  python3 tools/i18n/build.py
The sources must still be the bilingual pages, so run it once on a clean tree.
"""
import html as htmllib
import json
import os
import re
import sys
from urllib.parse import quote, unquote, urljoin, urlsplit

sys.path.insert(0, os.path.dirname(__file__))
from langsplit import TAG_RE, _classes, _end_of, split  # noqa: E402
import pages  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'httpdocs')
SITE = pages.SITE

TR_MONTHS = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz',
             'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
EN_MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
             'August', 'September', 'October', 'November', 'December']
TR_CHARS = set('çğışöüÇĞİŞÖÜ')

SWITCH_SNIPPET = """<script>
  window.setLang = function (l) {
    if (l === document.documentElement.lang) return;
    try { localStorage.setItem('edualist_lang', l); } catch (e) {}
    var alt = document.querySelector('link[rel="alternate"][hreflang="' + l + '"]');
    location.href = alt ? new URL(alt.getAttribute('href'), location.href).pathname : '/' + l + '/';
  };
  document.querySelectorAll('.lang-btn').forEach(function (b) {
    var l = b.getAttribute('data-lang') || (b.id === 'langEN' ? 'en' : b.id === 'langTR' ? 'tr' : '');
    b.classList.toggle('active', l === document.documentElement.lang);
    if (b.hasAttribute('data-lang')) b.addEventListener('click', function () { setLang(l); });
  });
</script>
"""


# ── paths ───────────────────────────────────────────────────────────────────

def norm(path):
    """Canonical form of a site path: decoded, trailing slash, no index.html."""
    path = unquote(path)
    if path.endswith('index.html'):
        path = path[:-len('index.html')]
    if not path.endswith('/') and '.' not in path.rsplit('/', 1)[-1]:
        path += '/'
    return path


def file_for(path):
    return os.path.join(ROOT, norm(path).lstrip('/'), 'index.html')


def enc(path):
    return quote(path, safe='/%#?=&')


PAIRS = list(pages.all_pairs())
TR2EN = {norm(tr): en for tr, en, *_ in PAIRS if tr}
EN2TR = {en: norm(tr) for tr, en, *_ in PAIRS if tr}
# links that must resolve differently per language
LINK_MAP = {
    'tr': {'/blog/what-is-pisa/': '/blog/pisa-nedir/',
           '/blog/dubai-top-schools/': '/blog/dubai-en-iyi-uluslararasi-okullar/',
           '/en/': '/tr/'},
    'en': dict(TR2EN, **{norm(k): v for k, v in pages.REDIRECTS.items()}, **{'/': '/en/'}),
}
EN_ONLY_SOURCES = {norm(k) for k in pages.REDIRECTS}


# ── element helpers ─────────────────────────────────────────────────────────

def remove_elements(s, pred):
    """Remove every element whose start tag satisfies pred(name, attrs)."""
    out, i, pos = [], 0, 0
    while True:
        m = TAG_RE.search(s, pos)
        if not m:
            break
        if m.group(0).startswith('<!--') or m.group(1) or not pred(m.group(2).lower(), m.group(3)):
            pos = m.end()
            continue
        end = _end_of(s, m.group(2).lower(), m.end())
        start = m.start()
        # drop a "<!-- Post: … -->" comment and indentation right before it
        before = s[i:start]
        cm = re.search(r'\n[ \t]*<!--[^\n]*-->[ \t]*\n[ \t]*$', before)
        before = before[:cm.start() + 1] if cm else re.sub(r'\n[ \t]*$', '\n', before)
        out.append(before)
        if s[end:end + 1] == '\n':
            end += 1
        i = pos = end
    out.append(s[i:])
    return ''.join(out)


def attr(attrs, name):
    m = re.search(r'\s' + name + r'=(["\'])(.*?)\1', attrs, re.S)
    return m.group(2) if m else None


# ── links ───────────────────────────────────────────────────────────────────

SKIP = ('mailto:', 'tel:', 'data:', 'javascript:', '#', '//', 'whatsapp:')


def resolve(url, src_path):
    """Absolute site path (+query/fragment) for an internal url, else None."""
    if url.startswith(SITE):
        url = url[len(SITE):] or '/'
    elif url.startswith(('http:', 'https:')) or url.startswith(SKIP) or not url:
        return None
    parts = urlsplit(urljoin(src_path, url))
    return parts.path, parts.query, parts.fragment


def map_url(url, src_path, lang, absolutize):
    r = resolve(url, src_path)
    if not r:
        return url
    path, query, frag = r
    full = url.startswith(SITE)
    target = LINK_MAP[lang].get(norm(path)) if '.' not in path.rsplit('/', 1)[-1] else None
    if target is None:
        if not absolutize:
            return url
        target = path
    out = enc(target) + (('?' + query) if query else '') + (('#' + frag) if frag else '')
    return SITE + out if full else out


def rewrite_urls(s, src_path, lang, absolutize):
    def one(m):
        return m.group(1) + m.group(2) + map_url(htmllib.unescape(m.group(3)), src_path, lang, absolutize) + m.group(2)

    def srcset(m):
        items = [x.strip().split(None, 1) for x in m.group(3).split(',') if x.strip()]
        new = ', '.join(' '.join([map_url(u[0], src_path, lang, absolutize)] + u[1:]) for u in items)
        return m.group(1) + m.group(2) + new + m.group(2)

    def cssurl(m):
        return 'url(' + m.group(1) + map_url(m.group(2), src_path, lang, absolutize) + m.group(1) + ')'

    s = re.sub(r'(\s(?:href|src|data-src|action|poster)=)(["\'])(.*?)\2', one, s)
    s = re.sub(r'(\ssrcset=)(["\'])(.*?)\2', srcset, s, flags=re.S)
    s = re.sub(r'url\((["\']?)([^)"\']+)\1\)', cssurl, s)
    return s


# ── scripts ─────────────────────────────────────────────────────────────────

def _strip_block(code, start_pat):
    """Remove `start_pat … {balanced}` (plus a trailing `)();` / `;`)."""
    while True:
        m = re.search(start_pat, code)
        if not m:
            return code
        i = code.index('{', m.start())
        depth = 0
        for j in range(i, len(code)):
            depth += {'{': 1, '}': -1}.get(code[j], 0)
            if depth == 0:
                break
        end = j + 1
        tail = re.match(r'\s*(\(\s*\)\s*\)\s*;?|\)\s*\(\s*\)\s*;?|\s*;)?', code[end:])
        code = code[:m.start()] + code[end + tail.end():]


def fix_scripts(s):
    # head "lang from localStorage" bootstraps
    s = re.sub(r'[ \t]*<script>\s*try\{var _l=localStorage\.getItem\(\'edualist_lang\'\).*?</script>\n?', '', s, flags=re.S)
    s = re.sub(r'[ \t]*<script>\s*/\* Early lang detection.*?</script>\n?', '', s, flags=re.S)

    def clean(m):
        code = m.group(2)
        if 'setLang' not in code and 'edualist_lang' not in code:
            return m.group(0)
        code = _strip_block(code, r'function\s+setLang\s*\(')
        code = _strip_block(code, r'\(\s*function\s*\(\s*\)\s*\{(?=[^}]*(?:edualist_lang|setLang\(|langTR))')
        return '' if not code.strip() else m.group(1) + code + '</script>\n'

    s = re.sub(r'([ \t]*<script>)(.*?)</script>\n?', clean, s, flags=re.S)
    # new app.js: bust the 6-month browser cache
    s = re.sub(r'(/app\.js)(\?v=[^"\']*)?(["\'])', r'\1?v=20261004\3', s)
    return s.replace('</body>', SWITCH_SNIPPET + '</body>', 1)


# ── head ────────────────────────────────────────────────────────────────────

def set_meta(s, key, value, prop='name'):
    pat = re.compile(r'(<meta\s+' + prop + r'="' + re.escape(key) + r'"\s+content=")[^"]*(")')
    if pat.search(s):
        return pat.sub(lambda m: m.group(1) + htmllib.escape(value) + m.group(2), s, count=1)
    return s


def rewrite_head(s, lang, url, alts, title=None, desc=None):
    head_end = s.index('</head>')
    head, rest = s[:head_end], s[head_end:]
    # keep only the first <title>
    first = re.search(r'<title[^>]*>.*?</title>', head, re.S)
    if first:
        head = head[:first.end()] + re.sub(r'[ \t]*<title[^>]*>.*?</title>\n?', '', head[first.end():], flags=re.S)
    head = re.sub(r'<html[^>]*>', lambda m: re.sub(r'lang="[^"]*"', f'lang="{lang}"', m.group(0)), head, count=1)
    if title:
        head = re.sub(r'<title[^>]*>.*?</title>', '<title>' + htmllib.escape(title, quote=False) + '</title>', head, count=1, flags=re.S)
        short = re.sub(r'\s*\|\s*Edualist$', '', title)
        head = set_meta(head, 'og:title', short, 'property')
        head = set_meta(head, 'twitter:title', short)
    if lang == 'en':
        head = re.sub(r'[ \t]*<meta\s+name="keywords"[^>]*>\n?', '', head)
    if desc:
        if re.search(r'<meta\s+name="description"', head):
            head = set_meta(head, 'description', desc)
        else:
            head = re.sub(r'(</title>)', r'\1\n  <meta name="description" content="' + htmllib.escape(desc) + '">', head, count=1)
        head = set_meta(head, 'og:description', desc, 'property')
        head = set_meta(head, 'twitter:description', desc)
    head = set_meta(head, 'og:url', SITE + enc(url), 'property')
    head = set_meta(head, 'og:locale', 'en_US' if lang == 'en' else 'tr_TR', 'property')
    if 'tr' in alts and 'en' in alts:
        head = set_meta(head, 'og:locale:alternate', 'tr_TR' if lang == 'en' else 'en_US', 'property')
    else:
        head = re.sub(r'[ \t]*<meta\s+property="og:locale:alternate"[^>]*>\n?', '', head)

    links = [f'<link rel="alternate" hreflang="{l}" href="{SITE}{enc(alts[l])}">' for l in ('tr', 'en') if l in alts]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}{enc(alts.get("tr", url))}">')
    head = re.sub(r'[ \t]*<link\s+rel="alternate"\s+hreflang="[^"]*"[^>]*>\n?', '', head)
    canon = f'<link rel="canonical" href="{SITE}{enc(url)}">'
    block = '\n  '.join([canon] + links)
    if re.search(r'<link\s+rel="canonical"[^>]*>', head):
        head = re.sub(r'<link\s+rel="canonical"[^>]*>', lambda m: block, head, count=1)
    else:
        head = re.sub(r'(</title>)', lambda m: m.group(1) + '\n  ' + block, head, count=1)
    return head + rest


# ── structured data ─────────────────────────────────────────────────────────

def is_turkish(v):
    t = v.replace('Özlem Çimen', '').replace('Çimen', '')
    return any(c in TR_CHARS for c in t)


def strip_turkish(o):
    """Drop string fields (recursively) that are Turkish."""
    if isinstance(o, dict):
        return {k: strip_turkish(v) for k, v in o.items()
                if not (isinstance(v, str) and k not in ('@type', '@context', '@id') and is_turkish(v))}
    if isinstance(o, list):
        return [strip_turkish(x) for x in o if not (isinstance(x, str) and is_turkish(x))]
    return o


def faq_from_body(body):
    qs = []
    for m in re.finditer(r'class="[^"]*\bfaq-q\b[^"]*"[^>]*>(.*?)</[a-z0-9]+>\s*'
                         r'(?:<[^>]+>\s*)*?<[a-z0-9]+[^>]*class="[^"]*\bfaq-a\b[^"]*"[^>]*>(.*?)</(?:p|div)>', body, re.S):
        q, a = (re.sub(r'\s+', ' ', htmllib.unescape(re.sub(r'<[^>]+>', ' ', x))).strip() for x in m.groups())
        if q and a:
            qs.append({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}})
    return qs


PAGE_TYPES = {'WebPage', 'AboutPage', 'ProfilePage', 'BlogPosting', 'Article'}
DROP_EN = {'HowTo', 'DefinedTermSet', 'Course'}


def rewrite_jsonld(s, lang, url, tr_url, title, desc, crumb):
    body = s.split('<body', 1)[-1]
    page_url = SITE + enc(url)

    def fix_urls(o):
        if isinstance(o, dict):
            return {k: fix_urls(v) for k, v in o.items()}
        if isinstance(o, list):
            return [fix_urls(x) for x in o]
        if isinstance(o, str) and o.startswith(SITE):
            return SITE + map_url(o[len(SITE):] or '/', '/', lang, False)
        return o

    def item(it):
        t = it.get('@type')
        types = set(t) if isinstance(t, list) else {t}
        if lang == 'tr':
            if 'inLanguage' in it and 'WebSite' not in types:
                it['inLanguage'] = 'tr'
            return fix_urls(it)
        # English
        if types & DROP_EN and is_turkish(json.dumps(it, ensure_ascii=False)):
            return None
        if 'BreadcrumbList' in types:
            return crumb
        if 'FAQPage' in types:
            qs = faq_from_body(body)
            return {'@context': it.get('@context', 'https://schema.org'), '@type': 'FAQPage', 'mainEntity': qs} if qs else None
        if types & PAGE_TYPES:
            h1 = re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S)
            h1 = re.sub(r'\s+', ' ', htmllib.unescape(re.sub(r'<[^>]+>', ' ', h1.group(1)))).strip() if h1 else None
            short = re.sub(r'\s*\|\s*Edualist$', '', title)
            for k in ('headline', 'name'):
                if k in it:
                    it[k] = h1 if (k == 'headline' and h1) else short
            if 'description' in it and desc:
                it['description'] = desc
            for k in ('url', '@id'):
                if isinstance(it.get(k), str) and it[k].startswith(SITE + enc(tr_url or '/__none__')):
                    it[k] = page_url + it[k][len(SITE + enc(tr_url)):]
            if isinstance(it.get('mainEntityOfPage'), (str, dict)):
                it['mainEntityOfPage'] = {'@type': 'WebPage', '@id': page_url}
        if 'inLanguage' in it and 'WebSite' not in types:
            it['inLanguage'] = 'en'
        if types & {'Service', 'ProfessionalService', 'LocalBusiness'} and is_turkish(str(it.get('name', ''))):
            it['name'] = 'Edualist'
        if 'description' in it and is_turkish(str(it['description'])) and desc:
            it['description'] = desc
        return strip_turkish(fix_urls(it))

    def block(m):
        if lang == 'tr':
            # minimal textual edits so the Turkish pages keep their formatting
            code = m.group(2)
            if '"WebSite"' not in code:
                code = re.sub(r'"inLanguage":\s*\[\s*"tr"\s*,\s*"en"\s*\]', '"inLanguage": "tr"', code)
            for old, new in LINK_MAP['tr'].items():
                if old.startswith('/blog/'):
                    code = code.replace(SITE + old, SITE + new)
            return m.group(1) + code + '</script>'
        data = json.loads(m.group(2))
        if isinstance(data, list):
            new = [x for x in (item(i) for i in data) if x]
        elif '@graph' in data:
            data['@graph'] = [x for x in (item(i) for i in data['@graph']) if x]
            new = data if data['@graph'] else None
        else:
            new = item(data)
        if not new:
            return ''
        return m.group(1) + '\n' + json.dumps(new, ensure_ascii=False, indent=2) + '\n  </script>'

    def sub(m):
        out = block(m)
        return m.group(0)[:len(m.group(0)) - len(m.group(0).lstrip())] + out + '\n' if out else ''

    return re.sub(r'[ \t]*(<script type="application/ld\+json"[^>]*>)(.*?)</script>\n?', sub, s, flags=re.S)


def breadcrumb(lang, url, name):
    home = '/en/' if lang == 'en' else '/'
    items = [('Home' if lang == 'en' else 'Ana Sayfa', home)]
    if '/blog/' in url and not url.endswith('/blog/'):
        items.append(('Blog', '/en/blog/' if lang == 'en' else '/blog/'))
    if url != home:
        items.append((name, url))
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + enc(u)} for i, (n, u) in enumerate(items)]}


# ── English text fixes ──────────────────────────────────────────────────────

EN_UI = {
    'WhatsApp ile yazın': 'Message us on WhatsApp',
    'WhatsApp ile iletişime geç': 'Contact us on WhatsApp',
    'Menüyü aç/kapat': 'Toggle menu',
    'Dil seçimi': 'Language',
    '"Menü"': '"Menu"',
    'Örn: Ayşe Demir': 'e.g. Jane Smith',
}

# Untranslated labels found on the English pages (text nodes / attributes).
EN_TEXT = {
    '>2020 – Günümüz<': '>2020 – Present<',
    'MBA — Uluslararası Pazarlama': 'MBA — International Marketing',
    'IB Müfredatı Uzmanlığı': 'IB Curriculum Expertise',
    'EAL Koçluğu': 'EAL Coaching',
    '🇬🇧 İngiltere': '🇬🇧 United Kingdom',
    '🇮🇹 İtalya': '🇮🇹 Italy',
    'IRT · 4 bilişsel alan': 'IRT · 4 cognitive domains',
    'Özlem Çimen — Uluslararası Eğitim Danışmanı': 'Özlem Çimen — International Education Consultant',
    'Özlem Çimen — Akademik Koç': 'Özlem Çimen — Academic Coach',
    'Dubai · Uluslararası okul ebeveyni': 'Dubai · International school parent',
    'Sharjah · Uluslararası okul ebeveyni': 'Sharjah · International school parent',
    'Abu Dhabi · IB MYP → DP geçiş ebeveyni': 'Abu Dhabi · Parent, IB MYP → DP transition',
    'İstanbul · Uzaktan expat koçluk': 'Istanbul · Remote expat coaching',
    'Dubai · A-Level müfredat geçişi ebeveyni': 'Dubai · Parent, A-Level transition',
    '>IB Uzmanı<': '>IB Specialist<',
    '>EAL Koçu<': '>EAL Coach<',
    '>20+ Yıl<': '>20+ Years<',
    '"Önceki"': '"Previous"',
    '"Sonraki"': '"Next"',
    '>Önceki<': '>Previous<',
    '>Sonraki<': '>Next<',
    'Çocuğunuzun Akademik Gelişimi: Kapsamlı Rehber →': "Your Child's Academic Development: Complete Guide (in Turkish) →",
    'Bu konuda kapsamlı rehberimize de göz atın:': 'See also our comprehensive guide:',
    'CAT4 Test Dubai Hazırlık Rehberi': 'CAT4 Test Dubai Preparation Guide',
    '>Koçluk<': '>Coaching<',
    '>Öğrenme<': '>Learning<',
    '>Üniversite<': '>University<',
    '🇦🇪 Dubai · Türk Aileler İçin': '🇦🇪 Dubai · For Turkish Families',
    'Görüşme Planla': 'Book a Session',
    'Örn: 8 yaş, 4. sınıf': 'e.g. age 8, Grade 4',
    'Örn: 9 yaş, 4. sınıf': 'e.g. age 9, Grade 4',
    'Ne zaman taşınıyorsunuz, hangi müfredat veya okul türü ilginizi çekiyor, varsa sorularınız...':
        'When are you moving, which curriculum or school type interests you, any questions...',
    'Ne zaman taşınmayı planlıyorsunuz, hangi müfredat veya okul türüyle ilgileniyorsunuz, sorularınız…':
        'When are you planning to move, which curriculum or school type interests you, any questions…',
    'C. ve N. Yıldız': 'C. & N. Yıldız',
    'E. ve T. Güneş': 'E. & T. Güneş',
    'Örn: Ahmet Yılmaz': 'e.g. John Doe',
    '🎓 Uluslararası Okul Danışmanlığı': '🎓 International School Consulting',
    'İngiltere / UK': 'UK',
    'İtalya / Italy': 'Italy',
    'Diğer / Other': 'Other',
    "Everything in one place: Your Child's Academic Development →":
        "Everything in one place: Your Child's Academic Development (in Turkish) →",
    "Everything in one place: Your Child&#39;s Academic Development →":
        "Everything in one place: Your Child&#39;s Academic Development (in Turkish) →",
}

EN_TITLES = {}  # en path -> short English title, filled in main()


def english_links(body):
    """Give links to English pages English text / alt where it was Turkish."""
    def anchor(m):
        open_tag, inner = m.group(1), m.group(2)
        href = attr(open_tag, 'href') or ''
        target = EN_TITLES.get(norm(urlsplit(href[len(SITE):] if href.startswith(SITE) else href).path))
        if not target:
            return m.group(0)
        inner = re.sub(r'(\salt=")([^"]*)(")', lambda a: a.group(1) + (htmllib.escape(target) if is_turkish(a.group(2)) else a.group(2)) + a.group(3), inner)
        if '<' not in inner and is_turkish(inner):
            arrow = ' →' if inner.rstrip().endswith('→') else ''
            lead = re.match(r'\s*', inner).group(0)
            inner = lead + htmllib.escape(target, quote=False) + arrow
        return open_tag + inner + '</a>'
    return re.sub(r'(<a\b[^>]*>)(.*?)</a>', anchor, body, flags=re.S)


def english_text(s):
    head_end = s.index('</head>')
    body = s[head_end:]
    for k, v in EN_UI.items():
        body = body.replace(k, v)
    body = english_links(body)
    body = re.sub(r'(?<![\w])((?:\d{1,2} )?)(' + '|'.join(TR_MONTHS) + r') (\d{4})\b',
                  lambda m: f'{m.group(1)}{EN_MONTHS[TR_MONTHS.index(m.group(2))]} {m.group(3)}', body)
    body = re.sub(r'\b(\d{1,3}) dk\b', r'\1 min', body)
    body = body.replace('Tüm hakları saklıdır. / All Rights Reserved.', 'All Rights Reserved.')
    body = body.replace('All Rights Reserved. / Tüm hakları saklıdır.', 'All Rights Reserved.')
    for k, v in EN_TEXT.items():
        body = body.replace(k, v)
    body = body.replace('text=Merhaba,%20Daha%20fazla%20bilgi%20almak%20istiyorum',
                        'text=Hello,%20I%20would%20like%20more%20information')
    return s[:head_end] + body


def set_counts(s, lang, n_posts):
    s = re.sub(r'(<span class="nav-count-badge">)\d+(</span>)', rf'\g<1>{n_posts}\2', s)
    rounded = f'{n_posts // 5 * 5}+'
    if lang == 'tr':
        s = re.sub(r'\b\d+\+ bağımsız rehber', f'{rounded} bağımsız rehber', s)
        s = re.sub(r'\b\d+ bağımsız rehber', f'{n_posts} bağımsız rehber', s)
    else:
        s = re.sub(r'\b\d+\+ independent guides', f'{rounded} independent guides', s)
        s = re.sub(r'\b\d+ independent guides', f'{n_posts} independent guides', s)
    return s


# ── main ────────────────────────────────────────────────────────────────────

def drop_cards(s, src_path, lang):
    def pred(name, attrs):
        if name != 'a' or not ({'blog-card', 'blog-related-card'} & set(_classes(attrs))):
            return False
        r = resolve(htmllib.unescape(attr(attrs, 'href') or ''), src_path)
        if not r:
            return False
        p = norm(r[0])
        if lang == 'en':
            return p not in LINK_MAP['en'] or not LINK_MAP['en'][p].startswith('/en/blog/')
        return p in EN_ONLY_SOURCES
    return remove_elements(s, pred)


def drop_marker_comments(s):
    """Remove comments that only marked the old tr-only / en-only blocks."""
    return re.sub(r'[ \t]*<!--(?:(?!-->).)*?(?:\b(?:tr|en)-only\b|\b(?:TR|EN) (?:CONTENT|FALLBACK|VERSION)\b)(?:(?!-->).)*-->[ \t]*\n?',
                  '', s, flags=re.S)


def tr_ratio(fragment):
    t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', fragment)).replace('Özlem Çimen', '')
    return sum(c in TR_CHARS for c in t) / max(len(t), 1), len(t)


def drop_foreign_faqs(s, lang):
    """Some FAQ blocks were never wrapped in tr-only/en-only; keep only the page's language."""
    def pred(name, attrs):
        return name == 'div' and 'blog-faq' in _classes(attrs)

    out, i, pos = [], 0, 0
    while True:
        m = TAG_RE.search(s, pos)
        if not m:
            break
        if m.group(0).startswith('<!--') or m.group(1) or not pred(m.group(2).lower(), m.group(3)):
            pos = m.end()
            continue
        end = _end_of(s, 'div', m.end())
        ratio, n = tr_ratio(s[m.start():end])
        foreign = ratio > 0.01 if lang == 'en' else (ratio < 0.002 and n > 200)
        if foreign:
            out.append(re.sub(r'[ \t]*$', '', s[i:m.start()]))
            if s[end:end + 1] == '\n':
                end += 1
            i = end
        pos = end
    out.append(s[i:])
    return ''.join(out)


# Gaps in the bilingual sources, patched before splitting.
SOURCE_FIXES = {
    '/neden-biz/': [(
        'color:var(--text-light);">Neden Edualist?</h1>',
        'color:var(--text-light);">Neden Edualist?</h1>\n      <h1 class="en-only" style="font-size:var(--font-2xl);'
        'font-weight:700;margin-top:1.5rem;color:var(--text-light);">Why Edualist?</h1>',
    )],
}


def build_page(src_html, src_path, lang, url, alts, title=None, desc=None):
    for old, new in SOURCE_FIXES.get(src_path, []):
        assert old in src_html, (src_path, old)
        src_html = src_html.replace(old, new)
    s = drop_marker_comments(split(src_html, lang))
    s = drop_foreign_faqs(s, lang)
    s = drop_cards(s, src_path, lang)
    s = rewrite_urls(s, src_path, lang, absolutize=(lang == 'en'))
    s = fix_scripts(s)
    s = rewrite_head(s, lang, url, alts, title, desc)
    if lang == 'en':
        s = english_text(s)
    name = re.sub(r'\s*\|\s*Edualist$', '', title or '')
    if not name:
        t = re.search(r'<title[^>]*>(.*?)</title>', s, re.S)
        name = htmllib.unescape(re.sub(r'\s*[|—-]\s*Edualist.*$', '', t.group(1))).strip() if t else ''
    s = rewrite_jsonld(s, lang, url, alts.get('tr'), title or name, desc, breadcrumb(lang, url, name))
    return s


def main():
    sources = {}
    for root, _, files in os.walk(ROOT):
        if 'index.html' in files:
            rel = '/' + os.path.relpath(root, ROOT).replace(os.sep, '/') + '/'
            rel = '/' if rel == '/./' else rel
            if rel in ('/', '/en/'):
                continue
            sources[rel] = open(os.path.join(root, 'index.html'), encoding='utf-8').read()
    sources['/en/'] = open(file_for('/en/'), encoding='utf-8').read()

    for _, en, _, title, _ in PAIRS:
        EN_TITLES[en] = re.sub(r'\s*\|\s*Edualist$', '', title)
    en_posts = sum(1 for _, en, *_ in PAIRS if en.startswith('/en/blog/'))
    tr_posts = sum(1 for p in sources if p.startswith('/blog/') and p != '/blog/' and p not in EN_ONLY_SOURCES)

    outputs = {}
    # Turkish pages (in place)
    for path, src in sources.items():
        if path == '/en/' or path in EN_ONLY_SOURCES:
            continue
        alts = {'tr': path}
        if path in TR2EN:
            alts['en'] = TR2EN[path]
        outputs[path] = set_counts(build_page(src, path, 'tr', path, alts), 'tr', tr_posts)
    # English pages
    for tr, en, src_path, title, desc in PAIRS:
        alts = {'en': en}
        if tr:
            alts['tr'] = norm(tr)
        src = sources[norm(src_path)]
        outputs[en] = set_counts(build_page(src, norm(src_path), 'en', en, alts, title, desc), 'en', en_posts)

    for path in EN_ONLY_SOURCES:
        os.remove(file_for(path))
        os.rmdir(os.path.dirname(file_for(path)))
    for path, s in outputs.items():
        f = file_for(path)
        os.makedirs(os.path.dirname(f), exist_ok=True)
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(s)
    print(f'wrote {len(outputs)} pages ({tr_posts} TR posts, {en_posts} EN posts)')


if __name__ == '__main__':
    main()
