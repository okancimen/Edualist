"""Generate school-review blog thumbnails with real school logos.

Usage:
  python3 tools/thumbs/school_thumbs.py /tmp/school-thumbs
  node tools/thumbs/render.js /tmp/school-thumbs
  # Then for each thumb-<slug>.png:
  cwebp -q 82 /tmp/school-thumbs/thumb-<slug>.png -o httpdocs/assets/blog/thumb-<slug>.webp
  cwebp -q 82 -resize 640 360 /tmp/school-thumbs/thumb-<slug>.png -o httpdocs/assets/blog/thumb-<slug>-640.webp
  # Or with ImageMagick:
  convert /tmp/school-thumbs/thumb-<slug>.png -quality 82 httpdocs/assets/blog/thumb-<slug>.webp
  convert /tmp/school-thumbs/thumb-<slug>.png -resize 640x360 -quality 82 httpdocs/assets/blog/thumb-<slug>-640.webp
"""
import base64, html, json, os, random, sys, urllib.request, ssl

G = '#DBAF2E'

# slug -> display settings
# logo_url: None = use initials fallback
# logo_bg: background behind logo box
#   'white' = #f5f6f8  (for coloured logos)
#   'dark'  = #071729  (for white/light logos)
SCHOOLS = {
    'jess-dubai-incelemesi': {
        'logo_url': 'https://www.jess.sch.ae/wp-content/uploads/2024/09/jess-logo-dark-10-png.webp',
        'logo_bg': 'white',
        'kicker': 'DUBAİ · İNGİLİZ OKULU',
        't1': 'JESS Dubai',
        't2': 'İncelemesi 2026',
        'sub': 'KHDA Outstanding · FS1–Y13 · Bekleme listesi rehberi',
    },
    'gems-wellington-dubai-incelemesi': {
        'logo_url': 'https://www.gemseducation.com/-/media/project/gems/corporate/_generic-content-images/gems-logo-navy-rgb.svg',
        'logo_bg': 'white',
        'kicker': 'DUBAİ · GEMS EĞİTİM',
        't1': 'GEMS Wellington',
        't2': 'İncelemesi 2026',
        'sub': 'KHDA Outstanding · 12 yıl üst üste · IB + A-Level',
    },
    'kings-school-dubai-incelemesi': {
        'logo_url': 'https://kings-edu.com/wp-content/themes/kingsgroup/images/kings-school-logo.png',
        'logo_bg': 'white',
        'kicker': "DUBAİ · İNGİLİZ OKULU",
        't1': "Kings' School",
        't2': 'Dubai İncelemesi 2026',
        'sub': 'KHDA Outstanding · British GCSE + A-Level',
    },
    'dubai-college-incelemesi': {
        'logo_url': 'https://resources.finalsite.net/images/v1652716294/dubaicollegeorg/amcb6n0brpwff0h8r4ql/DubaiCollege.svg',
        'logo_bg': 'dark',
        'kicker': 'DUBAİ · A-LEVEL',
        't1': 'Dubai College',
        't2': 'İncelemesi 2026',
        'sub': 'KHDA Outstanding · Seçici · A-Level uzmanı',
    },
    'repton-school-dubai-incelemesi': {
        'logo_url': 'https://www.reptondubai.org/wp-content/uploads/sites/15/2024/07/RDXB_IVORY_2f0290.png',
        'logo_bg': 'dark',
        'kicker': 'DUBAİ · İNGİLİZ OKULU',
        't1': 'Repton School',
        't2': 'Dubai İncelemesi 2026',
        'sub': 'KHDA Outstanding · British · Seçici kabul',
    },
    'gems-dubai-american-academy-incelemesi': {
        'logo_url': 'https://www.gemseducation.com/-/media/project/gems/corporate/_generic-content-images/gems-logo-navy-rgb.svg',
        'logo_bg': 'white',
        'kicker': 'DUBAİ · AMERİKAN OKULU',
        't1': 'GEMS Dubai',
        't2': 'American Academy 2026',
        'sub': 'KHDA Outstanding · AP · ABD üniversite yolu',
    },
    'dubai-international-academy-incelemesi': {
        'logo_url': 'https://innoventuresedu.static.amais.com/DIAEH_white-508_3551.webp',
        'logo_bg': 'dark',
        'kicker': 'DUBAİ · IB OKULU',
        't1': 'Dubai International',
        't2': 'Academy İncelemesi 2026',
        'sub': 'KHDA Outstanding · IB Dünya Okulu · Emirates Hills',
    },
    'nord-anglia-dubai-incelemesi': {
        'logo_url': 'https://www.nordangliaeducation.com/-/media/corporate/logo/logo-20210616.svg',
        'logo_bg': 'dark',
        'kicker': 'DUBAİ · ULUSLARARASI OKUL',
        't1': 'Nord Anglia',
        't2': 'Dubai İncelemesi 2026',
        'sub': 'KHDA Outstanding · IB + British · MIT ortaklığı',
    },
    'safa-community-school-dubai-incelemesi': {
        'logo_url': 'https://safacommunityschool.com/assets/frontend/img/logo.svg',
        'logo_bg': 'white',
        'kicker': 'DUBAİ · İNGİLİZ OKULU',
        't1': 'Safa Community',
        't2': 'School İncelemesi 2026',
        'sub': 'KHDA Outstanding · British · Safa 1 bölgesi',
    },
    'jumeirah-college-dubai-incelemesi': {
        'logo_url': 'https://www.gemsjc.com/-/media/project/gems/jcd_gems_jumeirah_college/_design-images/jc_logo-2-svg.svg',
        'logo_bg': 'white',
        'kicker': 'DUBAİ · A-LEVEL',
        't1': 'Jumeirah College',
        't2': 'Dubai İncelemesi 2026',
        'sub': 'KHDA Outstanding · Sadece Sixth Form · A-Level uzmanı',
    },
    'brighton-college-dubai-incelemesi': {
        'logo_url': 'https://www.brightoncollege.ae/assets/img/bci-dubai-blue.svg',
        'logo_bg': 'white',
        'kicker': 'DUBAİ · İNGİLİZ OKULU',
        't1': 'Brighton College',
        't2': 'Dubai İncelemesi 2026',
        'sub': 'KHDA Outstanding (ilk denetimde) · A-Level · MBR City',
    },
    'dubai-british-school-incelemesi': {
        'logo_url': 'https://www.dubaibritishschool.ae/wp-content/uploads/2024/09/Emirates-hills-updated.svg',
        'logo_bg': 'dark',
        'kicker': 'DUBAİ · İNGİLİZ OKULU',
        't1': 'Dubai British',
        't2': 'School İncelemesi 2026',
        'sub': 'KHDA Outstanding · Jumeirah Park · British müfredat',
    },
    'sunmarke-school-dubai-incelemesi': {
        'logo_url': 'https://sunmarke.com/wp-content/uploads/2026/01/sunmarke-logo-main.svg',
        'logo_bg': 'white',
        'kicker': 'DUBAİ · İNGİLİZ OKULU',
        't1': 'Sunmarke School',
        't2': 'Dubai İncelemesi 2026',
        'sub': 'KHDA Outstanding · British · Jumeirah Park',
    },
    'gems-founders-school-dubai-incelemesi': {
        'logo_url': 'https://www.gemseducation.com/-/media/project/gems/corporate/_generic-content-images/gems-logo-navy-rgb.svg',
        'logo_bg': 'white',
        'kicker': 'DUBAİ · AMERİKAN OKULU',
        't1': 'GEMS Founders',
        't2': 'School İncelemesi 2026',
        'sub': 'KHDA Good · Açık kayıt · AED 25k–55k',
    },
    'gems-jumeirah-primary-school-dubai-incelemesi': {
        'logo_url': 'https://www.gemseducation.com/-/media/project/gems/corporate/_generic-content-images/gems-logo-navy-rgb.svg',
        'logo_bg': 'white',
        'kicker': 'DUBAİ · İLKOKUL',
        't1': 'GEMS Jumeirah',
        't2': 'Primary İncelemesi 2026',
        'sub': 'KHDA Outstanding · FS1–Year 6 · AED 42k–52k',
    },
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120',
    'Accept': '*/*',
}

HEADERS_CURL = {
    'User-Agent': 'curl/7.88.0',
    'Accept': '*/*',
}

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def fetch_logo(url):
    for headers in (HEADERS, HEADERS_CURL):
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, context=CTX, timeout=15)
            data = resp.read()
            ct = resp.headers.get('Content-Type', 'image/png').split(';')[0].strip()
            if 'svg' in ct:
                ct = 'image/svg+xml'
            elif 'webp' in ct:
                ct = 'image/webp'
            elif 'png' in ct:
                ct = 'image/png'
            elif 'jpeg' in ct or 'jpg' in ct:
                ct = 'image/jpeg'
            return data, ct
        except Exception:
            pass
    raise RuntimeError(f'Could not fetch {url}')


def stars(seed, n=55):
    rnd = random.Random(seed)
    return ''.join(
        f'<circle cx="{rnd.uniform(0,800):.0f}" cy="{rnd.uniform(0,410):.0f}" '
        f'r="{rnd.choice([0.8,1,1.2,1.6])}" '
        f'fill="{rnd.choice(["#ffffff","#ffffff",G])}" '
        f'opacity="{rnd.uniform(.25,.7):.2f}"/>'
        for _ in range(n)
    )


INITIALS_SVG = {
    # Simple bold initials rendered as SVG text inside the left area
}


def logo_page(slug, logo_b64, mime, bg, kicker, t1, t2, sub):
    e = html.escape
    bg_color = '#f5f6f8' if bg == 'white' else '#071729'
    border = '1px solid #e0e4ea' if bg == 'white' else '1px solid rgba(255,255,255,0.08)'
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:800px;height:450px;overflow:hidden}}
.wrap{{position:relative;width:800px;height:450px;background:linear-gradient(160deg,#0f2a49 0%,#0b213a 60%,#081a2e 100%);font-family:'Liberation Sans',sans-serif}}
svg.bg{{position:absolute;inset:0}}
.logo-box{{position:absolute;left:44px;top:88px;width:230px;height:230px;background:{bg_color};border-radius:16px;border:{border};display:flex;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;overflow:hidden}}
.logo-box img{{max-width:100%;max-height:100%;object-fit:contain;display:block}}
.rule{{position:absolute;left:322px;top:96px;width:2px;height:218px;background:{G};opacity:.9}}
.text{{position:absolute;left:350px;top:0;width:420px;height:410px;display:flex;flex-direction:column;justify-content:center}}
.k{{color:{G};font-size:14px;letter-spacing:2.5px;font-weight:700;margin-bottom:14px}}
.t{{font-family:'Liberation Serif',serif;font-weight:700;line-height:1.08;white-space:nowrap}}
.t1{{color:#fff}} .t2{{color:{G}}}
.s{{color:#d7dee8;font-size:17px;margin-top:16px;line-height:1.35}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:40px;background:#071729;border-top:2px solid {G};color:{G};font-size:13px;font-weight:700;letter-spacing:2px;display:flex;align-items:center;justify-content:center}}
.top{{position:absolute;left:0;right:0;top:0;height:6px;background:{G}}}
</style></head><body><div class="wrap">
<svg class="bg" width="800" height="450">{stars(slug)}</svg>
<div class="top"></div>
<div class="logo-box"><img src="data:{mime};base64,{logo_b64}" alt=""></div>
<div class="rule"></div>
<div class="text"><div class="k">{e(kicker)}</div><div class="t t1">{e(t1)}</div><div class="t t2">{e(t2)}</div><div class="s">{e(sub)}</div></div>
<div class="foot">EDUALIST · DUBAİ OKUL REHBERİ</div>
</div>
<script>
  let fs=50;const ts=[...document.querySelectorAll('.t')];
  const fits=()=>ts.every(t=>t.scrollWidth<=420);
  do{{ts.forEach(t=>t.style.fontSize=fs+'px');fs-=1;}}while(!fits()&&fs>24);
</script></body></html>'''


def initials_page(slug, initials, kicker, t1, t2, sub):
    e = html.escape
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:800px;height:450px;overflow:hidden}}
.wrap{{position:relative;width:800px;height:450px;background:linear-gradient(160deg,#0f2a49 0%,#0b213a 60%,#081a2e 100%);font-family:'Liberation Sans',sans-serif}}
svg.bg{{position:absolute;inset:0}}
.init-box{{position:absolute;left:44px;top:88px;width:230px;height:230px;border:2px solid {G};border-radius:16px;display:flex;align-items:center;justify-content:center}}
.init-box span{{font-family:'Liberation Serif',serif;font-size:72px;font-weight:700;color:{G};letter-spacing:-.02em}}
.rule{{position:absolute;left:322px;top:96px;width:2px;height:218px;background:{G};opacity:.9}}
.text{{position:absolute;left:350px;top:0;width:420px;height:410px;display:flex;flex-direction:column;justify-content:center}}
.k{{color:{G};font-size:14px;letter-spacing:2.5px;font-weight:700;margin-bottom:14px}}
.t{{font-family:'Liberation Serif',serif;font-weight:700;line-height:1.08;white-space:nowrap}}
.t1{{color:#fff}} .t2{{color:{G}}}
.s{{color:#d7dee8;font-size:17px;margin-top:16px;line-height:1.35}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:40px;background:#071729;border-top:2px solid {G};color:{G};font-size:13px;font-weight:700;letter-spacing:2px;display:flex;align-items:center;justify-content:center}}
.top{{position:absolute;left:0;right:0;top:0;height:6px;background:{G}}}
</style></head><body><div class="wrap">
<svg class="bg" width="800" height="450">{stars(slug)}</svg>
<div class="top"></div>
<div class="init-box"><span>{e(initials)}</span></div>
<div class="rule"></div>
<div class="text"><div class="k">{e(kicker)}</div><div class="t t1">{e(t1)}</div><div class="t t2">{e(t2)}</div><div class="s">{e(sub)}</div></div>
<div class="foot">EDUALIST · DUBAİ OKUL REHBERİ</div>
</div>
<script>
  let fs=50;const ts=[...document.querySelectorAll('.t')];
  const fits=()=>ts.every(t=>t.scrollWidth<=420);
  do{{ts.forEach(t=>t.style.fontSize=fs+'px');fs-=1;}}while(!fits()&&fs>24);
</script></body></html>'''


def asset_name(slug):
    return 'thumb-' + slug.replace('ı', 'i')


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    jobs = []
    ok = 0
    fail = 0
    for slug, cfg in SCHOOLS.items():
        name = asset_name(slug)
        f = os.path.join(out, name + '.html')
        if cfg.get('logo_url'):
            try:
                data, mime = fetch_logo(cfg['logo_url'])
                b64 = base64.b64encode(data).decode()
                content = logo_page(slug, b64, mime, cfg['logo_bg'],
                                    cfg['kicker'], cfg['t1'], cfg['t2'], cfg['sub'])
                print(f'  logo  {slug} ({len(data)}b {mime})')
                ok += 1
            except Exception as ex:
                print(f'  WARN  {slug}: logo fetch failed ({ex}), using initials fallback')
                initials = ''.join(w[0].upper() for w in cfg['t1'].split()[:3])
                content = initials_page(slug, initials, cfg['kicker'], cfg['t1'], cfg['t2'], cfg['sub'])
                fail += 1
        else:
            content = initials_page(slug, cfg['initials'], cfg['kicker'],
                                    cfg['t1'], cfg['t2'], cfg['sub'])
            print(f'  init  {slug}')
        open(f, 'w', encoding='utf-8').write(content)
        jobs.append({'html': f, 'name': name})
    json.dump(jobs, open(os.path.join(out, 'jobs.json'), 'w'))
    print(f'\n{len(jobs)} pages ({ok} logo, {fail} fallback, {len(jobs)-ok-fail} planned initials)')
