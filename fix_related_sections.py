#!/usr/bin/env python3
"""Fix related sections for CAT4 + child academic support clusters."""
import re, os

BASE = '/Users/okancimen/Documents/GitHub/new/Edualist/httpdocs/blog'

def card(slug, thumb, alt, title, meta):
    return (f'        <a href="/blog/{slug}/" class="blog-related-card">\n'
            f'          <img src="/assets/blog/{thumb}" alt="{alt}" width="800" height="450" loading="lazy" decoding="async">\n'
            f'          <div class="blog-related-card-body"><p class="blog-related-card-title">{title}</p><p class="blog-related-card-meta">{meta}</p></div>\n'
            f'        </a>')

CARDS = {
    'cat4-sinavi-nedir': card('cat4-sinavi-nedir', 'thumb-cat4-sinavi-nedir.webp',
        'CAT4 Sınavı Nedir Dubai',
        'CAT4 Sınavı Nedir?',
        'Dubai okullarında başvuru ve hazırlık rehberi'),
    'cat4-ornek-sorular': card('cat4-ornek-sorular', 'thumb-cat4-sinavi-nedir.webp',
        'CAT4 Örnek Sorular',
        'CAT4 Örnek Sorular 2027',
        'Her pil için soru tipleri ve hazırlık stratejisi'),
    'cocugum-ingilizce-ogrenemiyor': card('cocugum-ingilizce-ogrenemiyor', 'thumb-cocugum-ingilizce-ogrenemiyor.webp',
        'Çocuğum İngilizce Öğrenemiyor',
        'Çocuğum İngilizce Öğrenemiyor',
        'Yöntem mi, motivasyon mu, seviye mi — kök nedeni bulmak'),
    'cocugum-sinav-kaygisi-yasiyor': card('cocugum-sinav-kaygisi-yasiyor', 'thumb-cocugum-sinav-kaygisi-yasiyor.webp',
        'Çocuğum Sınav Kaygısı Yaşıyor',
        'Çocuğum Sınav Kaygısı Yaşıyor',
        'Anlamak ve yönetmek için rehber'),
    'dubai-expat-cocuk-akademik-destek': card('dubai-expat-cocuk-akademik-destek', 'thumb-dubai-expat-cocuk-akademik-destek.webp',
        'Dubai Expat Çocuk Akademik Destek',
        'Expat Çocuklar için Akademik Destek',
        "Dubai'de aileler için tam rehber"),
    'ingilizcesi-yetersiz-cocuk-dubai-okulu-uyum': card('ingilizcesi-yetersiz-cocuk-dubai-okulu-uyum', 'thumb-ingilizce-uyum.webp',
        'İngilizcesi Yetersiz Çocuk Dubai Okulu Uyum',
        'İngilizcesi Yetersiz Çocuk Nasıl Uyum Sağlar?',
        'Dubai uluslararası okullarında dil bariyerini aşmak'),
    'oglumun-ingilizcesi-iyiydi': card('oglumun-ingilizcesi-iyiydi', 'thumb-ingilizce.webp',
        'Oğlumun İngilizcesi İyiydi',
        '"Oğlumun İngilizcesi İyiydi" — Gerçek Bir Hikaye',
        'Akademik İngilizce ve dil desteğinin önemi'),
    'eal-nedir': card('eal-nedir', 'thumb-eal-nedir.webp',
        'EAL Nedir Dubai Uluslararası Okulları',
        'EAL Nedir? Dubai Okullarında İngilizce Dil Desteği',
        'EAL programı nasıl işler, nasıl erişilir'),
}

def related_section(heading, card_keys):
    cards_html = '\n'.join(CARDS[k] for k in card_keys)
    return (f'  <section class="blog-related-section">\n'
            f'    <div class="container">\n'
            f'      <h2 class="blog-related-title">{heading}</h2>\n'
            f'      <div class="blog-related-grid">\n'
            f'{cards_html}\n'
            f'      </div>\n'
            f'    </div>\n'
            f'  </section>')

UPDATES = {
    'cat4-sinavi-nedir': related_section('İlgili Rehberler', [
        'cat4-ornek-sorular',
        'cocugum-sinav-kaygisi-yasiyor',
        'dubai-expat-cocuk-akademik-destek',
    ]),
    'cat4-ornek-sorular': related_section('İlgili Rehberler', [
        'cat4-sinavi-nedir',
        'cocugum-sinav-kaygisi-yasiyor',
        'dubai-expat-cocuk-akademik-destek',
    ]),
    'cocugum-ingilizce-ogrenemiyor': related_section('İlgili Rehberler', [
        'ingilizcesi-yetersiz-cocuk-dubai-okulu-uyum',
        'oglumun-ingilizcesi-iyiydi',
        'eal-nedir',
    ]),
    'cocugum-sinav-kaygisi-yasiyor': related_section('İlgili Rehberler', [
        'cat4-sinavi-nedir',
        'cat4-ornek-sorular',
        'dubai-expat-cocuk-akademik-destek',
    ]),
    'dubai-expat-cocuk-akademik-destek': related_section('İlgili Rehberler', [
        'cat4-sinavi-nedir',
        'cocugum-sinav-kaygisi-yasiyor',
        'cocugum-ingilizce-ogrenemiyor',
    ]),
    'ingilizcesi-yetersiz-cocuk-dubai-okulu-uyum': related_section('İlgili Rehberler', [
        'cocugum-ingilizce-ogrenemiyor',
        'oglumun-ingilizcesi-iyiydi',
        'eal-nedir',
    ]),
    'oglumun-ingilizcesi-iyiydi': related_section('İlgili Rehberler', [
        'cocugum-ingilizce-ogrenemiyor',
        'ingilizcesi-yetersiz-cocuk-dubai-okulu-uyum',
        'eal-nedir',
    ]),
}

SECTION_RE = re.compile(r'<section class="blog-related-section">.*?</section>', re.S)

updated = 0
for slug, new_section in UPDATES.items():
    path = os.path.join(BASE, slug, 'index.html')
    with open(path, encoding='utf-8') as f:
        html = f.read()
    new_html, n = SECTION_RE.subn(new_section, html, count=1)
    if n:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(f'  OK  {slug}')
        updated += 1
    else:
        print(f'  !!  {slug} — no related section found')

print(f'\n{updated} files updated.')
