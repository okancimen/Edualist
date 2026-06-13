#!/usr/bin/env python3
"""Fix blog post meta descriptions over 160 chars + add hero preload to main pages."""
import re, os

BASE = '/Users/okancimen/Edualist/httpdocs/blog'

FIXES = {
    'uluslararasi-okul-mulakatı-nasil-gecilir': (
        'Uluslararası okul mülakatı başarıyla geçmenin sırları. Çocuk mülakatı, ebeveyn görüşmesi, yazılı sınav, mülakat soruları ve hazırlık stratejileri. Özlem Çimen – Edualist.',
        'Uluslararası okul mülakatı nasıl geçilir? Çocuk mülakatı, ebeveyn görüşmesi ve yazılı sınav hazırlığı. Özlem Çimen – Edualist.'
    ),
    'italya-okul-kayit-rehberi': (
        "İtalya'da okul kaydı nasıl yapılır? Scuola elementare, media, liceo seçimi, dil hazırlığı ve başvuru adımları hakkında Türk aileler için kapsamlı rehber. Özlem Çimen – Edualist.",
        "İtalya'da okul kaydı: Scuola elementare'den Liceo'ya sistem, dil hazırlığı ve başvuru adımları. Türk aileler için rehber."
    ),
    'almanya-okul-kayit-rehberi': (
        "Almanya'da okul kaydı nasıl yapılır? Gymnasium, Realschule, uluslararası okul seçimi, dil hazırlığı ve başvuru adımları hakkında Türk aileler için kapsamlı rehber. Özlem Çimen – Edualist.",
        "Almanya'da okul kaydı: Gymnasium, Realschule, dil hazırlığı ve başvuru adımları. Türk aileler için adım adım rehber."
    ),
    'hollanda-okul-kayit-rehberi': (
        "Hollanda'da okul kaydı nasıl yapılır? VWO, HAVO, uluslararası okul seçimi, dil hazırlığı ve başvuru adımları hakkında Türk aileler için kapsamlı rehber. Özlem Çimen – Edualist.",
        "Hollanda'da okul kaydı: VWO, HAVO, VMBO sistemi, ISK programı ve başvuru adımları. Türk aileler için rehber."
    ),
    'kanada-okul-kayit-rehberi': (
        "Kanada'da okul kaydı nasıl yapılır? Ontario, BC, Quebec sistemleri, devlet okulu vs özel okul, İngilizce/Fransızca seçimi. Türk aileler için kapsamlı rehber. Özlem Çimen – Edualist.",
        "Kanada'da okul kaydı: Ontario, BC, Quebec sistemleri, devlet vs özel okul ve dil seçimi. Türk aileler için rehber."
    ),
    'dubai-okul-kayit-rehberi': (
        "Dubai okul kaydı nasıl yapılır? KHDA, başvuru belgeleri, ücretler ve zaman planı. Dubai'de uluslararası okul seçimi için Türk aileler için kapsamlı rehber. Özlem Çimen – Edualist.",
        "Dubai okul kaydı: KHDA sistemi, başvuru belgeleri, ücretler ve zaman planı. Türk aileler için adım adım rehber."
    ),
    'kizim-sinifin-zemininde-yatiyordu': (
        "Singapur'da yanlış uluslararası okul seçiminin gerçek bedeli. 4 yaşındaki kızı sınıfın zemininde bulan Özlem Çimen'den kişisel bir deneyim ve doğru okul seçim rehberi.",
        "Yanlış uluslararası okul seçiminin bedeli. Özlem Çimen'den kişisel bir deneyim: 4 yaşında Singapur, ve doğru okulu bulmanın yolu."
    ),
    'oglumun-ingilizcesi-iyiydi': (
        "Türkiye'de İngilizcesi iyi olan oğlum uluslararası okulda neden üç yıl gerideydi? Özlem Çimen'den kişisel bir deneyim: global İngilizce seviyesi ile Türkiye standardı arasındaki fark.",
        "Türkiye'de 'iyi İngilizce' neden uluslararası okul için yetmez? Özlem Çimen'den EAL ve akademik İngilizce üzerine kişisel bir deneyim."
    ),
    'bae-uluslararasi-okul-rehberi': (
        "BAE'de 1.600'den fazla uluslararası okul var. IB, British, Amerikan ve Fransız müfredatlarını karşılaştır, ücretleri öğren, doğru okulu bul. Özlem Çimen – Edualist.",
        "BAE'de uluslararası okul seçimi: IB, British ve Amerikan müfredatı karşılaştırması, ücretler ve başvuru rehberi."
    ),
    'fransa-okul-kayit-rehberi': (
        "Fransa'da okul kaydı nasıl yapılır? École primaire, collège, lycée seçimi, dil hazırlığı ve başvuru adımları hakkında Türk aileler için kapsamlı rehber. Özlem Çimen – Edualist.",
        "Fransa'da okul kaydı: École, Collège, Lycée sistemi, Baccalauréat ve başvuru adımları. Türk aileler için rehber."
    ),
    'lise-yurt-disi-tasinma-adaptasyon': (
        "Lise çağında yurt dışına taşınmanın sosyal, duygusal ve akademik etkileri. IB ve AP müfredatlarında doğru zamanlama, üniversite yolculuğuna etkileri ve Edualist'in rehberlik yaklaşımı.",
        "Lise döneminde yurt dışına taşınma: sosyal uyum, IB/AP zamanlama ve üniversite başvurularına etkisi. Özlem Çimen rehberi."
    ),
    'yurtdisi-egitim-maliyet-karsilastirma': (
        "Dubai, Londra, Berlin, Paris, Amsterdam ve diğer şehirlerde uluslararası okul ücretleri ve yaşam maliyeti. Gerçekçi rakamlarla ülke ülke maliyet karşılaştırması. Özlem Çimen – Edualist.",
        "Yurt dışı eğitim maliyeti: Dubai, Londra, Berlin, Paris, Amsterdam — gerçekçi rakamlarla ülke ülke karşılaştırma."
    ),
    'dubai-en-iyi-uluslararasi-okullar': (
        "Dubai'de hangi okul gerçekten en iyi? KHDA Outstanding dereceli 23 okulun Türk aileler için değerlendirmesi, müfredat karşılaştırması ve Özlem Çimen'den seçim rehberi.",
        "Dubai'nin en iyi uluslararası okulları: 23 KHDA Outstanding okul, müfredat karşılaştırması ve Türk aileler için seçim rehberi."
    ),
    'ucuncu-kultur-cocugu-tck-rehberi': (
        "Üçüncü kültür çocuğu nedir? Yurt dışında büyüyen çocuklarda kimlik, aidiyet ve Türkçe koruma için kanıtlanmış aile stratejileri. Third Culture Kids (TCK) rehberi – Özlem Çimen, Edualist.",
        "Üçüncü kültür çocuğu (TCK) nedir? Kimlik, aidiyet ve Türkçe koruma için aile stratejileri. Özlem Çimen – Edualist."
    ),
    'ingiltere-okul-kayit-rehberi': (
        "İngiltere'de uluslararası okul kaydı nasıl yapılır? State school, independent school, müfredat seçimi ve başvuru adımları hakkında Türk aileler için kapsamlı rehber. Özlem Çimen – Edualist.",
        "İngiltere'de okul kaydı: state vs independent school, Ofsted, 11+ sınavı ve başvuru adımları. Türk aileler için rehber."
    ),
}

ok = 0
for slug, (old, new) in FIXES.items():
    path = os.path.join(BASE, slug, 'index.html')
    if not os.path.exists(path):
        print(f"NOT FOUND: {slug}")
        continue
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    if old in html:
        html = html.replace(old, new, 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"OK {slug}: {len(old)}→{len(new)} chars")
        ok += 1
    else:
        print(f"NOT MATCHED: {slug}")

print(f"\n{ok}/{len(FIXES)} blog meta descriptions fixed")

# Add preload for hero image on main pages
PRELOAD = '  <link rel="preload" as="image" href="assets/hero-bg.png" fetchpriority="high">\n'
PRELOAD_EN = '  <link rel="preload" as="image" href="../assets/hero-bg.png" fetchpriority="high">\n'

for fpath, preload_tag in [
    ('/Users/okancimen/Edualist/httpdocs/index.html', PRELOAD),
    ('/Users/okancimen/Edualist/httpdocs/tr/index.html', PRELOAD_EN),
    ('/Users/okancimen/Edualist/httpdocs/en/index.html', PRELOAD_EN),
]:
    with open(fpath, 'r', encoding='utf-8') as f:
        html = f.read()
    if 'rel="preload" as="image"' in html:
        print(f"SKIP preload: {fpath.split('httpdocs/')[-1]}")
        continue
    # Insert before </head>
    html = html.replace('<link rel="preconnect" href="https://fonts.googleapis.com">',
                        preload_tag + '  <link rel="preconnect" href="https://fonts.googleapis.com">', 1)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Preload added: {fpath.split('httpdocs/')[-1]}")
