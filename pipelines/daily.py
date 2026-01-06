from dotenv import load_dotenv
load_dotenv()

import time
import random
from scrapers.tribunnews import (
    load_articles_from_index,
    extract_article_content,
)
from utilities.playwright_utils import launch_browser
from utilities.sheets import get_worksheet, append_rows
from config.settings import (
    HEADERS,
    SPREADSHEET_ID,
    SHEET_NAME,
    GOOGLE_CREDENTIALS_FILE,
    FIELDNAMES,
)

def run_daily():
    articles = load_articles_from_index()
    if not articles:
        print("No articles found.")
        return

    # 🔧 TEMP: limit for testing
    articles = articles[:3]
    print("🧪 Test mode: limit to 3 articles")

    worksheet = get_worksheet(
        SPREADSHEET_ID,
        SHEET_NAME,
        GOOGLE_CREDENTIALS_FILE,
    )

    p, browser, page = launch_browser(HEADERS["User-Agent"])
    results = []

    try:
        for i, art in enumerate(articles, 1):
            print(f"[{i}/{len(articles)}] {art['url']}")

            try:
                content, total_pages, tags = extract_article_content(
                    page, art["url"]
                )
            except Exception as e:
                content, total_pages, tags = f"ERROR: {e}", 1, ""

            results.append({
                **art,
                "tags": tags,
                "total_pages": total_pages,
                "content": content,
            })

            time.sleep(random.uniform(5, 7))

    finally:
        browser.close()
        p.stop()

    append_rows(
        worksheet=worksheet,
        rows=results,
        header=FIELDNAMES,
        dedup_key="url",
    )

    print(f"✅ Uploaded {len(results)} rows")

if __name__ == "__main__":
    run_daily()
