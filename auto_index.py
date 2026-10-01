#!/usr/bin/env python3
"""
Auto-submit changed pages to Google Indexing API.
Runs daily via cron. Detects HTML files modified since last run.
State tracked in .index_state.json (git-ignored).
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("Önce kütüphaneleri kur:")
    print("  pip3 install google-auth google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────

KEY_FILE   = Path.home() / "Downloads/aibot-92369-5069a2de1bb0.json"
PROJECT    = Path(__file__).parent
HTTPDOCS   = PROJECT / "httpdocs"
STATE_FILE = PROJECT / ".index_state.json"
BASE_URL   = "https://www.edualist.com"
DAILY_LIMIT = 195  # buffer below 200/day quota

SCOPES = ["https://www.googleapis.com/auth/indexing"]

# ── State helpers ─────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_run_ts": 0, "submitted": {}}

def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))

# ── Path → URL ────────────────────────────────────────────────────────────────

def html_to_url(path: Path) -> str | None:
    """Convert httpdocs/.../index.html to https://www.edualist.com/.../ """
    try:
        rel = path.relative_to(HTTPDOCS)
    except ValueError:
        return None
    parts = list(rel.parts)
    # drop trailing index.html
    if parts and parts[-1] == "index.html":
        parts = parts[:-1]
    slug = "/".join(parts)
    return f"{BASE_URL}/{slug}/" if slug else f"{BASE_URL}/"

# ── Detect changed files ──────────────────────────────────────────────────────

def find_changed(since_ts: float) -> list[str]:
    """Return URLs for index.html files modified after since_ts."""
    urls = []
    for html in HTTPDOCS.rglob("index.html"):
        if html.stat().st_mtime > since_ts:
            url = html_to_url(html)
            if url:
                urls.append(url)
    # deterministic order, newest first
    urls.sort(key=lambda u: HTTPDOCS.joinpath(
        u.replace(BASE_URL + "/", "").strip("/"), "index.html"
    ).stat().st_mtime if HTTPDOCS.joinpath(
        u.replace(BASE_URL + "/", "").strip("/"), "index.html"
    ).exists() else 0, reverse=True)
    return urls

# ── Submit ────────────────────────────────────────────────────────────────────

def submit_urls(urls: list[str], submitted: dict) -> tuple[int, int]:
    if not KEY_FILE.exists():
        print(f"HATA: JSON key bulunamadı: {KEY_FILE}")
        sys.exit(1)

    credentials = service_account.Credentials.from_service_account_file(
        str(KEY_FILE), scopes=SCOPES
    )
    service = build("indexing", "v3", credentials=credentials)

    ok = fail = 0
    for url in urls:
        try:
            resp = service.urlNotifications().publish(
                body={"url": url, "type": "URL_UPDATED"}
            ).execute()
            notify_time = (resp.get("urlNotificationMetadata", {})
                              .get("latestUpdate", {})
                              .get("notifyTime", "—"))
            print(f"  ✓  {url}  ({notify_time})")
            submitted[url] = datetime.now(timezone.utc).isoformat()
            ok += 1
        except Exception as e:
            print(f"  ✗  {url}  → {e}")
            fail += 1
        time.sleep(0.3)  # stay well under rate limits

    return ok, fail

# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    state = load_state()
    since_ts: float = state["last_run_ts"]
    submitted: dict  = state["submitted"]

    since_dt = datetime.fromtimestamp(since_ts).strftime("%Y-%m-%d %H:%M") if since_ts else "ever"
    print(f"[auto_index] Scanning for changes since {since_dt}...")

    changed = find_changed(since_ts)
    if not changed:
        print("  Değişen sayfa yok, çıkılıyor.")
        state["last_run_ts"] = time.time()
        save_state(state)
        return

    print(f"  {len(changed)} değişen sayfa bulundu.")
    if len(changed) > DAILY_LIMIT:
        print(f"  Günlük limit: ilk {DAILY_LIMIT} sayfa gönderiliyor.")
        changed = changed[:DAILY_LIMIT]

    print(f"\nGoogle Indexing API — {len(changed)} URL gönderiliyor...\n")
    ok, fail = submit_urls(changed, submitted)
    print(f"\n{ok} başarılı, {fail} hatalı / toplam {len(changed)} URL")

    state["last_run_ts"] = time.time()
    state["submitted"]   = submitted
    save_state(state)

if __name__ == "__main__":
    main()
