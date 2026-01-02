import re
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from config.settings import (
    SITEMAP_URL,
    START_DATE,
    END_DATE,
    WIB,
    HEADERS,
)

# ======================================================
# LOAD SITEMAP (Browser-based to avoid 403 on GitHub)
# ======================================================
def load_articles_from_sitemap():
    print("Loading sitemap (via browser)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=HEADERS["User-Agent"]
        )
        page = context.new_page()

        page.goto(SITEMAP_URL, wait_until="domcontentloaded", timeout=60000)
        xml_text = page.content()

        browser.close()

    soup = BeautifulSoup(xml_text, "xml")
    articles = []

    for url in soup.find_all("url"):
        try:
            loc = url.find("loc").text.strip()

            pub_date = datetime.fromisoformat(
                url.find("news:publication_date").text.strip()
            ).astimezone(WIB)

            # Date filter (yesterday only / configured range)
            if not (START_DATE <= pub_date <= END_DATE):
                continue

            title = url.find("news:title").text.strip()

            kw_tag = url.find("news:keywords")
            tags = kw_tag.text.strip() if kw_tag else ""

            source_tag = url.find("news:name")
            source = source_tag.get_text(strip=True) if source_tag else ""

            articles.append({
                "day": pub_date.strftime("%d/%m/%Y"),
                "publication_datetime": pub_date.strftime("%d/%m/%Y %H:%M"),
                "source": source,
                "title": title,
                "url": loc,
                "tags": tags,
            })

        except Exception as e:
            print("⚠️ Sitemap parse error:", e)

    # 🔑 IMPORTANT: scrape oldest first
    articles.sort(key=lambda x: x["publication_datetime"])

    print(f"Found {len(articles)} articles")
    return articles


# ======================================================
# ARTICLE CONTENT EXTRACTION
# ======================================================
def extract_article_content(page, url):
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)

    soup = BeautifulSoup(page.content(), "html.parser")

    # ---------- TOTAL PAGES ----------
    total_pages = 1
    page_info = soup.select_one("span.total-page")
    if page_info:
        m = re.search(r"Halaman\s+\d+/(\d+)", page_info.get_text())
        if m:
            total_pages = int(m.group(1))

    # ---------- CONTENT (JS variable – primary) ----------
    for s in soup.find_all("script"):
        if s.string and "keywordBrandSafety" in s.string:
            match = re.search(
                r'keywordBrandSafety\s*=\s*"(.+?)";',
                s.string,
                re.DOTALL
            )
            if match:
                content = (
                    match.group(1)
                    .replace("\\n", "\n")
                    .replace("\\\"", "\"")
                    .strip()
                )
                return content, total_pages

    # ---------- CONTENT (DOM fallback) ----------
    content_div = soup.find("div", class_="side-article txt-article")
    if content_div:
        paragraphs = [
            p.get_text(strip=True)
            for p in content_div.find_all("p")
            if p.get_text(strip=True)
        ]
        if paragraphs:
            return "\n\n".join(paragraphs), total_pages

    return "N/A", total_pages
