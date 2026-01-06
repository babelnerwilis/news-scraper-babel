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
    TRIBUN_SOURCES,
    HEADERS,
    SPREADSHEET_ID,
    # SHEET_NAME,
    GOOGLE_CREDENTIALS_FILE,
    FIELDNAMES,
    URL_FIELDNAMES, 
    URL_SHEET_NAME
)

import os
import sys
import platform

# print("=== DEBUG ENV ===")
# print("CWD:", os.getcwd())
# print("Python:", sys.version)
# print("Platform:", platform.platform())
# print("TZ:", os.environ.get("TZ"))
# print("=================")

def run_daily():
    p, browser, page = launch_browser(HEADERS["User-Agent"])

    try:
        for source_key, cfg in TRIBUN_SOURCES.items():
            print(f"\n🚀 Processing source: {cfg['label']}")

            worksheet = get_worksheet(
                SPREADSHEET_ID,
                cfg["sheet"],
                GOOGLE_CREDENTIALS_FILE,
            )

            existing_urls = set(
                worksheet.col_values(FIELDNAMES.index("url") + 1)[1:]
            )

            articles = load_articles_from_index(
                index_base_url=cfg["base_url"],
                source_key=source_key,
                existing_urls=existing_urls,
            )

            # 🔴 LIMIT PER SOURCE (testing mode)
            # articles = articles[:1]
            # print(f"🧪 Test mode: limiting to {len(articles)} articles for {source_key}")
            
            if not articles:
                print("No articles found.")
                continue

            
            # =========================
            # SAVE COLLECTED URLS
            # =========================
            url_worksheet = get_worksheet(
                SPREADSHEET_ID,
                URL_SHEET_NAME,
                GOOGLE_CREDENTIALS_FILE,
            )

            append_rows(
                worksheet=url_worksheet,
                rows=articles,          # already contains url + metadata
                header=URL_FIELDNAMES,
                dedup_key="url",
            )

            print(f"🔗 Saved {len(articles)} URLs to {URL_SHEET_NAME}")

            results = []

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

            append_rows(
                worksheet=worksheet,
                rows=results,
                header=FIELDNAMES,
                dedup_key="url",
            )

            print(f"✅ Uploaded {len(results)} rows for {source_key}")

    finally:
        browser.close()
        p.stop()


# def run_daily():
#     worksheet = get_worksheet(
#         SPREADSHEET_ID,
#         SHEET_NAME,
#         GOOGLE_CREDENTIALS_FILE,
#     )

#     # 🔹 EARLY DEDUP SOURCE
#     existing_urls = set(
#         worksheet.col_values(FIELDNAMES.index("url") + 1)[1:]
#     )

#     # articles = load_articles_from_index()
#     articles = load_articles_from_index(existing_urls=existing_urls)

#     if not articles:
#         print("No articles found.")
#         return

#     # TEMP: limit for testing
#     # articles = articles[:3]
#     # print("Test mode: limit to 3 articles")

#     worksheet = get_worksheet(
#         SPREADSHEET_ID,
#         SHEET_NAME,
#         GOOGLE_CREDENTIALS_FILE,
#     )

#     p, browser, page = launch_browser(HEADERS["User-Agent"])
#     results = []

#     try:
#         for i, art in enumerate(articles, 1):
#             print(f"[{i}/{len(articles)}] {art['url']}")

#             try:
#                 content, total_pages, tags = extract_article_content(
#                     page, art["url"]
#                 )
#             except Exception as e:
#                 content, total_pages, tags = f"ERROR: {e}", 1, ""

#             results.append({
#                 **art,
#                 "tags": tags,
#                 "total_pages": total_pages,
#                 "content": content,
#             })

#             time.sleep(random.uniform(5, 7))

#     finally:
#         browser.close()
#         p.stop()

#     append_rows(
#         worksheet=worksheet,
#         rows=results,
#         header=FIELDNAMES,
#         dedup_key="url",
#     )

#     print(f"✅ Uploaded {len(results)} rows")

if __name__ == "__main__":
    run_daily()
