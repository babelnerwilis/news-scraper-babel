import time
import random

from scrapers.tribunnews import (
    load_articles_from_sitemap,
    extract_article_content,
)

from utilities.playwright_utils import launch_browser
from utilities.sheets import (
    get_worksheet,
    append_rows,
)

from config.settings import (
    SPREADSHEET_ID,
    SHEET_NAME,
    GOOGLE_CREDENTIALS_FILE,
    MIN_DELAY,
    MAX_DELAY,
)

# =========================
# COLUMN ORDER (GOOGLE SHEET)
# =========================
FIELDNAMES = [
    "day",
    "publication_datetime",
    "source",
    "title",
    "url",
    "tags",
    "total_pages",
    "content",
]


def run_daily():
    print("🚀 Starting daily scraper")

    # =========================
    # 1. Launch Playwright browser
    # =========================
    p, browser, page = launch_browser()

    try:
        # =========================
        # 2. Load sitemap via browser
        # =========================
        articles = load_articles_from_sitemap(page)

        if not articles:
            print("⚠️ No articles found for date range.")
            return

        # 🔧 TEMP: limit for testing
        articles = articles[:3]
        print("🧪 Test mode: limit to 3 articles")

        # =========================
        # 3. Prepare Google Sheet
        # =========================
        worksheet = get_worksheet(
            spreadsheet_id=SPREADSHEET_ID,
            worksheet_name=SHEET_NAME,
            credentials_file=GOOGLE_CREDENTIALS_FILE,
        )

        results = []

        # =========================
        # 4. Scrape article contents
        # =========================
        for i, art in enumerate(articles, 1):
            print(f"[{i}/{len(articles)}] {art['url']}")

            try:
                content, total_pages = extract_article_content(
                    page,
                    art["url"]
                )
            except Exception as e:
                print("⚠️ Article error:", e)
                content = f"ERROR: {e}"
                total_pages = 1

            results.append({
                **art,
                "total_pages": total_pages,
                "content": content,
            })

            # Polite delay
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

        # =========================
        # 5. Save results
        # =========================
        append_rows(
            worksheet=worksheet,
            rows=results,
            header=FIELDNAMES,
        )

        print(f"✅ Updated {len(results)} rows in Google Sheets")

    finally:
        browser.close()
        p.stop()
        print("🧹 Browser closed")


if __name__ == "__main__":
    run_daily()
