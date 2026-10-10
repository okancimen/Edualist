#!/usr/bin/env python3
"""Add tag-based filtering to TR and EN blog listing pages."""

import re

# ── Tag mappings (slug → space-separated tag keys) ──────────────────────────
TR_TAGS = {
    # Dubai
    "dubai-ingiliz-okullari-a-level":          "dubai muefredat",
    "dubai-amerikan-mufredat-ap-okullari":      "dubai ap",
    "dubai-ib-okullari-mezun-basarisi":         "dubai ib",
    "dubai-okul-ucretleri-2026":                "dubai okul-secimi",
    "dubai-okul-tatil-tarihleri":               "dubai",
    "khda-notu-nedir":                          "dubai",
    "eal-nedir":                                "dubai muefredat",
    "dubai-okul-kayit-sezonu-ne-zaman-baslar":  "dubai okul-secimi",
    "dubai-okul-bekleme-listesi":               "dubai okul-secimi",
    "dubai-turk-okulu-var-mi":                  "dubai",
    "dubai-egitim-sistemi":                     "dubai",
    "dubai-basarili-turk-ogrenciler":           "dubai",
    "dubai-yasam-maliyeti-2026":                "dubai",
    "dubai-semt-rehberi":                       "dubai",
    "dubai-okul-burs-imkanlari":                "dubai okul-secimi",
    "dubai-okul-basvuru-nasil-yapilir":         "dubai okul-secimi",
    "dubai-gelmeden-once-bilmeniz-gerekenler":  "dubai",
    "dubai-en-iyi-uluslararasi-okullar":        "dubai okul-secimi",
    "dubai-ib-okul-secimi":                     "dubai ib okul-secimi",
    "turkiyeden-dubaya-tasima-cocuk-okul":      "dubai",
    "dubai-ozel-okul-mu-devlet-okulu-mu":       "dubai okul-secimi",
    "dubai-turk-aileler-okul-rehberi":          "dubai okul-secimi",
    "dubai-khda-okul-dereceleri-ucret-karsilastirmasi": "dubai okul-secimi",
    "dubai-okul-kayit-rehberi":                 "dubai okul-secimi",
    "ingilizcesi-yetersiz-cocuk-dubai-okulu-uyum": "dubai akademik-destek",
    "dubai-expat-cocuk-akademik-destek":        "dubai akademik-destek",
    "turkiye-ozel-okuldan-dubai-uluslararasi-okula-gecis": "dubai okul-secimi",
    "turkiye-dubai-okul-ucreti-karsilastirma":  "dubai okul-secimi",
    "bae-uluslararasi-okul-rehberi":            "dubai yurtdisi okul-secimi",
    # IB
    "ib-diploma-universite-basvuru":            "ib kariyer",
    "ib-alevel-amerikan-mufredat-karsilastirma":"ib ap muefredat",
    "basarili-ogrenciler-ib-de-neden-zorlanir": "ib akademik-destek",
    "cocugum-ib-ye-basliyor":                   "ib akademik-destek",
    "ib-gecisinde-akademik-kocluk":             "ib akademik-destek",
    # AP (non-dubai already done above)
    # Müfredat
    "cat4-sinavi-nedir":                        "muefredat",
    "pisa-nedir":                               "muefredat",
    "pisa-2025-erken-is-deneyimi":              "muefredat kariyer",
    "pisa-2025-turkiye-sonuclari":              "muefredat",
    "farklilastirilmis-ogretim-nedir":          "muefredat",
    "turkiye-egitim-sistemi-neden-yetmiyor":    "muefredat",
    "ingiltere-devlet-ozel-okul":               "muefredat yurtdisi okul-secimi",
    "turk-egitim-sisteminden-uluslararasi-okula-gecis": "muefredat okul-secimi",
    "lgs-surecinde-ders-calis-savaslari":       "muefredat akademik-destek",
    # Okul Seçimi
    "katar-okul-kayit-rehberi":                 "yurtdisi okul-secimi",
    "abu-dhabi-uluslararasi-okullar":           "yurtdisi okul-secimi",
    "international-school-nedir":               "okul-secimi",
    "uluslararasi-okul-mulakat-sorulari":       "okul-secimi",
    "uluslararasi-okul-mulakatı-nasil-gecilir": "okul-secimi",
    "robert-kolej-ucreti-2026":                 "okul-secimi",
    "yurtdisi-egitim-maliyet-karsilastirma":    "yurtdisi okul-secimi",
    "cocugunuz-yurt-disinda-okumaya-hazir-mi":  "yurtdisi okul-secimi",
    "cocugumu-yurtdisinda-okutmali-miyim":      "yurtdisi okul-secimi",
    "cocugum-uluslararasi-okula-geciyor":       "okul-secimi akademik-destek",
    "cocugum-okul-degistiriyor":                "okul-secimi akademik-destek",
    # Akademik Destek
    "cocugunuzun-guclu-yonleri":               "akademik-destek",
    "cocugum-akademik-olarak-geride-kaliyor":  "akademik-destek",
    "cocugum-motivasyonunu-kaybetti":          "akademik-destek",
    "cocugum-sinav-kaygisi-yasiyor":           "akademik-destek",
    "cocugum-ders-calismak-istemiyor":         "akademik-destek",
    "ogretmen-tembel-dedi":                    "akademik-destek",
    "cocugum-ingilizce-ogrenemıyor":      "akademik-destek",
    "egitim-kocu-ne-yapar":                    "akademik-destek",
    "akademik-koc-nedir":                      "akademik-destek",
    "ozel-ders-mi-akademik-koc-mu":            "akademik-destek",
    "eduentry-uluslararasi-akademik-degerlendirme-nedir": "akademik-destek",
    "cocugunuzun-gercek-akademik-seviyesi":    "akademik-destek",
    "anxious-generation-ergen-ruh-sagligi":    "akademik-destek",
    "ogretmen-tembel-dedi":                    "akademik-destek",
    # Yurt Dışı
    "almanya-okul-kayit-rehberi":              "yurtdisi",
    "almanyada-turk-okulu-var-mi":             "yurtdisi",
    "kanada-okul-kayit-rehberi":               "yurtdisi",
    "ispanya-okul-kayit-rehberi":              "yurtdisi",
    "italya-okul-kayit-rehberi":               "yurtdisi",
    "fransa-okul-kayit-rehberi":               "yurtdisi",
    "hollanda-okul-kayit-rehberi":             "yurtdisi",
    "ingiltere-okul-kayit-rehberi":            "yurtdisi",
    "ucuncu-kultur-cocugu-tck-rehberi":        "yurtdisi",
    "lise-yurt-disi-tasinma-adaptasyon":       "yurtdisi",
    "oglumun-ingilizcesi-iyiydi":              "yurtdisi",
    "kizim-sinifin-zemininde-yatiyordu":       "yurtdisi",
    "turkiye-yilda-46000-cocugunu-yurt-disina-gonderiyor": "yurtdisi",
    # Kariyer
    "cocuklar-icin-gelecek-becerileri":        "kariyer",
    "yapay-zekaya-direncli-meslekler":         "kariyer",
    "gelecegin-meslekleri-ebeveyn-sorulari":   "kariyer",
    "gelecekte-hangi-meslekler-onem-kazanacak":"kariyer",
    "lise-ogrencisi-staj-is-deneyimi":         "kariyer",
    "universitede-fark-yaratan-aktiviteler":   "kariyer",
    "lise-ogrencisi-yaz-programlari":          "kariyer",
    "yurt-disi-universite-hazirlik-lisede":    "kariyer",
}

EN_TAGS = {
    "dubai-british-schools-a-level":           "dubai curriculum",
    "best-ap-schools-dubai":                   "dubai ap",
    "dubai-ib-schools-graduate-success":       "dubai ib",
    "dubai-top-schools":                       "dubai school-selection",
    "future-skills-for-children":              "careers",
    "future-careers-2030-parent-questions":    "careers",
    "ai-proof-jobs":                           "careers",
    "child-strengths-and-weaknesses":          "academic-support",
    "dubai-school-fees-2026":                  "dubai school-selection",
    "qatar-international-schools":             "international school-selection",
    "dubai-school-holidays":                   "dubai",
    "what-is-a-khda-rating":                   "dubai",
    "what-is-eal":                             "dubai curriculum",
    "dubai-school-registration-season":        "dubai school-selection",
    "ib-diploma-university-requirements":      "ib careers",
    "what-is-pisa":                            "curriculum",
    "turkish-school-in-germany":               "international",
    "robert-kolej-fees-2026":                  "school-selection",
    "pisa-2025-early-work-experience":         "curriculum careers",
    "cat4-test-dubai":                         "curriculum dubai",
    "pisa-2025-turkey-results":                "curriculum",
    "dubai-school-waiting-list":               "dubai school-selection",
    "turkish-school-in-dubai":                 "dubai",
    "turkey-to-dubai-international-school":    "dubai school-selection",
    "what-is-an-international-school":         "school-selection",
    "dubai-education-system":                  "dubai",
    "turkish-students-succeeding-in-dubai":    "dubai",
    "anxious-generation-teen-mental-health":   "academic-support",
    "dubai-cost-of-living-2026":               "dubai",
    "dubai-neighbourhood-school-guide":        "dubai",
    "dubai-school-scholarships":               "dubai school-selection",
    "abu-dhabi-international-schools":         "international school-selection",
    "how-to-apply-dubai-school":               "dubai school-selection",
    "international-school-interview-questions":"school-selection",
    "turkey-vs-dubai-school-fees":             "dubai school-selection",
    "jobs-of-the-future":                      "careers",
    "eduentry-international-assessment":       "academic-support",
    "why-turkish-education-falls-short":       "curriculum",
    "turkey-46000-children-abroad":            "international",
    "uae-international-school-guide":          "dubai international school-selection",
    "dubai-international-schools-khda-fees-2026": "dubai school-selection",
    "dubai-khda-outstanding-schools":          "dubai school-selection",
    "how-to-pass-international-school-interview": "school-selection",
    "school-enrolment-canada":                 "international",
    "should-my-child-study-abroad":            "international school-selection",
    "international-education-cost":            "international school-selection",
    "ib-vs-a-level-vs-ap":                     "ib ap curriculum",
    "limited-english-child-dubai-school":      "dubai academic-support",
    "before-moving-to-dubai":                  "dubai",
    "uk-school-enrolment":                     "international",
    "school-enrolment-france":                 "international",
    "school-enrolment-netherlands":            "international",
    "school-enrolment-italy":                  "international",
    "school-enrolment-germany":                "international",
    "dubai-school-registration":               "dubai school-selection",
    "why-high-achievers-struggle-with-ib":     "ib academic-support",
    "what-does-an-education-coach-do":         "academic-support",
    "childs-real-academic-level":              "academic-support",
    "what-is-an-academic-coach":               "academic-support",
}

# ── Shared CSS + JS (injected once per file) ─────────────────────────────────
FILTER_CSS = """<style id="blog-filter-css">
.blog-filter-bar{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:2.5rem}
.blog-filter-btn{padding:.38rem 1.1rem;border-radius:50px;border:1.5px solid hsla(212,66%,13%,.18);background:transparent;color:var(--primary);font-family:inherit;font-size:.82rem;font-weight:600;cursor:pointer;transition:background .18s,color .18s,border-color .18s;letter-spacing:.02em}
.blog-filter-btn:hover{border-color:var(--primary);background:hsla(212,66%,13%,.06)}
.blog-filter-btn.active{background:var(--primary);color:#fff;border-color:var(--primary)}
.blog-card[hidden]{display:none!important}
</style>"""

TR_FILTER_HTML = """<div class="blog-filter-bar" id="blogFilterBar" role="group" aria-label="Kategori filtrele">
        <button class="blog-filter-btn active" data-filter="all">Tümü</button>
        <button class="blog-filter-btn" data-filter="dubai">Dubai</button>
        <button class="blog-filter-btn" data-filter="ib">IB</button>
        <button class="blog-filter-btn" data-filter="ap">AP</button>
        <button class="blog-filter-btn" data-filter="muefredat">Müfredat</button>
        <button class="blog-filter-btn" data-filter="okul-secimi">Okul Seçimi</button>
        <button class="blog-filter-btn" data-filter="akademik-destek">Akademik Destek</button>
        <button class="blog-filter-btn" data-filter="yurtdisi">Yurt Dışı</button>
        <button class="blog-filter-btn" data-filter="kariyer">Kariyer</button>
      </div>"""

EN_FILTER_HTML = """<div class="blog-filter-bar" id="blogFilterBar" role="group" aria-label="Filter by category">
        <button class="blog-filter-btn active" data-filter="all">All</button>
        <button class="blog-filter-btn" data-filter="dubai">Dubai</button>
        <button class="blog-filter-btn" data-filter="ib">IB</button>
        <button class="blog-filter-btn" data-filter="ap">AP</button>
        <button class="blog-filter-btn" data-filter="curriculum">Curriculum</button>
        <button class="blog-filter-btn" data-filter="school-selection">School Selection</button>
        <button class="blog-filter-btn" data-filter="academic-support">Academic Support</button>
        <button class="blog-filter-btn" data-filter="international">International</button>
        <button class="blog-filter-btn" data-filter="careers">Careers</button>
      </div>"""

FILTER_JS = """<script>
(function(){
  var bar=document.getElementById('blogFilterBar');
  if(!bar)return;
  var cards=document.querySelectorAll('.blog-card[data-tags]');
  bar.addEventListener('click',function(e){
    var btn=e.target.closest('[data-filter]');
    if(!btn)return;
    bar.querySelectorAll('.blog-filter-btn').forEach(function(b){b.classList.remove('active');});
    btn.classList.add('active');
    var f=btn.dataset.filter;
    cards.forEach(function(c){
      c.hidden=f!=='all'&&!(' '+c.dataset.tags+' ').includes(' '+f+' ');
    });
  });
})();
</script>"""

def slug_from_href(href):
    """Extract the final path segment from an href."""
    href = href.strip().rstrip('/')
    return href.split('/')[-1]

def add_data_tags(html, tag_map):
    """Add data-tags attribute to every <a class="blog-card ..."> element."""
    def replacer(m):
        full = m.group(0)
        href_match = re.search(r'href="([^"]*)"', full)
        if not href_match:
            return full
        slug = slug_from_href(href_match.group(1))
        tags = tag_map.get(slug, '')
        if not tags:
            # Try lowercase + strip accents minimally
            tags = tag_map.get(slug.lower(), '')
        if not tags:
            return full
        if 'data-tags=' in full:
            return full  # already tagged
        # Insert data-tags after the href attribute
        return full.replace(
            href_match.group(0),
            href_match.group(0) + f' data-tags="{tags}"',
            1
        )
    # Match opening <a> tags that contain blog-card class
    pattern = r'<a\s[^>]*class="blog-card[^"]*"[^>]*>'
    return re.sub(pattern, replacer, html)

def process_file(path, tag_map, filter_html, lang):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Skip if already processed
    if 'blogFilterBar' in html:
        print(f'  {path}: already has filter bar, skipping filter injection')
    else:
        # Inject CSS just before </style> of the first big style block
        # (append before </style> tag)
        html = html.replace('</style>\n  <meta name="viewport"',
                            FILTER_CSS + '\n</style>\n  <meta name="viewport"', 1)

        # Inject filter bar just before <div class="blog-grid">
        html = html.replace('<div class="blog-grid">',
                            filter_html + '\n      <div class="blog-grid">', 1)

        # Inject JS just before </body>
        html = html.replace('</body>', FILTER_JS + '\n</body>', 1)

    # 2. Add data-tags to each card
    html = add_data_tags(html, tag_map)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    # Count tagged cards
    tagged = len(re.findall(r'data-tags="', html))
    print(f'  {path}: {tagged} cards tagged')

print('Processing TR blog...')
process_file(
    '/Users/okancimen/Documents/GitHub/new/Edualist/httpdocs/blog/index.html',
    TR_TAGS, TR_FILTER_HTML, 'tr'
)

print('Processing EN blog...')
process_file(
    '/Users/okancimen/Documents/GitHub/new/Edualist/httpdocs/en/blog/index.html',
    EN_TAGS, EN_FILTER_HTML, 'en'
)

print('Done.')
