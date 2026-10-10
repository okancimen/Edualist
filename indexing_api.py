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
    # 2026-10-05 kotası dolunca gönderilemeyenler — yarın tekrar dene
    "https://www.edualist.com/blog/dubai-turk-okulu-var-mi/",
    "https://www.edualist.com/blog/farklilastirilmis-ogretim-nedir/",
    "https://www.edualist.com/blog/ib-diploma-universite-basvuru/",
    "https://www.edualist.com/blog/ingiltere-devlet-ozel-okul/",
    "https://www.edualist.com/blog/ispanya-okul-kayit-rehberi/",
    "https://www.edualist.com/blog/kanada-okul-kayit-rehberi/",
    "https://www.edualist.com/blog/katar-okul-kayit-rehberi/",
    "https://www.edualist.com/blog/khda-notu-nedir/",
    "https://www.edualist.com/blog/lise-yurt-disi-tasinma-adaptasyon/",
    "https://www.edualist.com/blog/pisa-2025-turkiye-sonuclari/",
    "https://www.edualist.com/blog/turk-egitim-sisteminden-uluslararasi-okula-gecis/",
    "https://www.edualist.com/blog/turkiye-dubai-okul-ucreti-karsilastirma/",
    "https://www.edualist.com/blog/turkiye-ozel-okuldan-dubai-uluslararasi-okula-gecis/",
    "https://www.edualist.com/blog/turkiye-yilda-46000-cocugunu-yurt-disina-gonderiyor/",
    "https://www.edualist.com/blog/ucuncu-kultur-cocugu-tck-rehberi/",
    "https://www.edualist.com/blog/uluslararasi-okul-mulakat-sorulari/",
    "https://www.edualist.com/blog/uluslararasi-okul-mulakatı-nasil-gecilir/",
    "https://www.edualist.com/blog/yurtdisi-egitim-maliyet-karsilastirma/",
    # Ana sayfalar — 2026-10-05
    "https://www.edualist.com/",
    "https://www.edualist.com/dubai/",
    "https://www.edualist.com/gizlilik-politikasi/",
    "https://www.edualist.com/okul-ucretleri-karsilastirma/",
    "https://www.edualist.com/uluslararasi-akademik-kocluk/",
    "https://www.edualist.com/uluslararasi-okul-danismanligi/",
    "https://www.edualist.com/en/about/",
    "https://www.edualist.com/en/academic-coaching/",
    "https://www.edualist.com/en/dubai/",
    "https://www.edualist.com/en/international-school-consulting/",
    "https://www.edualist.com/en/privacy-policy/",
    "https://www.edualist.com/en/why-edualist/",
    # /en/ blog yazıları — 2026-10-05
    "https://www.edualist.com/en/blog/abu-dhabi-international-schools/",
    "https://www.edualist.com/en/blog/ai-proof-jobs/",
    "https://www.edualist.com/en/blog/anxious-generation-teen-mental-health/",
    "https://www.edualist.com/en/blog/before-moving-to-dubai/",
    "https://www.edualist.com/en/blog/cat4-test-dubai/",
    "https://www.edualist.com/en/blog/child-strengths-and-weaknesses/",
    "https://www.edualist.com/en/blog/dubai-cost-of-living-2026/",
    "https://www.edualist.com/en/blog/dubai-education-system/",
    "https://www.edualist.com/en/blog/dubai-khda-outstanding-schools/",
    "https://www.edualist.com/en/blog/dubai-neighbourhood-school-guide/",
    "https://www.edualist.com/en/blog/dubai-school-fees-2026/",
    "https://www.edualist.com/en/blog/dubai-school-holidays/",
    "https://www.edualist.com/en/blog/dubai-school-registration-season/",
    "https://www.edualist.com/en/blog/dubai-school-registration/",
    "https://www.edualist.com/en/blog/dubai-school-scholarships/",
    "https://www.edualist.com/en/blog/dubai-school-waiting-list/",
    "https://www.edualist.com/en/blog/dubai-top-schools/",
    "https://www.edualist.com/en/blog/eduentry-international-assessment/",
    "https://www.edualist.com/en/blog/future-careers-2030-parent-questions/",
    "https://www.edualist.com/en/blog/future-skills-for-children/",
    "https://www.edualist.com/en/blog/how-to-apply-dubai-school/",
    "https://www.edualist.com/en/blog/how-to-pass-international-school-interview/",
    "https://www.edualist.com/en/blog/ib-diploma-university-requirements/",
    "https://www.edualist.com/en/blog/ib-vs-a-level-vs-ap/",
    "https://www.edualist.com/en/blog/international-education-cost/",
    "https://www.edualist.com/en/blog/international-school-interview-questions/",
    "https://www.edualist.com/en/blog/jobs-of-the-future/",
    "https://www.edualist.com/en/blog/limited-english-child-dubai-school/",
    "https://www.edualist.com/en/blog/pisa-2025-early-work-experience/",
    "https://www.edualist.com/en/blog/pisa-2025-turkey-results/",
    "https://www.edualist.com/en/blog/qatar-international-schools/",
    "https://www.edualist.com/en/blog/robert-kolej-fees-2026/",
    "https://www.edualist.com/en/blog/school-enrolment-canada/",
    "https://www.edualist.com/en/blog/school-enrolment-france/",
    "https://www.edualist.com/en/blog/school-enrolment-germany/",
    "https://www.edualist.com/en/blog/school-enrolment-italy/",
    "https://www.edualist.com/en/blog/school-enrolment-netherlands/",
    "https://www.edualist.com/en/blog/should-my-child-study-abroad/",
    "https://www.edualist.com/en/blog/turkey-46000-children-abroad/",
    "https://www.edualist.com/en/blog/turkey-to-dubai-international-school/",
    "https://www.edualist.com/en/blog/turkey-vs-dubai-school-fees/",
    "https://www.edualist.com/en/blog/turkish-school-in-dubai/",
    "https://www.edualist.com/en/blog/turkish-school-in-germany/",
    "https://www.edualist.com/en/blog/turkish-students-succeeding-in-dubai/",
    "https://www.edualist.com/en/blog/uae-international-school-guide/",
    "https://www.edualist.com/en/blog/uk-school-enrolment/",
    "https://www.edualist.com/en/blog/what-does-an-education-coach-do/",
    "https://www.edualist.com/en/blog/what-is-a-khda-rating/",
    "https://www.edualist.com/en/blog/what-is-an-academic-coach/",
    "https://www.edualist.com/en/blog/what-is-an-international-school/",
    "https://www.edualist.com/en/blog/what-is-eal/",
    "https://www.edualist.com/en/blog/what-is-pisa/",
    "https://www.edualist.com/en/blog/why-high-achievers-struggle-with-ib/",
    "https://www.edualist.com/en/blog/why-turkish-education-falls-short/",
    # Thin content fix batch 2 — 14 sayfa 1200+ kelimeye genişletildi — 2026-10-07
    "https://www.edualist.com/blog/akademik-koc-nedir/",
    "https://www.edualist.com/blog/ib-gecisinde-akademik-kocluk/",
    "https://www.edualist.com/blog/ogretmen-tembel-dedi/",
    "https://www.edualist.com/blog/italya-okul-kayit-rehberi/",
    "https://www.edualist.com/blog/turkiye-ozel-okuldan-dubai-uluslararasi-okula-gecis/",
    "https://www.edualist.com/blog/egitim-kocu-ne-yapar/",
    "https://www.edualist.com/blog/uluslararasi-okul-mulakati-nasil-gecilir/",
    "https://www.edualist.com/en/blog/school-enrolment-italy/",
    "https://www.edualist.com/blog/lgs-surecinde-ders-calis-savaslari/",
    # SEO düzeltmeleri — 2026-10-07
    "https://www.edualist.com/blog/cat4-sinavi-nedir/",
    # Yeni blog yazıları — 2026-10-06
    "https://www.edualist.com/blog/cocugunuzun-gercek-akademik-seviyesi/",
    "https://www.edualist.com/en/blog/childs-real-academic-level/",
    "https://www.edualist.com/blog/dubai-khda-okul-dereceleri-ucret-karsilastirmasi/",
    "https://www.edualist.com/blog/dubai-okul-ucretleri-2026/",
    "https://www.edualist.com/en/blog/dubai-international-schools-khda-fees-2026/",
    # Yeni blog yazıları — 2026-10-09
    "https://www.edualist.com/blog/dubai-ib-okullari-mezun-basarisi/",
    "https://www.edualist.com/en/blog/dubai-ib-schools-graduate-success/",
    "https://www.edualist.com/blog/dubai-ingiliz-okullari-a-level/",
    "https://www.edualist.com/en/blog/dubai-british-schools-a-level/",
    # Yeni blog yazıları — 2026-10-09 (AP okulları)
    "https://www.edualist.com/blog/dubai-amerikan-mufredat-ap-okullari/",
    "https://www.edualist.com/en/blog/best-ap-schools-dubai/",
    # 2026-10-09 — Almanya description CTR fix
    "https://www.edualist.com/blog/almanyada-turk-okulu-var-mi/",
    # 2026-10-09 — blog tag filter + CTR optimizasyonu + hakkimda dateModified fix
    "https://www.edualist.com/blog/",
    "https://www.edualist.com/en/blog/",
    "https://www.edualist.com/blog/cocugunuzun-guclu-yonleri/",
    "https://www.edualist.com/blog/robert-kolej-ucreti-2026/",
    "https://www.edualist.com/hakkimda/",
    # 2026-10-09 — The Anxious Generation Bölüm 2
    "https://www.edualist.com/blog/anxious-generation-oyun-temelli-cocukluk/",
    "https://www.edualist.com/blog/anxious-generation-ergen-ruh-sagligi/",
    # 2026-10-10 — TR differentiators: coaching, homepage, hakkimda, neden-biz
    "https://www.edualist.com/uluslararasi-akademik-kocluk/",
    "https://www.edualist.com/tr/",
    "https://www.edualist.com/hakkimda/",
    "https://www.edualist.com/neden-biz/",
    # 2026-10-10 — cocugunuzun-guclu-yonleri: title/desc CTR fix + eduentry kisilik-degerlendirmesi link
    "https://www.edualist.com/blog/cocugunuzun-guclu-yonleri/",
    # 2026-10-10 — child-strengths-and-weaknesses EN: title/desc CTR fix + personality assessment callout
    "https://www.edualist.com/en/blog/child-strengths-and-weaknesses/",
    # 2026-10-11 — cocugumun-guclu-yonleri: VIA karakter güçlü yönleri yeni blog yazısı
    "https://www.edualist.com/blog/cocugumun-guclu-yonleri/",
    # 2026-10-11 — my-childs-character-strengths: EN version of cocugumun-guclu-yonleri
    "https://www.edualist.com/en/blog/my-childs-character-strengths/",
    # 2026-10-11 — SEO internal links: cocugumun-guclu-yonleri + my-childs-character-strengths
    "https://www.edualist.com/blog/cocugunuzun-guclu-yonleri/",
    "https://www.edualist.com/en/blog/child-strengths-and-weaknesses/",
    "https://www.edualist.com/blog/farklilastirilmis-ogretim-nedir/",
    "https://www.edualist.com/blog/akademik-koc-nedir/",
    "https://www.edualist.com/blog/eduentry-uluslararasi-akademik-degerlendirme-nedir/",
    "https://www.edualist.com/en/blog/what-is-an-academic-coach/",
    "https://www.edualist.com/en/blog/eduentry-international-assessment/",
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
