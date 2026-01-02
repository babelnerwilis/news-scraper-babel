import time
import random

from scrapers.tribunnews import (
    load_sitemap_articles,
    extract_article_content
)
from utilities.playwright_utils import get_page
from utilities.sheets import (
    get_worksheet,
    get_existing_urls,
    append_row
)
from config.settings import (
    SPREADSHEET_NAME,
    WORKSHEET_NAME,
    CRAWL_DELAY
)

def run():
    ws = get_worksheet(SPREADSHEET_NAME, WORKSHEET_NAME)
    existing_urls = get_existing_urls(ws)

    articles = load_sitemap_articles()
    if not articles:
        print("No new articles found.")
        return

    p, browser, page = get_page()

    try:
        for i, art in enumerate(articles, 1):
            if art["url"] in existing_urls:
                continue

            print(f"[{i}/{len(articles)}] {art['url']}")

            try:
                content, total_pages = extract_article_content(page, art["url"])
            except Exception as e:
                content, total_pages = f"ERROR: {e}", 1

            append_row(ws, {
                **art,
                "total_pages": total_pages,
                "content": content
            })

            time.sleep(CRAWL_DELAY)
            MIN_DELAY = CRAWL_DELAY - 1
            MAX_DELAY = CRAWL_DELAY + 1
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    finally:
        browser.close()
        p.stop()

