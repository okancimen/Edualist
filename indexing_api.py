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
    # ── Yeni eklenen / son değişenler — BURAYA EKLE, en fazla ~150 URL ──────────
    # Kural: yeni veya güncellenen sayfaları üste ekle; eski sabit sayfaları silme.
    # Quota: 200/gün — bu listenin her zaman 150'nin altında kalmasını sağla.

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
