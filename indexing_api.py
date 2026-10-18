#!/usr/bin/env python3
"""
Google Indexing API + IndexNow — URL submit script
Kullanım: python3 indexing_api.py
"""

import json
import sys
import urllib.request
from pathlib import Path

try:
    import google.auth
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("Önce kütüphaneleri kur:")
    print("  pip3 install google-auth google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# ── Ayarlar ───────────────────────────────────────────────────────────────────

KEY_FILE = Path.home() / "Downloads/aibot-92369-5069a2de1bb0.json"

INDEXNOW_KEY      = "5017990445f8bb07d511f1beeadb647d"
INDEXNOW_HOST     = "www.edualist.com"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

URLS = [
    # 2026-10-19 GSC crawled-not-indexed fix — Oct 7'den beri recrawl yok; Oct 12-15 güncellemeleri görmedi
    "https://www.edualist.com/blog/hollanda-okul-kayit-rehberi/",
    "https://www.edualist.com/en/blog/school-enrolment-netherlands/",
    # 2026-10-19 GSC redirect error fix — .htaccess Oct 16'dan beri 1-hop; yeniden crawl zorunlu
    "https://edualist.com/uluslararasi-akademik-kocluk/index.html",
    "https://edualist.com/blog/",
    "https://edualist.com/blog/ib-diploma-universite-basvuru/",
    "https://edualist.com/blog/turkiye-dubai-okul-ucreti-karsilastirma",
    # 2026-10-19 sitemap'e eklenen 3 yeni yazı
    "https://www.edualist.com/sitemap.xml",
    # 2026-10-19 yeni yazı: dubai-okul-seciminde-5-hata + görseller
    "https://www.edualist.com/blog/dubai-okul-seciminde-5-hata/",
    # 2026-10-18 yeni yazı: dubai-okul-basvuru-takvimi-2027 + inbound link güncellemeleri
    "https://www.edualist.com/blog/dubai-okul-basvuru-takvimi-2027/",
    "https://www.edualist.com/blog/dubai-okul-kayit-rehberi/",
    "https://www.edualist.com/blog/dubai-okul-kayit-sezonu-ne-zaman-baslar/",
    "https://www.edualist.com/blog/",
    "https://www.edualist.com/llms.txt",
    "https://www.edualist.com/llms-full.txt",
    # 2026-10-18 meta/H1 fixes — title trimmed, desc trimmed, H1 spacing fixed
    "https://www.edualist.com/blog/dubai-ingiliz-okullari-a-level/",
    "https://www.edualist.com/blog/khda-notu-nedir/",
    "https://www.edualist.com/blog/ib-diploma-universite-basvuru/",
    "https://www.edualist.com/blog/basarili-ogrenciler-ib-de-neden-zorlanir/",
    "https://www.edualist.com/blog/cocugum-ozguvensiz-ve-cekingen/",
    "https://www.edualist.com/blog/egitim-kocu-ne-yapar/",
    "https://www.edualist.com/blog/dubai-okul-karsilastirma/",
    "https://www.edualist.com/blog/dubai-semt-rehberi/",
    "https://www.edualist.com/blog/kizim-sinifin-zemininde-yatiyordu/",
    "https://www.edualist.com/blog/lgs-surecinde-ders-calis-savaslari/",
    # 2026-10-18 inbound link additions — 1-3 view blog posts boosted via cluster box edits
    "https://www.edualist.com/blog/dubai-top-10-okullari/",
    "https://www.edualist.com/blog/dubai-ib-okullari-mezun-basarisi/",
    "https://www.edualist.com/blog/dubai-gelmeden-once-bilmeniz-gerekenler/",
    "https://www.edualist.com/blog/dubai-okul-karsilastirma/",
    "https://www.edualist.com/blog/dubai-semt-rehberi/",
    "https://www.edualist.com/blog/cocugumun-guclu-yonleri/",
    "https://www.edualist.com/blog/cocugum-ozguvensiz-ve-cekingen/",
    "https://www.edualist.com/blog/cocugum-telefona-ekrana-bagimli/",
    # 2026-10-18 source pages updated (cluster boxes)
    "https://www.edualist.com/blog/dubai-egitim-sistemi/",
    "https://www.edualist.com/blog/dubai-en-iyi-uluslararasi-okullar/",
    "https://www.edualist.com/blog/dubai-okul-kayit-rehberi/",
    "https://www.edualist.com/blog/ib-alevel-amerikan-mufredat-karsilastirma/",
    "https://www.edualist.com/blog/dubai-okul-ucretleri-2026/",
    "https://www.edualist.com/blog/cocugunuzun-guclu-yonleri/",
    "https://www.edualist.com/blog/anxious-generation-oyun-temelli-cocukluk/",
    # 2026-10-17 new post: Repton vs GEMS vs Nord Anglia vs JESS comparison + inbound link updates
    "https://www.edualist.com/blog/dubai-okul-karsilastirma/",
    "https://www.edualist.com/blog/dubai-en-iyi-uluslararasi-okullar/",
    "https://www.edualist.com/blog/dubai-turk-aileler-okul-rehberi/",
    # 2026-10-17 content fixes: school-holidays date table moved up, cocugunuzun-guclu-yonleri coaching CTA, dubai-semt-rehberi tables, khda-outstanding HTML fix
    "https://www.edualist.com/en/blog/dubai-school-holidays/",
    "https://www.edualist.com/blog/cocugunuzun-guclu-yonleri/",
    "https://www.edualist.com/blog/dubai-semt-rehberi/",
    "https://www.edualist.com/en/blog/dubai-khda-outstanding-schools/",
    # 2026-10-17 PageSpeed fix — GTM load trigger (182 pages) + carousel reflow + non-composited animations (styles.css)
    "https://www.edualist.com/tr/",
    "https://www.edualist.com/en/",
    # 2026-10-17 EN translations (3 posts) + TR hreflang updates
    "https://www.edualist.com/en/blog/tutoring-vs-academic-coaching/",
    "https://www.edualist.com/en/blog/academic-coaching-for-ib/",
    "https://www.edualist.com/en/blog/child-falling-behind-at-school/",
    "https://www.edualist.com/blog/ozel-ders-mi-akademik-koc-mu/",
    "https://www.edualist.com/blog/ib-gecisinde-akademik-kocluk/",
    "https://www.edualist.com/blog/cocugum-akademik-olarak-geride-kaliyor/",
    # 2026-10-16 GSC coverage fix — redirect/404 sorunu olan URL'lerin hedefleri + düzeltilen sayfa
    "https://www.edualist.com/blog/uluslararasi-okul-mulakati-nasil-gecilir/",  # 404 (mülakatı) → doğru slug
    "https://www.edualist.com/en/blog/what-is-pisa/",                           # /blog/what-is-pisa/ redirect hedefi
    "https://www.edualist.com/blog/dubai-gelmeden-once-bilmeniz-gerekenler/",   # /blog/dubai-school-guide/ redirect hedefi
    "https://www.edualist.com/blog/ucuncu-kultur-cocugu-tck-rehberi/",          # /index.html suffix redirect hedefi
    "https://www.edualist.com/blog/ib-diploma-universite-basvuru/",             # redirect error hedefi
    "https://www.edualist.com/blog/turkiye-dubai-okul-ucreti-karsilastirma/",   # no-trailing-slash redirect hedefi
    "https://www.edualist.com/uluslararasi-akademik-kocluk/",                   # /index.html redirect hedefi
    # 2026-10-16 EduBot widget eklendi
    "https://www.edualist.com/blog/ib-alevel-amerikan-mufredat-karsilastirma/",
    "https://www.edualist.com/blog/dubai-egitim-sistemi/",
    # 2026-10-15 SEO: servis sayfalarına blog küme bölümü + dubai-top-10-okullari yeni yazı
    "https://www.edualist.com/blog/dubai-top-10-okullari/",
    "https://www.edualist.com/en/blog/dubai-top-schools/",
    "https://www.edualist.com/uluslararasi-okul-danismanligi/",
    "https://www.edualist.com/uluslararasi-akademik-kocluk/",
    "https://www.edualist.com/sitemap.xml",
    # 2026-10-15 GSC "Discovered - not indexed" (N/A last crawled) — crawl önceliği artırıldı
    "https://www.edualist.com/blog/cocugunuzun-gercek-akademik-seviyesi/",
    "https://www.edualist.com/blog/dubai-expat-cocuk-akademik-destek/",
    "https://www.edualist.com/en/blog/dubai-school-fees-2026/",
    "https://www.edualist.com/gizlilik-politikasi/",
    # 2026-10-15 Footer: badge sayısı, bio metni, CTA etiketleri tüm sayfalarda güncellendi
    "https://www.edualist.com/blog/dubai-ingiliz-okullari-a-level/",
    "https://www.edualist.com/en/blog/dubai-british-schools-a-level/",
    "https://www.edualist.com/en/blog/best-ap-schools-dubai/",
    "https://www.edualist.com/en/blog/dubai-international-schools-khda-fees-2026/",
    "https://www.edualist.com/en/blog/dubai-ib-schools-graduate-success/",
    "https://www.edualist.com/en/blog/childs-real-academic-level/",
    # 2026-10-15 İspanya — içerik önemli ölçüde zenginleştirildi (GSC not-indexed sorunu)
    "https://www.edualist.com/blog/ispanya-okul-kayit-rehberi/",
    # 2026-10-15 Dubai A-Level sayfalarına iç bağlantı eklendi (GSC not-indexed sorunu)
    "https://www.edualist.com/blog/dubai-ingiliz-okullari-a-level/",
    "https://www.edualist.com/en/blog/dubai-british-schools-a-level/",
    # 2026-10-15 iç bağlantı güncellenen kaynak sayfalar (TR)
    "https://www.edualist.com/blog/dubai-en-iyi-uluslararasi-okullar/",
    "https://www.edualist.com/blog/dubai-egitim-sistemi/",
    "https://www.edualist.com/blog/dubai-amerikan-mufredat-ap-okullari/",
    "https://www.edualist.com/blog/dubai-ib-okul-secimi/",
    "https://www.edualist.com/blog/dubai-ozel-okul-mu-devlet-okulu-mu/",
    # 2026-10-15 iç bağlantı güncellenen kaynak sayfalar (EN)
    "https://www.edualist.com/en/blog/dubai-top-schools/",
    "https://www.edualist.com/en/blog/dubai-international-schools-khda-fees-2026/",
    "https://www.edualist.com/en/blog/dubai-education-system/",
    # 2026-10-15 sitemap güncellendi (Holland EN lastmod düzeltmesi)
    "https://www.edualist.com/sitemap.xml",
    # 2026-10-15 testimonial carousel hizalama düzeltmesi (ana sayfalar)
    "https://www.edualist.com/tr/",
    "https://www.edualist.com/en/",
    # 2026-10-14 yeni EN çevirileri (5 yazı — en yüksek öncelik)
    "https://www.edualist.com/en/blog/child-wont-study/",
    "https://www.edualist.com/en/blog/child-exam-anxiety/",
    "https://www.edualist.com/en/blog/child-lost-motivation/",
    "https://www.edualist.com/en/blog/third-culture-kids-guide/",
    "https://www.edualist.com/en/blog/teen-moving-abroad-adjustment/",
    # 2026-10-14 iç bağlantı/hreflang güncellenen sayfalar
    "https://www.edualist.com/en/blog/anxious-generation-teen-mental-health/",
    "https://www.edualist.com/en/blog/",
    "https://www.edualist.com/blog/cocugum-ders-calismak-istemiyor/",
    "https://www.edualist.com/blog/cocugum-sinav-kaygisi-yasiyor/",
    "https://www.edualist.com/blog/cocugum-motivasyonunu-kaybetti/",
    "https://www.edualist.com/blog/ucuncu-kultur-cocugu-tck-rehberi/",
    "https://www.edualist.com/blog/lise-yurt-disi-tasinma-adaptasyon/",
    # 2026-10-14 title/meta kısaltılan yazılar
    "https://www.edualist.com/blog/cocugum-ozguvensiz-ve-cekingen/",
    "https://www.edualist.com/blog/cocugum-telefona-ekrana-bagimli/",
    "https://www.edualist.com/en/blog/shy-and-insecure-child/",
    "https://www.edualist.com/en/blog/child-screen-phone-addiction/",
]

# ──────────────────────────────────────────────────────────────────────────────

SCOPES = ["https://www.googleapis.com/auth/indexing"]

def submit_urls(urls: list[str], key_file: Path) -> None:
    if not key_file.exists():
        print(f"HATA: JSON key dosyası bulunamadı: {key_file}")
        print("Doğru yolu KEY_FILE değişkenine gir.")
        sys.exit(1)

    credentials = service_account.Credentials.from_service_account_file(
        str(key_file), scopes=SCOPES
    )
    service = build("indexing", "v3", credentials=credentials)

    ok, fail = 0, 0
    for url in urls:
        try:
            body = {"url": url, "type": "URL_UPDATED"}
            response = service.urlNotifications().publish(body=body).execute()
            notify_time = response.get("urlNotificationMetadata", {}) \
                                  .get("latestUpdate", {}) \
                                  .get("notifyTime", "—")
            print(f"  ✓  {url}  ({notify_time})")
            ok += 1
        except Exception as e:
            print(f"  ✗  {url}  → {e}")
            fail += 1

    print(f"\n{ok} başarılı, {fail} hatalı / toplam {len(urls)} URL")

def submit_indexnow(urls: list[str]) -> None:
    payload = json.dumps({
        "host": INDEXNOW_HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://{INDEXNOW_HOST}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }).encode()
    req = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"  IndexNow → HTTP {resp.status} ({len(urls)} URL)")
    except urllib.error.HTTPError as e:
        print(f"  IndexNow HATA → HTTP {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"  IndexNow HATA → {e}")


if __name__ == "__main__":
    print(f"Google Indexing API — {len(URLS)} URL gönderiliyor...\n")
    submit_urls(URLS, KEY_FILE)

    print(f"\nIndexNow — {len(URLS)} URL gönderiliyor...")
    submit_indexnow(URLS)
