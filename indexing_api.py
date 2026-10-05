#!/usr/bin/env python3
"""
Google Indexing API — URL submit script
Kullanım: python3 indexing_api.py
"""

import json
import sys
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

URLS = [
    # Yeni ve değiştirilen sayfalar — 2026-10-02
    "https://www.edualist.com/cocugunuzun-potansiyeli/",
    # Hub backlink + first-person title updates
    "https://www.edualist.com/blog/basarili-ogrenciler-ib-de-neden-zorlanir/",
    "https://www.edualist.com/blog/eduentry-uluslararasi-akademik-degerlendirme-nedir/",
    "https://www.edualist.com/blog/akademik-koc-nedir/",
    "https://www.edualist.com/blog/anxious-generation-ergen-ruh-sagligi/",
    "https://www.edualist.com/blog/cat4-sinavi-nedir/",
    "https://www.edualist.com/blog/cocuklar-icin-gelecek-becerileri/",
    "https://www.edualist.com/blog/dubai-expat-cocuk-akademik-destek/",
    "https://www.edualist.com/blog/egitim-kocu-ne-yapar/",
    "https://www.edualist.com/blog/gelecekte-hangi-meslekler-onem-kazanacak/",
    "https://www.edualist.com/blog/ib-alevel-amerikan-mufredat-karsilastirma/",
    "https://www.edualist.com/blog/ib-gecisinde-akademik-kocluk/",
    "https://www.edualist.com/blog/kizim-sinifin-zemininde-yatiyordu/",
    "https://www.edualist.com/blog/lgs-surecinde-ders-calis-savaslari/",
    "https://www.edualist.com/blog/lise-ogrencisi-staj-is-deneyimi/",
    "https://www.edualist.com/blog/lise-ogrencisi-yaz-programlari/",
    "https://www.edualist.com/blog/oglumun-ingilizcesi-iyiydi/",
    "https://www.edualist.com/blog/pisa-2025-erken-is-deneyimi/",
    "https://www.edualist.com/blog/pisa-nedir/",
    "https://www.edualist.com/blog/turkiye-egitim-sistemi-neden-yetmiyor/",
    "https://www.edualist.com/blog/universitede-fark-yaratan-aktiviteler/",
    "https://www.edualist.com/blog/yapay-zekaya-direncli-meslekler/",
    "https://www.edualist.com/blog/yurt-disi-universite-hazirlik-lisede/",
    # Yeni hikaye yazıları
    "https://www.edualist.com/blog/cocugum-ders-calismak-istemiyor/",
    "https://www.edualist.com/blog/ogretmen-tembel-dedi/",
    # Yeni ne-yapmalıyım + karşılaştırma yazıları 2026-10-03
    "https://www.edualist.com/blog/cocugum-uluslararasi-okula-geciyor/",
    "https://www.edualist.com/blog/ozel-ders-mi-akademik-koc-mu/",
    "https://www.edualist.com/blog/cocugum-ib-ye-basliyor/",
    "https://www.edualist.com/blog/cocugum-akademik-olarak-geride-kaliyor/",
    # Yeni ne-yapmalıyım yazıları 2026-10-05
    "https://www.edualist.com/blog/cocugum-motivasyonunu-kaybetti/",
    "https://www.edualist.com/blog/cocugum-sinav-kaygisi-yasiyor/",
    "https://www.edualist.com/blog/cocugum-okul-degistiriyor/",
    "https://www.edualist.com/blog/cocugum-ingilizce-ogrenemıyor/",
    # Yeni Dubai + geçiş rehberleri 2026-10-08
    "https://www.edualist.com/blog/dubai-ib-okul-secimi/",
    "https://www.edualist.com/blog/turkiyeden-dubaya-tasima-cocuk-okul/",
    "https://www.edualist.com/blog/dubai-ozel-okul-mu-devlet-okulu-mu/",
    "https://www.edualist.com/blog/dubai-turk-aileler-okul-rehberi/",
    # Genişletilen yazılar + EN body + SearchAction
    "https://www.edualist.com/blog/dubai-okul-ucretleri-2026/",
    "https://www.edualist.com/blog/dubai-yasam-maliyeti-2026/",
    "https://www.edualist.com/blog/international-school-nedir/",
    "https://www.edualist.com/blog/dubai-en-iyi-uluslararasi-okullar/",
    "https://www.edualist.com/blog/akademik-koc-nedir/",
    "https://www.edualist.com/tr/",
    "https://www.edualist.com/en/",
    # IB düzeltmesi — 2026-10-04
    "https://www.edualist.com/blog/robert-kolej-ucreti-2026/",
    # Geleceğin meslekleri ebeveyn Q&A — 2026-10-04
    "https://www.edualist.com/blog/gelecegin-meslekleri-ebeveyn-sorulari/",
    # Hakkımda + Neden Biz IICS düzeltmesi — 2026-10-05
    "https://www.edualist.com/hakkimda/",
    "https://www.edualist.com/neden-biz/",
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

if __name__ == "__main__":
    print(f"Google Indexing API — {len(URLS)} URL gönderiliyor...\n")
    submit_urls(URLS, KEY_FILE)
