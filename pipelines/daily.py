import time
import random
from datetime import datetime

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
    HEADERS,
    SPREADSHEET_ID,
    SHEET_NAME,
    GOOGLE_CREDENTIALS_FILE,
)


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
    articles = load_articles_from_sitemap()

    if not articles:
        print("No articles found for today.")
        return
    
    # LIMIT FOR TESTING
    articles = articles[:3]
    print("Limit testing 3 articles")

    worksheet = get_worksheet(
        spreadsheet_id=SPREADSHEET_ID,
        worksheet_name=SHEET_NAME,
        credentials_file=GOOGLE_CREDENTIALS_FILE,
    )

    p, browser, page = launch_browser(HEADERS["User-Agent"])
    results = []

    try:
        for i, art in enumerate(articles, 1):
            print(f"[{i}/{len(articles)}] {art['url']}")

            try:
                content, total_pages = extract_article_content(
                    page, art["url"]
                )
            except Exception as e:
                content, total_pages = f"ERROR: {e}", 1

            results.append({
                **art,
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
    )

    print(f"\nUpdated {len(results)} rows to Google Sheets")


if __name__ == "__main__":
    run_daily()
