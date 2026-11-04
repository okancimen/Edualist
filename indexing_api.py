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
    # ── Yeni eklenen / son değişenler — her zaman başta ──────────────────────
    # 2026-11-04 EN version: Hospitality, Tourism & Aviation salaries
    "https://www.edualist.com/en/blog/dubai-hospitality-tourism-aviation-salaries/",
    "https://www.edualist.com/blog/dubai-maaslar-otelcilik-turizm-havayollari/",
    # 2026-11-04 Cross-links: all 3 maaslar posts now fully interlinked (body text + related posts)
    "https://www.edualist.com/blog/dubai-maaslar-2026/",
    "https://www.edualist.com/blog/dubai-maaslar-finans-muhasebe-hukuk/",
    # 2026-11-04 New post: Otelcilik, Turizm ve Havacılık maaşları + blog listing + sitemap
    "https://www.edualist.com/blog/dubai-maaslar-otelcilik-turizm-havayollari/",
    "https://www.edualist.com/blog/",
    # 2026-11-04 EN internal links: hub links to 4 school reviews + IB cross-links
    "https://www.edualist.com/en/blog/gems-founders-school-dubai-review/",
    "https://www.edualist.com/en/blog/gems-jumeirah-primary-school-dubai-review/",
    "https://www.edualist.com/en/blog/jumeirah-college-dubai-review/",
    "https://www.edualist.com/en/blog/safa-community-school-dubai-review/",
    "https://www.edualist.com/en/blog/dubai-ib-school-selection/",
    # 2026-11-04 CTR fixes: "Çocuğumun"→"Çocukların", holiday description improved
    "https://www.edualist.com/blog/cocugunuzun-guclu-yonleri/",
    "https://www.edualist.com/en/blog/dubai-school-holidays/",
    # 2026-11-04 title fix: match exact query "dubai okul başvurusu nasıl yapılır"
    "https://www.edualist.com/blog/dubai-okul-basvuru-nasil-yapilir/",
    # 2026-11-04 CTR: remove jargon from titles, match actual search queries
    "https://www.edualist.com/en/blog/my-childs-character-strengths/",
    "https://www.edualist.com/en/blog/what-is-eal/",
    "https://www.edualist.com/blog/cocugumun-guclu-yonleri/",
    # 2026-11-04 academic coach titles
    "https://www.edualist.com/blog/akademik-koc-nedir/",
    "https://www.edualist.com/blog/egitim-kocu-ne-yapar/",
    # 2026-11-03 restore Oct 27 title damage
    "https://www.edualist.com/blog/dubai-egitim-sistemi/",
    "https://www.edualist.com/blog/dubai-okul-kayit-sezonu-ne-zaman-baslar/",
    "https://www.edualist.com/blog/dubai-yasam-maliyeti-2026/",
    "https://www.edualist.com/en/blog/ib-diploma-university-requirements/",
    "https://www.edualist.com/en/blog/cat4-test-dubai/",
    "https://www.edualist.com/blog/dubai-en-iyi-uluslararasi-okullar/",
    "https://www.edualist.com/en/blog/dubai-top-schools/",
    "https://www.edualist.com/blog/robert-kolej-ucreti-2026/",
    "https://www.edualist.com/dubai/",

    # ── Core site pages ────────────────────────────────────────────────────────
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

    # ── Dubai — cost & lifestyle ───────────────────────────────────────────────
    "https://www.edualist.com/blog/dubai-gelmeden-once-bilmeniz-gerekenler/",
    "https://www.edualist.com/en/blog/before-moving-to-dubai/",
    "https://www.edualist.com/blog/dubai-maaslar-2026/",
    "https://www.edualist.com/en/blog/dubai-salaries-2026/",
    "https://www.edualist.com/blog/dubai-maaslar-finans-muhasebe-hukuk/",
    "https://www.edualist.com/en/blog/dubai-finance-accounting-legal-salaries/",
    "https://www.edualist.com/en/blog/dubai-cost-of-living-2026/",
    "https://www.edualist.com/blog/dubai-semt-rehberi/",
    "https://www.edualist.com/en/blog/dubai-neighbourhood-school-guide/",
    "https://www.edualist.com/blog/turkiye-dubai-okul-ucreti-karsilastirma/",
    "https://www.edualist.com/en/blog/turkey-vs-dubai-school-fees/",

    # ── Dubai — school system & process ───────────────────────────────────────
    "https://www.edualist.com/blog/dubai-okul-ucretleri-2026/",
    "https://www.edualist.com/en/blog/dubai-school-fees-2026/",
    "https://www.edualist.com/blog/dubai-okul-kayit-rehberi/",
    "https://www.edualist.com/en/blog/dubai-school-registration/",
    "https://www.edualist.com/en/blog/dubai-school-registration-season/",
    "https://www.edualist.com/blog/dubai-okul-basvuru-takvimi-2027/",
    "https://www.edualist.com/en/blog/dubai-school-application-timeline-2027/",
    "https://www.edualist.com/en/blog/dubai-school-application-guide/",
    "https://www.edualist.com/en/blog/how-to-apply-dubai-school/",
    "https://www.edualist.com/blog/dubai-okul-bekleme-listesi/",
    "https://www.edualist.com/en/blog/dubai-school-waiting-list/",
    "https://www.edualist.com/blog/dubai-okul-burs-imkanlari/",
    "https://www.edualist.com/en/blog/dubai-school-scholarships/",
    "https://www.edualist.com/blog/dubai-okul-seciminde-5-hata/",
    "https://www.edualist.com/en/blog/dubai-school-selection-mistakes/",
    "https://www.edualist.com/blog/dubai-okul-karsilastirma/",
    "https://www.edualist.com/en/blog/dubai-school-comparison/",
    "https://www.edualist.com/blog/dubai-okul-tatil-tarihleri/",
    "https://www.edualist.com/en/blog/dubai-school-hidden-costs/",
    "https://www.edualist.com/blog/dubai-ozel-okul-mu-devlet-okulu-mu/",
    "https://www.edualist.com/en/blog/dubai-private-vs-government-school/",
    "https://www.edualist.com/en/blog/dubai-education-system/",
    "https://www.edualist.com/blog/khda-notu-nedir/",
    "https://www.edualist.com/en/blog/what-is-a-khda-rating/",
    "https://www.edualist.com/blog/dubai-khda-okul-dereceleri-ucret-karsilastirmasi/",
    "https://www.edualist.com/en/blog/dubai-international-schools-khda-fees-2026/",
    "https://www.edualist.com/en/blog/dubai-khda-outstanding-schools/",
    "https://www.edualist.com/en/blog/dubai-outstanding-schools/",

    # ── Dubai — IB & curriculum ────────────────────────────────────────────────
    "https://www.edualist.com/blog/dubai-ib-okul-secimi/",
    "https://www.edualist.com/en/blog/dubai-ib-school-selection/",
    "https://www.edualist.com/blog/dubai-ib-okullari-mezun-basarisi/",
    "https://www.edualist.com/en/blog/dubai-ib-schools-results/",
    "https://www.edualist.com/en/blog/dubai-ib-schools-graduate-success/",
    "https://www.edualist.com/blog/dubai-ingiliz-okullari-a-level/",
    "https://www.edualist.com/en/blog/dubai-british-schools-a-level/",
    "https://www.edualist.com/blog/dubai-amerikan-mufredat-ap-okullari/",
    "https://www.edualist.com/en/blog/best-ap-schools-dubai/",
    "https://www.edualist.com/blog/ib-alevel-amerikan-mufredat-karsilastirma/",
    "https://www.edualist.com/en/blog/ib-vs-a-level-vs-ap/",
    "https://www.edualist.com/en/blog/ib-vs-a-level-dubai/",
    "https://www.edualist.com/blog/basarili-ogrenciler-ib-de-neden-zorlanir/",
    "https://www.edualist.com/en/blog/why-high-achievers-struggle-with-ib/",
    "https://www.edualist.com/blog/ib-gecisinde-akademik-kocluk/",
    "https://www.edualist.com/en/blog/academic-coaching-for-ib/",
    "https://www.edualist.com/blog/ib-diploma-universite-basvuru/",

    # ── Dubai — top schools & Turkish community ───────────────────────────────
    "https://www.edualist.com/blog/dubai-top-10-okullari/",
    "https://www.edualist.com/en/blog/dubai-top-10-schools/",
    "https://www.edualist.com/blog/dubai-turk-aileler-okul-rehberi/",
    "https://www.edualist.com/blog/dubai-turk-okulu-var-mi/",
    "https://www.edualist.com/en/blog/turkish-school-in-dubai/",
    "https://www.edualist.com/blog/dubai-turk-okulu-arayanlara/",
    "https://www.edualist.com/en/blog/searching-for-turkish-school-dubai/",
    "https://www.edualist.com/blog/dubai-basarili-turk-ogrenciler/",
    "https://www.edualist.com/en/blog/turkish-students-succeeding-in-dubai/",
    "https://www.edualist.com/blog/dubai-lise-secimi/",
    "https://www.edualist.com/en/blog/dubai-secondary-school-guide/",
    "https://www.edualist.com/en/blog/dubai-boarding-schools-guide/",

    # ── School reviews ─────────────────────────────────────────────────────────
    "https://www.edualist.com/blog/repton-school-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/repton-school-dubai-review/",
    "https://www.edualist.com/blog/nord-anglia-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/nord-anglia-dubai-review/",
    "https://www.edualist.com/blog/gems-wellington-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/gems-wellington-dubai-review/",
    "https://www.edualist.com/blog/jess-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/jess-dubai-review/",
    "https://www.edualist.com/blog/kings-school-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/kings-school-dubai-review/",
    "https://www.edualist.com/blog/dubai-college-incelemesi/",
    "https://www.edualist.com/en/blog/dubai-college-review/",
    "https://www.edualist.com/blog/brighton-college-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/brighton-college-dubai-review/",
    "https://www.edualist.com/blog/dubai-british-school-incelemesi/",
    "https://www.edualist.com/en/blog/dubai-british-school-review/",
    "https://www.edualist.com/blog/sunmarke-school-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/sunmarke-school-dubai-review/",
    "https://www.edualist.com/blog/american-school-of-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/american-school-of-dubai-review/",
    "https://www.edualist.com/blog/gems-jumeirah-primary-school-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/gems-jumeirah-primary-school-dubai-review/",
    "https://www.edualist.com/blog/gems-founders-school-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/gems-founders-school-dubai-review/",
    "https://www.edualist.com/blog/jumeirah-college-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/jumeirah-college-dubai-review/",
    "https://www.edualist.com/blog/safa-community-school-dubai-incelemesi/",
    "https://www.edualist.com/en/blog/safa-community-school-dubai-review/",
    "https://www.edualist.com/blog/dubai-international-academy-incelemesi/",
    "https://www.edualist.com/en/blog/dubai-international-academy-review/",
    "https://www.edualist.com/blog/gems-dubai-american-academy-incelemesi/",
    "https://www.edualist.com/en/blog/gems-dubai-american-academy-review/",

    # ── CAT4 & assessment ──────────────────────────────────────────────────────
    "https://www.edualist.com/blog/cat4-sinavi-nedir/",
    "https://www.edualist.com/en/blog/cat4-practice-test-sample-questions/",
    "https://www.edualist.com/blog/cocugunuzun-gercek-akademik-seviyesi/",
    "https://www.edualist.com/en/blog/childs-real-academic-level/",
    "https://www.edualist.com/blog/eduentry-uluslararasi-akademik-degerlendirme-nedir/",
    "https://www.edualist.com/en/blog/eduentry-international-assessment/",

    # ── School interview ───────────────────────────────────────────────────────
    "https://www.edualist.com/blog/uluslararasi-okul-mulakat-sorulari/",
    "https://www.edualist.com/en/blog/international-school-interview-questions/",
    "https://www.edualist.com/blog/uluslararasi-okul-mulakati-nasil-gecilir/",
    "https://www.edualist.com/en/blog/how-to-pass-international-school-interview/",

    # ── Transition to Dubai ────────────────────────────────────────────────────
    "https://www.edualist.com/blog/turkiyeden-dubaya-tasima-cocuk-okul/",
    "https://www.edualist.com/en/blog/turkey-to-dubai-international-school/",
    "https://www.edualist.com/blog/turkiye-ozel-okuldan-dubai-uluslararasi-okula-gecis/",
    "https://www.edualist.com/blog/turk-egitim-sisteminden-uluslararasi-okula-gecis/",
    "https://www.edualist.com/blog/cocugum-okul-degistiriyor/",
    "https://www.edualist.com/blog/cocugum-uluslararasi-okula-geciyor/",
    "https://www.edualist.com/en/blog/child-starting-international-school-dubai/",
    "https://www.edualist.com/blog/ingilizcesi-yetersiz-cocuk-dubai-okulu-uyum/",
    "https://www.edualist.com/en/blog/limited-english-child-dubai-school/",
    "https://www.edualist.com/blog/cocugum-ingilizce-ogrenemiyor/",
    "https://www.edualist.com/blog/eal-nedir/",

    # ── Academic coaching & student support ───────────────────────────────────
    "https://www.edualist.com/blog/ozel-ders-mi-akademik-koc-mu/",
    "https://www.edualist.com/en/blog/tutoring-vs-academic-coaching/",
    "https://www.edualist.com/en/blog/what-is-an-academic-coach/",
    "https://www.edualist.com/en/blog/what-does-an-education-coach-do/",
    "https://www.edualist.com/blog/cocugum-akademik-olarak-geride-kaliyor/",
    "https://www.edualist.com/en/blog/child-falling-behind-at-school/",
    "https://www.edualist.com/blog/dubai-expat-cocuk-akademik-destek/",
    "https://www.edualist.com/en/blog/academic-support-expat-child-dubai/",
    "https://www.edualist.com/en/blog/year-6-to-year-7-transition-dubai/",
    "https://www.edualist.com/blog/cocugum-ozguvensiz-ve-cekingen/",
    "https://www.edualist.com/en/blog/shy-and-insecure-child/",
    "https://www.edualist.com/blog/cocugum-telefona-ekrana-bagimli/",
    "https://www.edualist.com/en/blog/child-screen-phone-addiction/",
    "https://www.edualist.com/blog/cocugum-ders-calismak-istemiyor/",
    "https://www.edualist.com/en/blog/child-wont-study/",
    "https://www.edualist.com/blog/cocugum-sinav-kaygisi-yasiyor/",
    "https://www.edualist.com/en/blog/child-exam-anxiety/",
    "https://www.edualist.com/blog/cocugum-motivasyonunu-kaybetti/",
    "https://www.edualist.com/en/blog/child-lost-motivation/",

    # ── Parent decisions & future ──────────────────────────────────────────────
    "https://www.edualist.com/blog/cocugumu-yurtdisinda-okutmali-miyim/",
    "https://www.edualist.com/en/blog/should-my-child-study-abroad/",
    "https://www.edualist.com/blog/cocugunuz-yurt-disinda-okumaya-hazir-mi/",
    "https://www.edualist.com/blog/yapay-zekaya-direncli-meslekler/",
    "https://www.edualist.com/en/blog/ai-proof-jobs/",
    "https://www.edualist.com/blog/gelecegin-meslekleri-ebeveyn-sorulari/",
    "https://www.edualist.com/en/blog/future-careers-2030-parent-questions/",
    "https://www.edualist.com/blog/yurt-disi-universite-hazirlik-lisede/",
    "https://www.edualist.com/blog/cocugum-ib-ye-basliyor/",
    "https://www.edualist.com/en/blog/international-education-cost/",
    "https://www.edualist.com/blog/yurtdisi-egitim-maliyet-karsilastirma/",

    # ── TCK, teen wellbeing & regional ────────────────────────────────────────
    "https://www.edualist.com/blog/ucuncu-kultur-cocugu-tck-rehberi/",
    "https://www.edualist.com/en/blog/third-culture-kids-guide/",
    "https://www.edualist.com/blog/lise-yurt-disi-tasinma-adaptasyon/",
    "https://www.edualist.com/en/blog/teen-moving-abroad-adjustment/",
    "https://www.edualist.com/blog/anxious-generation-oyun-temelli-cocukluk/",
    "https://www.edualist.com/en/blog/anxious-generation-teen-mental-health/",
    "https://www.edualist.com/blog/abu-dhabi-uluslararasi-okullar/",
    "https://www.edualist.com/en/blog/abu-dhabi-international-schools/",
    "https://www.edualist.com/blog/international-school-nedir/",
    "https://www.edualist.com/en/blog/what-is-an-international-school/",
    "https://www.edualist.com/en/blog/robert-kolej-fees-2026/",
    "https://www.edualist.com/blog/turkiye-egitim-sistemi-neden-yetmiyor/",
    "https://www.edualist.com/en/blog/why-turkish-education-falls-short/",
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
