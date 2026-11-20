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
INDEXNOW_ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
    "https://yandex.com/indexnow",
]

URLS = [
    # Kasım 2026 — TR yapay-zekaya-direncli-meslekler: tam 65 meslek tablosu eklendi
    "https://www.edualist.com/blog/yapay-zekaya-direncli-meslekler/",
    # Kasım 2026 — 7 EN çevirisi
    "https://www.edualist.com/en/blog/my-child-cant-learn-english/",
    "https://www.edualist.com/en/blog/my-child-is-changing-schools/",
    "https://www.edualist.com/en/blog/is-your-child-ready-for-international-school/",
    "https://www.edualist.com/en/blog/turkish-families-dubai-school-guide/",
    "https://www.edualist.com/en/blog/my-sons-english-was-good-enough/",
    "https://www.edualist.com/en/blog/extracurricular-activities-university-application/",
    "https://www.edualist.com/en/blog/international-university-preparation-high-school/",
    # ── Yeni eklenen / son değişenler — BURAYA EKLE, en fazla ~150 URL ──────────
    # Kural: yeni veya güncellenen sayfaları üste ekle; eski sabit sayfaları silme.
    # Quota: 200/gün — bu listenin her zaman 150'nin altında kalmasını sağla.

    # Kasım 2026 — İç link eklendi: dubai-gcse-nedir + fransa bounce fix (3 inline link)
    "https://www.edualist.com/blog/dubai-gcse-nedir/",
    "https://www.edualist.com/blog/dubai-ingiliz-okullari-a-level/",
    "https://www.edualist.com/blog/dubai-en-iyi-uluslararasi-okullar/",
    "https://www.edualist.com/blog/dubai-top-10-okullari/",
    "https://www.edualist.com/blog/fransa-okul-kayit-rehberi/",

    # Kasım 2026 — Yeni post: Dubai okul kaydı belgeleri rehberi (apostil, TC, Emirates ID, KHDA sözleşmesi)
    "https://www.edualist.com/blog/dubai-okul-kaydi-apostil-rehberi/",
    "https://www.edualist.com/en/blog/dubai-school-enrollment-documents-guide/",

    # Kasım 2026 — 6 yeni okul incelemesi (DESS/DESC, GEMS World Academy, Raffles World Academy)
    "https://www.edualist.com/blog/dess-desc-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/dess-desc-dubai-review/",
    "https://www.edualist.com/blog/gems-world-academy-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/gems-world-academy-dubai-review/",
    "https://www.edualist.com/blog/raffles-world-academy-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/raffles-world-academy-dubai-review/",

    # Nov 2026 — GSC "Discovered not indexed" push: 11 EN blog pages never crawled
    "https://www.edualist.com/en/blog/academic-support-expat-child-dubai/",
    "https://www.edualist.com/en/blog/cat4-practice-test-sample-questions/",
    "https://www.edualist.com/en/blog/child-starting-international-school-dubai/",
    "https://www.edualist.com/en/blog/dubai-school-application-timeline-2027/",
    "https://www.edualist.com/en/blog/dubai-school-comparison/",
    "https://www.edualist.com/en/blog/dubai-school-hidden-costs/",
    "https://www.edualist.com/en/blog/dubai-school-selection-mistakes/",
    "https://www.edualist.com/en/blog/dubai-secondary-school-guide/",
    "https://www.edualist.com/en/blog/gems-founders-school-dubai-review/",
    "https://www.edualist.com/en/blog/searching-for-turkish-school-dubai/",
    "https://www.edualist.com/en/blog/year-6-to-year-7-transition-dubai/",

    # Nov 2026 — SEO CTR fix: title/meta/OG/twitter updated for 7 high-impression low-CTR pages
    "https://www.edualist.com/en/blog/dubai-school-holidays/",
    "https://www.edualist.com/blog/robert-kolej-ucreti-2026/",
    "https://www.edualist.com/en/blog/cat4-test-dubai/",
    "https://www.edualist.com/blog/international-school-nedir/",
    "https://www.edualist.com/en/blog/what-is-eal/",
    "https://www.edualist.com/en/blog/ib-diploma-university-requirements/",
    "https://www.edualist.com/en/blog/repton-school-dubai-review/",

    # Nov 2026 — Grup 2 visibility fix: title/meta/OG/content update for 10 low-ranking pages
    "https://www.edualist.com/blog/pisa-2025-turkiye-sonuclari/",
    "https://www.edualist.com/blog/pisa-2025-erken-is-deneyimi/",
    "https://www.edualist.com/blog/cocugum-ib-ye-basliyor/",
    "https://www.edualist.com/blog/cocuklar-icin-gelecek-becerileri/",
    "https://www.edualist.com/blog/gems-jumeirah-primary-school-dubai-incelemesi/",
    "https://www.edualist.com/blog/nord-anglia-dubai-incelemesi/",
    "https://www.edualist.com/blog/dubai-ilkokul-ortaokul-gecisi/",
    "https://www.edualist.com/blog/dubai-okul-karsilastirma/",
    "https://www.edualist.com/blog/cocugum-uluslararasi-okula-geciyor/",
    "https://www.edualist.com/blog/dubai-international-academy-incelemesi/",

    # Nov 2026 — New post: Abu Dhabi okul ücretleri 2026-2027 (Top 15 ADEK guide)
    "https://www.edualist.com/blog/abu-dhabi-okul-ucretleri-2026-2027/",

    # Nov 2026 — CTR fix: 5 blog title/meta/OG update (GSC CTR 0% despite impressions)
    "https://www.edualist.com/blog/dubai-turk-aileler-okul-rehberi/",
    "https://www.edualist.com/blog/oglumun-ingilizcesi-iyiydi/",
    "https://www.edualist.com/blog/turkiyeden-dubaya-tasima-cocuk-okul/",
    "https://www.edualist.com/blog/dubai-gelmeden-once-bilmeniz-gerekenler/",
    "https://www.edualist.com/blog/lgs-surecinde-ders-calis-savaslari/",

    # Nov 2026 — CTR fix: eal-nedir + ib-vs-a-level-vs-ap title/meta updates
    "https://www.edualist.com/blog/eal-nedir/",
    "https://www.edualist.com/en/blog/ib-vs-a-level-vs-ap/",

    # Nov 2026 — Internal linking: related-section cluster fix + 96 pages with new in-text links
    # CAT4 + child academic support cluster (related sections restructured)
    "https://www.edualist.com/blog/cat4-sinavi-nedir/",
    "https://www.edualist.com/blog/cat4-ornek-sorular/",
    "https://www.edualist.com/blog/cocugum-sinav-kaygisi-yasiyor/",
    "https://www.edualist.com/blog/dubai-expat-cocuk-akademik-destek/",
    "https://www.edualist.com/blog/cocugum-ingilizce-ogrenemiyor/",
    "https://www.edualist.com/blog/oglumun-ingilizcesi-iyiydi/",
    # High-traffic pages that gained new in-text links
    "https://www.edualist.com/blog/dubai-top-10-okullari/",
    "https://www.edualist.com/blog/dubai-ib-okullari-mezun-basarisi/",
    "https://www.edualist.com/blog/dubai-en-iyi-uluslararasi-okullar/",
    "https://www.edualist.com/blog/dubai-okul-ucretleri-2026/",
    "https://www.edualist.com/blog/dubai-ilkokul-ortaokul-gecisi/",
    "https://www.edualist.com/blog/cocugunuzun-gercek-akademik-seviyesi/",
    "https://www.edualist.com/blog/dubai-okul-kayit-rehberi/",
    "https://www.edualist.com/blog/dubai-turk-aileler-okul-rehberi/",
    "https://www.edualist.com/blog/international-school-nedir/",
    "https://www.edualist.com/blog/eal-nedir/",

    # Nov 2026 — GSC 404 fix destinations (re-crawl after redirect rules deployed)
    "https://www.edualist.com/blog/ingilizcesi-yetersiz-cocuk-dubai-okulu-uyum/",
    "https://www.edualist.com/en/blog/ib-vs-a-level-vs-ap/",
    "https://www.edualist.com/en/blog/dubai-khda-outstanding-schools/",

    # Nov 2026 — 3 new EN pages + cross-link updates on 3 EN salary pages
    "https://www.edualist.com/en/blog/dubai-healthcare-salaries/",
    "https://www.edualist.com/en/blog/dubai-construction-architecture-salaries/",
    "https://www.edualist.com/en/blog/dubai-vs-abu-dhabi-cost-of-living/",

    "https://www.edualist.com/blog/dubai-gcse-nedir/",

    # Nov 2026 — CTR fixes + content upgrades (page-2 push campaign)
    "https://www.edualist.com/en/blog/ib-diploma-university-requirements/",
    "https://www.edualist.com/en/blog/ai-proof-jobs/",
    "https://www.edualist.com/blog/international-school-nedir/",
    "https://www.edualist.com/en/blog/dubai-british-schools-a-level/",
    "https://www.edualist.com/en/blog/dubai-school-holidays/",
    "https://www.edualist.com/blog/cocugunuzun-guclu-yonleri/",
    "https://www.edualist.com/blog/robert-kolej-ucreti-2026/",
    "https://www.edualist.com/en/blog/cat4-test-dubai/",
    "https://www.edualist.com/blog/dubai-egitim-sistemi/",
    "https://www.edualist.com/en/blog/my-childs-character-strengths/",
    "https://www.edualist.com/blog/dubai-yasam-maliyeti-2026/",

    "https://www.edualist.com/blog/dubai-mi-abu-dhabi-mi-yasam-maliyeti/",
    "https://www.edualist.com/blog/dubai-en-iyi-uluslararasi-okullar/",
    "https://www.edualist.com/en/blog/dubai-international-schools-khda-fees-2026/",
    "https://www.edualist.com/blog/dubai-british-school-incelemesi/",
    "https://www.edualist.com/blog/brighton-college-dubai-incelemesi/",
    "https://www.edualist.com/blog/sunmarke-school-dubai-incelemesi/",
    "https://www.edualist.com/blog/jumeirah-college-dubai-incelemesi/",
    "https://www.edualist.com/blog/dubai-expat-cocuk-akademik-destek/",
    "https://www.edualist.com/blog/turkiye-dubai-okul-ucreti-karsilastirma/",
    "https://www.edualist.com/en/blog/dubai-education-system/",
    "https://www.edualist.com/blog/ib-gecisinde-akademik-kocluk/",
    "https://www.edualist.com/blog/turkiye-ozel-okuldan-dubai-uluslararasi-okula-gecis/",
    "https://www.edualist.com/blog/dubai-okul-yil-grubu-kayit-yasi/",
    "https://www.edualist.com/en/blog/dubai-school-year-groups/",
    "https://www.edualist.com/blog/cocugunuzun-gercek-akademik-seviyesi/",
    "https://www.edualist.com/en/blog/childs-real-academic-level/",
    "https://www.edualist.com/blog/dubai-okul-tatil-tarihleri/",
    "https://www.edualist.com/blog/cat4-ornek-sorular/",
    "https://www.edualist.com/blog/dubai-okul-gizli-maliyetler/",
    "https://www.edualist.com/blog/dubai-ilkokul-ortaokul-gecisi/",
    "https://www.edualist.com/blog/dubai-yatili-okul-rehberi/",
    "https://www.edualist.com/blog/dubai-ib-okul-secimi/",
    "https://www.edualist.com/en/blog/dubai-ib-school-selection/",
    "https://www.edualist.com/blog/dubai-ib-okullari-mezun-basarisi/",
    "https://www.edualist.com/en/blog/dubai-ib-schools-results/",
    "https://www.edualist.com/en/blog/dubai-ib-schools-graduate-success/",
    "https://www.edualist.com/blog/dubai-maaslar-2026/",
    "https://www.edualist.com/en/blog/dubai-salaries-2026/",
    "https://www.edualist.com/blog/dubai-maaslar-finans-muhasebe-hukuk/",
    "https://www.edualist.com/en/blog/dubai-finance-accounting-legal-salaries/",
    "https://www.edualist.com/blog/dubai-maaslar-otelcilik-turizm-havayollari/",
    "https://www.edualist.com/en/blog/dubai-hospitality-tourism-aviation-salaries/",
    "https://www.edualist.com/blog/dubai-maaslar-saglik/",
    "https://www.edualist.com/blog/dubai-maaslar-insaat-mimarlik/",

    # ── Core site pages (service pages + listings — always keep) ─────────────
    "https://www.edualist.com/dubai/",
    "https://www.edualist.com/tr/",
    "https://www.edualist.com/en/",
    "https://www.edualist.com/blog/",
    "https://www.edualist.com/en/blog/",
    "https://www.edualist.com/en/dubai/",
    "https://www.edualist.com/en/dubai-schools/",
    "https://www.edualist.com/uluslararasi-okul-danismanligi/",
    "https://www.edualist.com/en/international-school-consulting/",
    "https://www.edualist.com/en/school-advisory/",
    "https://www.edualist.com/uluslararasi-akademik-kocluk/",
    "https://www.edualist.com/en/academic-coaching/",
    "https://www.edualist.com/hakkimda/",
    "https://www.edualist.com/neden-biz/",
    "https://www.edualist.com/en/about/",
    "https://www.edualist.com/en/why-edualist/",
    "https://www.edualist.com/cocugunuzun-potansiyeli/",
    "https://www.edualist.com/en/your-childs-potential/",
    "https://www.edualist.com/okul-ucretleri-karsilastirma/",
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
    for endpoint in INDEXNOW_ENDPOINTS:
        name = endpoint.split("/")[2]
        # Yandex rejects non-HTML URLs (e.g. .txt files)
        batch = [u for u in urls if not u.endswith(".txt")] if "yandex" in endpoint else urls
        payload = json.dumps({
            "host": INDEXNOW_HOST,
            "key": INDEXNOW_KEY,
            "keyLocation": f"https://{INDEXNOW_HOST}/{INDEXNOW_KEY}.txt",
            "urlList": batch,
        }).encode()
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                print(f"  IndexNow [{name}] → HTTP {resp.status} ({len(batch)} URL)")
        except urllib.error.HTTPError as e:
            print(f"  IndexNow [{name}] HATA → HTTP {e.code}: {e.read().decode()}")
        except Exception as e:
            print(f"  IndexNow [{name}] HATA → {e}")


if __name__ == "__main__":
    print(f"Google Indexing API — {len(URLS)} URL gönderiliyor...\n")
    submit_urls(URLS, KEY_FILE)

    print(f"\nIndexNow — {len(URLS)} URL gönderiliyor...")
    submit_indexnow(URLS)
