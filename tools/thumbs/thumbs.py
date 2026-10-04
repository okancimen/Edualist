"""Blog thumbnail data + HTML template (rendered to 800x450 and 640x360 WebP by render.js).

Style matches the existing assets/blog thumbnails: navy background with stars,
gold accents, white + gold two-line title, kicker and footer band.

To add a thumbnail: add the post to THUMBS, then
  python3 tools/thumbs/thumbs.py /tmp/thumbs && node tools/thumbs/render.js /tmp/thumbs
  convert /tmp/thumbs/thumb-<slug>.png -quality 82 httpdocs/assets/blog/thumb-<slug>.webp
  convert /tmp/thumbs/thumb-<slug>.png -resize 640x360 -quality 82 httpdocs/assets/blog/thumb-<slug>-640.webp
"""
import html
import random

# slug -> (kicker, title line 1, title line 2 (gold), subtitle, icon)
THUMBS = {
    'akademik-koc-nedir': ('AKADEMİK KOÇLUK', 'Akademik Koç', 'Nedir?', 'Özel öğretmenden farkı ve ne zaman gerekir', 'bulb'),
    'cocugum-akademik-olarak-geride-kaliyor': ('ÇOCUĞUM · AKADEMİK', 'Derslerde', 'Geride Kalıyor', 'Önce sebebi bulun: yöntem, seviye, motivasyon', 'chart_down'),
    'cocugum-ders-calismak-istemiyor': ('ÇOCUĞUM · ÇALIŞMA', 'Ders Çalışmak', 'İstemiyor', 'Sorun tembellik değil: asıl sebep', 'books'),
    'cocugum-ib-ye-basliyor': ('ÇOCUĞUM · IB', "IB'ye", 'Başlıyor', 'İlk yıl rehberi: EE, TOK ve CAS', 'cap'),
    'cocugum-ingilizce-ogrenemıyor': ('ÇOCUĞUM · DİL', 'İngilizce', 'Öğrenemiyor', 'Yöntem mi, motivasyon mu, seviye mi?', 'bubble'),
    'cocugum-motivasyonunu-kaybetti': ('ÇOCUĞUM · MOTİVASYON', 'Motivasyonunu', 'Kaybetti', 'Neden olur, nasıl geri gelir?', 'battery'),
    'cocugum-okul-degistiriyor': ('ÇOCUĞUM · GEÇİŞ', 'Okul', 'Değiştiriyor', 'Geçiş döneminde aile rehberi', 'arrows'),
    'cocugum-sinav-kaygisi-yasiyor': ('ÇOCUĞUM · SINAV', 'Sınav', 'Kaygısı', 'Anlamak ve yönetmek için rehber', 'heart'),
    'cocugum-uluslararasi-okula-geciyor': ('ULUSLARARASI OKUL', 'Geçişte', '5 Kritik Hata', 'Ailelerin en sık yaptığı hatalar', 'warning'),
    'dubai-ib-okul-secimi': ('DUBAİ · IB', "Dubai'de", 'IB Okulu Seçimi', 'DIA, GEMS World Academy, Nord Anglia', 'cap'),
    'dubai-ozel-okul-mu-devlet-okulu-mu': ('DUBAİ · OKUL TÜRÜ', 'Özel mi,', 'Devlet mi?', 'Expat aileler için gerçekler', 'scale'),
    'dubai-turk-aileler-okul-rehberi': ('DUBAİ · TÜRK AİLELER', 'Türk Aileler', 'İçin Okul Rehberi', 'Müfredat, Türkçe ve topluluk', 'home'),
    'egitim-kocu-ne-yapar': ('AKADEMİK KOÇLUK', 'Eğitim Koçu', 'Ne Yapar?', 'Özel öğretmen mi, koç mu?', 'compass'),
    'farklilastirilmis-ogretim-nedir': ('ÖĞRENME', 'Farklılaştırılmış', 'Öğretim', 'Her çocuk aynı yöntemle öğrenemez', 'puzzle'),
    'ogretmen-tembel-dedi': ('BİR ANNENİN HİKÂYESİ', 'Öğretmeni', '"Tembel" Dedi', 'Aslında öğrenme biçimi farklıydı', 'quote'),
    'ozel-ders-mi-akademik-koc-mu': ('KARAR REHBERİ', 'Özel Ders mi,', 'Akademik Koç mu?', 'Hangisi ne zaman işe yarar?', 'scale'),
    'turkiyeden-dubaya-tasima-cocuk-okul': ('TÜRKİYE → DUBAİ', 'Taşınırken', 'Okul Geçişi', 'Taşınma ve okul takvimi', 'plane'),
    'cat4-sinavi-nedir': ('DUBAİ · SINAV', 'CAT4 Sınavı', 'Nedir?', '4 bölüm, puanlar ve hazırlık', 'grid'),
    'cocuklar-icin-gelecek-becerileri': ('WEF · BIG 4', 'Geleceğin', '4 Kritik Becerisi', "Çocuğunuzu 2030'a hazırlayın", 'target'),
    'dubai-okul-bekleme-listesi': ('DUBAİ · KAYIT', 'Bekleme', 'Listesi', 'Ne zaman ve nasıl başvurmalı?', 'hourglass'),
    'yurt-disi-universite-hazirlik-lisede': ('ÜNİVERSİTE', 'Yurt Dışı Üniversite', 'Lisede Başlar', '9–12. sınıf yol haritası', 'cap'),
    'cocugunuzun-guclu-yonleri': ('ÇOCUK GELİŞİMİ', 'Çocuğun', 'Güçlü Yönleri', '30 örnek ve akademik profil', 'star'),
    'dubai-okul-ucretleri-2026': ('DUBAİ · 2026–27', 'Dubai Okul', 'Ücretleri', 'KHDA ve müfredata göre fiyat tablosu', 'coins'),
    'gelecegin-meslekleri-ebeveyn-sorulari': ('KARİYER · 2030', 'Geleceğin', 'Meslekleri', 'Ebeveynlerin 8 sorusu, net yanıtlar', 'briefcase'),
    'khda-notu-nedir': ('DUBAİ · KHDA', 'KHDA Notu', 'Nedir?', 'Outstanding, Very Good, Good farkı', 'medal'),
    'yapay-zekaya-direncli-meslekler': ('YAPAY ZEKA', 'Yapay Zekadan', 'Etkilenmeyen 65 Meslek', 'Çocuğunuz için kariyer rehberi', 'chip'),
    'basarili-ogrenciler-ib-de-neden-zorlanir': ('IB · AKADEMİK KOÇLUK', 'Başarılı Çocuk', "IB'de Neden Zorlanır?", 'Extended Essay, TOK ve zaman yönetimi', 'books'),
    'ib-diploma-universite-basvuru': ('IB DIPLOMA', 'Üniversite İçin', 'Ülke Ülke Puanlar', 'Oxbridge, Russell Group, ABD, YÖK', 'globe'),
    'ib-gecisinde-akademik-kocluk': ('IB · GEÇİŞ', "IB'de", 'İlk 3 Ay', 'Akademik koçluk neden kritik?', 'calendar'),
    'dubai-expat-cocuk-akademik-destek': ('DUBAİ · EXPAT', 'Expat Çocuklar', 'İçin Akademik Destek', 'Uyum ve akademik koçluk rehberi', 'bulb'),
    'eal-nedir': ('DİL DESTEĞİ', 'EAL', 'Nedir?', 'English as an Additional Language', 'bubble'),
    'lgs-surecinde-ders-calis-savaslari': ('LGS', '"Ders Çalış"', 'Kavgasını Bitirin', '3 pratik adım', 'books'),
    'pisa-2025-turkiye-sonuclari': ('PISA 2025', 'Türkiye', 'Sonuçları', 'Rakamların arkasında ne var?', 'chart'),
    'almanyada-turk-okulu-var-mi': ('ALMANYA', "Almanya'da", 'Türk Okulu Var mı?', 'Maarif, konsolosluk kursları ve seçenekler', 'pin'),
    'katar-okul-kayit-rehberi': ('KATAR · DOHA', "Katar'da", 'Okul Kaydı 2026', "Doha'da uluslararası okullar", 'pin'),
    'universitede-fark-yaratan-aktiviteler': ('ÜNİVERSİTE BAŞVURUSU', 'Fark Yaratan', 'Aktiviteler', 'Derinlik mi, genişlik mi?', 'star'),
    'lise-ogrencisi-yaz-programlari': ('LİSE · YAZ', 'Doğru Yaz', 'Programını Seçmek', 'Başvuruya katkı sağlayan 3 kriter', 'sun'),
    'dubai-okul-kayit-sezonu-ne-zaman-baslar': ('DUBAİ · TAKVİM', 'Kayıt Sezonu', '2026–2027', 'Ay ay başvuru planı', 'calendar'),
    'pisa-2025-erken-is-deneyimi': ('PISA 2025', 'Erken İş', 'Deneyimi', 'Türk öğrenciler için eksik halka', 'briefcase'),
    'robert-kolej-ucreti-2026': ('ÖZEL OKUL · 2026–27', 'Robert Koleji', 'Ücreti', '2.488.200 TL ve 15 okul karşılaştırması', 'coins'),
    'turkiye-ozel-okuldan-dubai-uluslararasi-okula-gecis': ('TÜRKİYE → DUBAİ', 'Okul Geçişi:', 'Belgeler ve CAT4', 'Apostil, onay zinciri ve mülakat', 'document'),
    'dubai-top-schools': ('DUBAI · 2026', 'Top 10 Schools', 'in Dubai', 'KHDA Outstanding picks for expat families', 'medal'),
    'lise-ogrencisi-staj-is-deneyimi': ('LİSE · KARİYER', 'Lisede', 'İş Deneyimi', 'Üniversiteye fark yaratan 5 yol', 'briefcase'),
}

G = '#DBAF2E'
ICONS = {
    'bulb': '<path d="M100 40a42 42 0 0 0-24 76c6 5 8 11 8 18h32c0-7 2-13 8-18a42 42 0 0 0-24-76z"/><path d="M84 150h32M88 166h24"/><path d="M100 82v30M90 96l10-14 10 14"/>',
    'chart_down': '<path d="M40 160h120M40 160V40"/><rect x="56" y="70" width="18" height="90"/><rect x="86" y="96" width="18" height="64"/><rect x="116" y="124" width="18" height="36"/><path d="M60 52l40 34 30 20 24 14"/><path d="M146 108l10 14-16 2"/>',
    'books': '<rect x="40" y="70" width="28" height="94" rx="3"/><rect x="72" y="50" width="30" height="114" rx="3"/><rect x="106" y="62" width="26" height="102" rx="3"/><path d="M136 74l22-8 22 96-22 6z"/><path d="M80 70h14M80 144h14"/>',
    'cap': '<path d="M20 86l80-36 80 36-80 36z"/><path d="M52 100v34c0 12 22 22 48 22s48-10 48-22v-34"/><path d="M180 86v44"/><circle cx="180" cy="136" r="5"/>',
    'bubble': '<path d="M36 50h128a12 12 0 0 1 12 12v62a12 12 0 0 1-12 12H90l-30 26v-26H36a12 12 0 0 1-12-12V62a12 12 0 0 1 12-12z"/><text x="100" y="106" text-anchor="middle" font-family="Liberation Serif" font-weight="700" font-size="34" fill="#DBAF2E" stroke="none">ABC</text>',
    'battery': '<rect x="30" y="66" width="128" height="68" rx="8"/><path d="M158 88h12v24h-12"/><rect x="42" y="78" width="22" height="44" fill="#DBAF2E"/><path d="M104 74l-14 28h20l-14 28" stroke-width="5"/>',
    'arrows': '<path d="M36 76h104"/><path d="M122 58l22 18-22 18"/><path d="M164 128H60"/><path d="M78 110l-22 18 22 18"/>',
    'heart': '<path d="M100 168s-64-38-64-84a34 34 0 0 1 64-16 34 34 0 0 1 64 16c0 46-64 84-64 84z"/><path d="M52 104h26l10-20 14 40 12-24h34"/>',
    'warning': '<path d="M100 34l74 128H26z"/><path d="M100 82v40" stroke-width="7"/><circle cx="100" cy="140" r="5" fill="#DBAF2E"/>',
    'scale': '<path d="M100 40v120M60 160h80M44 62h112"/><path d="M44 62l-22 50h44zM156 62l-22 50h44z"/><path d="M22 112a22 10 0 0 0 44 0M134 112a22 10 0 0 0 44 0"/>',
    'home': '<path d="M30 98l70-58 70 58"/><path d="M48 86v76h104V86"/><rect x="86" y="118" width="28" height="44"/><path d="M100 70a10 10 0 1 1 0 .1"/>',
    'compass': '<circle cx="100" cy="100" r="66"/><path d="M128 72l-18 42-38 14 18-42z"/><circle cx="100" cy="100" r="5" fill="#DBAF2E"/><path d="M100 26v12M100 162v12M26 100h12M162 100h12"/>',
    'puzzle': '<path d="M40 60h36a14 14 0 1 1 28 0h36v36a14 14 0 1 0 0 28v36h-36a14 14 0 1 1-28 0H40v-36a14 14 0 1 0 0-28z"/>',
    'quote': '<path d="M52 128c0-34 10-54 36-66M110 128c0-34 10-54 36-66"/><circle cx="66" cy="130" r="16"/><circle cx="124" cy="130" r="16"/>',
    'plane': '<path d="M30 112l140-52-40 100-30-38-38 16z"/><path d="M100 122l70-62"/><path d="M28 160c30 10 70 10 100-6" stroke-dasharray="6 8"/>',
    'grid': '<rect x="40" y="40" width="54" height="54" rx="6"/><rect x="106" y="40" width="54" height="54" rx="6"/><rect x="40" y="106" width="54" height="54" rx="6"/><rect x="106" y="106" width="54" height="54" rx="6"/><text x="67" y="77" text-anchor="middle" font-family="Liberation Sans" font-size="20" fill="#DBAF2E" stroke="none">V</text><text x="133" y="77" text-anchor="middle" font-family="Liberation Sans" font-size="20" fill="#DBAF2E" stroke="none">Q</text><text x="67" y="143" text-anchor="middle" font-family="Liberation Sans" font-size="20" fill="#DBAF2E" stroke="none">NV</text><text x="133" y="143" text-anchor="middle" font-family="Liberation Sans" font-size="20" fill="#DBAF2E" stroke="none">S</text>',
    'target': '<circle cx="96" cy="104" r="64"/><circle cx="96" cy="104" r="40"/><circle cx="96" cy="104" r="16"/><path d="M96 104l70-70M148 34h18v18"/>',
    'hourglass': '<path d="M56 36h88M56 164h88"/><path d="M66 36c0 46 68 46 68 64s-68 18-68 64M134 36c0 46-68 46-68 64s68 18 68 64"/><path d="M84 150h32l-16-18z" fill="#DBAF2E"/>',
    'star': '<path d="M100 30l20 44 48 5-36 32 10 47-42-24-42 24 10-47-36-32 48-5z"/>',
    'coins': '<ellipse cx="80" cy="140" rx="46" ry="14"/><path d="M34 140v-20c0 8 20 14 46 14s46-6 46-14v20"/><ellipse cx="80" cy="120" rx="46" ry="14"/><ellipse cx="124" cy="80" rx="42" ry="14"/><path d="M82 80v-22c0 8 18 14 42 14s42-6 42-14v22c0 8-18 14-42 14"/><ellipse cx="124" cy="58" rx="42" ry="14"/>',
    'briefcase': '<rect x="30" y="66" width="140" height="94" rx="10"/><path d="M76 66V50a8 8 0 0 1 8-8h32a8 8 0 0 1 8 8v16"/><path d="M30 104h140"/><rect x="88" y="94" width="24" height="20" rx="3"/>',
    'medal': '<path d="M70 30l22 50M130 30l-22 50"/><circle cx="100" cy="122" r="42"/><path d="M100 98l9 18 20 3-14 14 3 20-18-9-18 9 3-20-14-14 20-3z"/>',
    'chip': '<rect x="56" y="56" width="88" height="88" rx="10"/><rect x="78" y="78" width="44" height="44" rx="4"/><path d="M76 40v16M100 40v16M124 40v16M76 144v16M100 144v16M124 144v16M40 76h16M40 100h16M40 124h16M144 76h16M144 100h16M144 124h16"/>',
    'globe': '<circle cx="100" cy="100" r="68"/><ellipse cx="100" cy="100" rx="30" ry="68"/><path d="M32 100h136M44 64h112M44 136h112"/>',
    'calendar': '<rect x="36" y="50" width="128" height="112" rx="10"/><path d="M36 82h128M70 36v28M130 36v28"/><path d="M60 104h16M92 104h16M124 104h16M60 132h16M92 132h16" stroke-width="6"/><circle cx="132" cy="132" r="10" fill="#DBAF2E"/>',
    'pin': '<path d="M100 172s-52-56-52-92a52 52 0 0 1 104 0c0 36-52 92-52 92z"/><circle cx="100" cy="80" r="18"/>',
    'sun': '<circle cx="100" cy="100" r="34"/><path d="M100 30v20M100 150v20M30 100h20M150 100h20M50 50l14 14M136 136l14 14M150 50l-14 14M64 136l-14 14"/>',
    'chart': '<path d="M40 160h124M40 160V40"/><rect x="56" y="110" width="20" height="50"/><rect x="86" y="84" width="20" height="76"/><rect x="116" y="60" width="20" height="100" fill="#DBAF2E"/><path d="M58 92l34-26 30-18 30-12"/>',
    'document': '<path d="M52 30h70l30 30v110H52z"/><path d="M122 30v30h30"/><path d="M70 84h64M70 104h64M70 124h40"/><circle cx="128" cy="148" r="16"/><path d="M120 148l6 6 10-12"/>',
}


def stars(seed, n=55):
    rnd = random.Random(seed)
    return ''.join(f'<circle cx="{rnd.uniform(0, 800):.0f}" cy="{rnd.uniform(0, 410):.0f}" r="{rnd.choice([0.8, 1, 1.2, 1.6])}" '
                   f'fill="{rnd.choice(["#ffffff", "#ffffff", G])}" opacity="{rnd.uniform(.25, .7):.2f}"/>' for _ in range(n))


def page(slug):
    k, l1, l2, sub, icon = THUMBS[slug]
    e = html.escape
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:800px;height:450px;overflow:hidden}}
.wrap{{position:relative;width:800px;height:450px;background:linear-gradient(160deg,#0f2a49 0%,#0b213a 60%,#081a2e 100%);font-family:'Liberation Sans',sans-serif}}
svg.bg{{position:absolute;inset:0}}
.icon{{position:absolute;left:62px;top:105px;width:200px;height:200px}}
.icon svg{{width:200px;height:200px;fill:none;stroke:{G};stroke-width:4;stroke-linecap:round;stroke-linejoin:round}}
.rule{{position:absolute;left:312px;top:96px;width:2px;height:218px;background:{G};opacity:.9}}
.text{{position:absolute;left:340px;top:0;width:430px;height:410px;display:flex;flex-direction:column;justify-content:center}}
.k{{color:{G};font-size:14px;letter-spacing:2.5px;font-weight:700;margin-bottom:14px}}
.t{{font-family:'Liberation Serif',serif;font-weight:700;line-height:1.08;white-space:nowrap}}
.t1{{color:#fff}} .t2{{color:{G}}}
.s{{color:#d7dee8;font-size:17px;margin-top:16px;line-height:1.35}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:40px;background:#071729;border-top:2px solid {G};color:{G};font-size:13px;font-weight:700;letter-spacing:2px;display:flex;align-items:center;justify-content:center}}
.top{{position:absolute;left:0;right:0;top:0;height:6px;background:{G}}}
</style></head><body><div class="wrap">
<svg class="bg" width="800" height="450">{stars(slug)}</svg>
<div class="top"></div>
<div class="icon"><svg viewBox="0 0 200 200">{ICONS[icon]}</svg></div>
<div class="rule"></div>
<div class="text"><div class="k">{e(k)}</div><div class="t t1">{e(l1)}</div><div class="t t2">{e(l2)}</div><div class="s">{e(sub)}</div></div>
<div class="foot">EDUALIST · {e(k)}</div>
</div>
<script>
  // shrink the title until both lines fit the text column
  let fs = 50; const ts = [...document.querySelectorAll('.t')];
  const fits = () => ts.every(t => t.scrollWidth <= 430);
  do {{ ts.forEach(t => t.style.fontSize = fs + 'px'); fs -= 1; }} while (!fits() && fs > 26);
</script></body></html>'''


def asset_name(slug):
    return 'thumb-' + slug.replace('ı', 'i')


if __name__ == '__main__':
    import json
    import os
    import sys
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    jobs = []
    for slug in THUMBS:
        f = os.path.join(out, asset_name(slug) + '.html')
        open(f, 'w', encoding='utf-8').write(page(slug))
        jobs.append({'html': f, 'name': asset_name(slug)})
    json.dump(jobs, open(os.path.join(out, 'jobs.json'), 'w'))
    print(len(jobs), 'pages')
