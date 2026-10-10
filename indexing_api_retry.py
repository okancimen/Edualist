#!/usr/bin/env python3
"""
Günlük 200 URL limitini aşan URL'ler için retry scripti.
Kullanım: python3 indexing_api_retry.py
"""

import json
import sys
import urllib.request
from pathlib import Path

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("pip3 install google-auth google-auth-httplib2 google-api-python-client")
    sys.exit(1)

KEY_FILE = Path.home() / "Downloads/aibot-92369-5069a2de1bb0.json"
INDEXNOW_KEY      = "5017990445f8bb07d511f1beeadb647d"
INDEXNOW_HOST     = "www.edualist.com"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
SCOPES = ["https://www.googleapis.com/auth/indexing"]

# 2026-10-09 quota aşımından kalan 6 URL
RETRY_URLS = [
    "https://www.edualist.com/en/blog/dubai-ib-schools-graduate-success/",
    "https://www.edualist.com/blog/dubai-amerikan-mufredat-ap-okullari/",
    "https://www.edualist.com/blog/",
    "https://www.edualist.com/en/blog/",
    "https://www.edualist.com/blog/cocugunuzun-guclu-yonleri/",
    "https://www.edualist.com/hakkimda/",
]

def submit_urls(urls, key_file):
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

def submit_indexnow(urls):
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
    print(f"Google Indexing API — {len(RETRY_URLS)} URL gönderiliyor...\n")
    submit_urls(RETRY_URLS, KEY_FILE)
    print(f"\nIndexNow — {len(RETRY_URLS)} URL gönderiliyor...")
    submit_indexnow(RETRY_URLS)
