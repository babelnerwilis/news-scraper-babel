import re
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
from config.settings import (
    SITEMAP_URL,
    START_DATE,
    END_DATE,
    WIB,
    MIN_DELAY,
    MAX_DELAY,
)

# ======================================================
# LOAD ARTICLES FROM SITEMAP (PLAYWRIGHT)
# ======================================================
def load_articles_from_sitemap(page):
    """
    Load Tribunnews sitemap using Playwright
    (403-safe for GitHub Actions).
    """

    print("🚀 Loading sitemap via Playwright browser...")
    print("🕒 START_DATE:", START_DATE.isoformat())
    print("🕒 END_DATE  :", END_DATE.isoformat())

    page.goto(SITEMAP_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)

    soup = BeautifulSoup(page.content(), "xml")
    articles = []

    urls = soup.find_all("url")
    print(f"🔍 Total <url> entries in sitemap: {len(urls)}")

    for url in urls:
        try:
            # ------------------------------------------
            # Namespace-safe XML extraction
            # ------------------------------------------
            loc_tag = url.find("loc")

            pub_tag = url.find(
                lambda t: t.name.endswith("publication_date")
            )
            title_tag = url.find(
                lambda t: t.name.endswith("title")
            )

            if not (loc_tag and pub_tag and title_tag):
                continue

            loc = loc_tag.get_text(strip=True)

            raw_date = pub_tag.get_text(strip=True)

            pub_date = (
                datetime.fromisoformat(raw_date)
                .astimezone(WIB)
            )

            # Debug (safe to keep in CI)
            # print("📰", pub_date.isoformat(), loc)

            # ------------------------------------------
            # DATE FILTER
            # ------------------------------------------
            if pub_date < START_DATE or pub_date > END_DATE:
                continue

            title = title_tag.get_text(strip=True)

            kw_tag = url.find(
                lambda t: t.name.endswith("keywords")
            )
            tags = kw_tag.get_text(strip=True) if kw_tag else ""

            source_tag = url.find(
                lambda t: t.name.endswith("name")
            )
            source = (
                source_tag.get_text(strip=True)
                if source_tag else "Tribunnews"
            )

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

    # Oldest → newest
    articles.sort(key=lambda x: x["publication_datetime"])

    print(f"✅ Found {len(articles)} articles in date window")
    return articles


# ======================================================
# EXTRACT ARTICLE CONTENT
# ======================================================
def extract_article_content(page, url):
    """
    Extract article text from Tribunnews article.
    Returns (content_text, total_pages)
    """

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)

        soup = BeautifulSoup(page.content(), "html.parser")

        # ------------------------------------------
        # Pagination detection
        # ------------------------------------------
        total_pages = 1
        page_info = soup.select_one("span.total-page")
        if page_info:
            m = re.search(r"Halaman\s+\d+/(\d+)", page_info.get_text())
            if m:
                total_pages = int(m.group(1))

        # ------------------------------------------
        # Preferred: embedded JS content
        # ------------------------------------------
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

        # ------------------------------------------
        # Fallback: HTML article body
        # ------------------------------------------
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

    finally:
        # Polite delay (anti-detection)
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
