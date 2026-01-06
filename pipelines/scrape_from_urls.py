from dotenv import load_dotenv
load_dotenv()

import time
import random
from datetime import datetime

from scrapers.tribunnews import extract_article_content
from utilities.playwright_utils import launch_browser
from utilities.sheets import get_worksheet, append_rows
from config.settings import (
    TRIBUN_SOURCES,
    HEADERS,
    SPREADSHEET_ID,
    GOOGLE_CREDENTIALS_FILE,
    FIELDNAMES,
    URL_SHEET_NAME,
)

# =========================
# HELPERS
# =========================

def load_all_urls(worksheet):
    """
    Load all rows from URL sheet as list of dicts
    """
    values = worksheet.get_all_values()
    if not values or len(values) < 2:
        return []

    header = values[0]
    rows = []

    for r in values[1:]:
        if len(r) < len(header):
            continue
        rows.append(dict(zip(header, r)))

    return rows


def get_existing_urls(worksheet):
    """
    Get set of URLs already scraped in destination sheet
    """
    values = worksheet.get_all_values()
    if not values or len(values) < 2:
        return set()

    header = values[0]
    try:
        url_idx = header.index("url")
    except ValueError:
        return set()

    return {
        row[url_idx]
        for row in values[1:]
        if len(row) > url_idx and row[url_idx]
    }


def resolve_day(publication_datetime: str) -> str:
    """
    Convert 'DD/MM/YYYY HH:MM' → weekday name
    """
    if not publication_datetime:
        return ""

    try:
        return datetime.strptime(
            publication_datetime, "%d/%m/%Y %H:%M"
        ).strftime("%A")
    except ValueError:
        return ""


# =========================
# MAIN PIPELINE
# =========================

def run():
    print("🚀 Starting scrape_from_urls pipeline")
    print(f"📅 Run date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # -------------------------
    # Load URL sheet
    # -------------------------
    url_worksheet = get_worksheet(
        SPREADSHEET_ID,
        URL_SHEET_NAME,
        GOOGLE_CREDENTIALS_FILE,
    )

    all_urls = load_all_urls(url_worksheet)
    print(f"🔗 Total URLs in sheet: {len(all_urls)}")

    if not all_urls:
        print("⚠️ No URLs found. Exiting.")
        return

    # -------------------------
    # Prepare destination sheets
    # -------------------------
    dest_sheets = {}
    dest_existing_urls = {}

    for source_key, cfg in TRIBUN_SOURCES.items():
        ws = get_worksheet(
            SPREADSHEET_ID,
            cfg["sheet"],
            GOOGLE_CREDENTIALS_FILE,
        )

        dest_sheets[source_key] = ws
        dest_existing_urls[source_key] = get_existing_urls(ws)

        print(
            f"📄 {cfg['sheet']} → "
            f"{len(dest_existing_urls[source_key])} existing articles"
        )

    # -------------------------
    # Launch browser ONCE
    # -------------------------
    p, browser, page = launch_browser(HEADERS["User-Agent"])

    scraped = 0
    skipped = 0

    try:
        for i, row in enumerate(all_urls, 1):
            source = row.get("source")
            url = row.get("url")

            if not source or not url:
                skipped += 1
                continue

            if source not in dest_sheets:
                skipped += 1
                continue

            if url in dest_existing_urls[source]:
                skipped += 1
                continue

            pub_dt = row.get("publication_datetime")
            day_name = resolve_day(pub_dt)

            print(
                f"\n[{i}/{len(all_urls)}] "
                f"🗓️ [{source}] {pub_dt} | {url}"
            )

            try:
                content, total_pages, tags = extract_article_content(
                    page, url
                )
            except Exception as e:
                print(f"❌ Scrape error: {e}")
                content, total_pages, tags = f"ERROR: {e}", 1, ""

            record = {
                **row,
                "day": day_name,            # 🔥 FIXED
                "tags": tags,
                "total_pages": total_pages,
                "content": content,
            }

            # -------------------------
            # STREAM SAVE (per article)
            # -------------------------
            append_rows(
                worksheet=dest_sheets[source],
                rows=[record],
                header=FIELDNAMES,
                dedup_key="url",
            )

            dest_existing_urls[source].add(url)
            scraped += 1

            print(
                f"✅ Saved [{source}] "
                f"{pub_dt} ({day_name}) | "
                f"{row.get('title', '')[:60]}..."
            )

            time.sleep(random.uniform(5, 7))

    finally:
        browser.close()
        p.stop()

    print("\n🏁 scrape_from_urls finished")
    print(f"🟢 Scraped & saved : {scraped}")
    print(f"🟡 Skipped        : {skipped}")


if __name__ == "__main__":
    run()
