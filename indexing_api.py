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
