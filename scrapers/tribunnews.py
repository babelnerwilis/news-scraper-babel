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
# LOAD ARTICLES FROM SITEMAP (USING PLAYWRIGHT BROWSER)
# ======================================================
def load_articles_from_sitemap(page):
    """
    Load sitemap using Playwright to avoid 403 on GitHub Actions.
    Returns list of article metadata dictionaries.
    """

    print("Loading sitemap via browser...")

    page.goto(SITEMAP_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)

    soup = BeautifulSoup(page.content(), "xml")
    articles = []

    for url in soup.find_all("url"):
        try:
            loc_tag = url.find("loc")
            pub_tag = url.find("news:publication_date")
            title_tag = url.find("news:title")

            if not (loc_tag and pub_tag and title_tag):
                continue

            loc = loc_tag.text.strip()

            pub_date = datetime.fromisoformat(
                pub_tag.text.strip()
            ).astimezone(WIB)

            # Filter by date window
            if not (START_DATE <= pub_date <= END_DATE):
                continue

            title = title_tag.text.strip()

            kw_tag = url.find("news:keywords")
            tags = kw_tag.text.strip() if kw_tag else ""

            source_tag = url.find("news:name")
            source = source_tag.get_text(strip=True) if source_tag else "Tribunnews"

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

    # Oldest → newest (important for historical consistency)
    articles.sort(key=lambda x: x["publication_datetime"])

    print(f"Found {len(articles)} articles in date range")
    return articles


# ======================================================
# EXTRACT ARTICLE CONTENT
# ======================================================
def extract_article_content(page, url):
    """
    Extract article text and total pages from a Tribunnews article.
    Returns: (content_text, total_pages)
    """

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)

        soup = BeautifulSoup(page.content(), "html.parser")

        # --------------------------------------------------
        # Detect pagination (if exists)
        # --------------------------------------------------
        total_pages = 1
        page_info = soup.select_one("span.total-page")
        if page_info:
            m = re.search(r"Halaman\s+\d+/(\d+)", page_info.get_text())
            if m:
                total_pages = int(m.group(1))

        # --------------------------------------------------
        # Preferred extraction (JS embedded content)
        # --------------------------------------------------
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

        # --------------------------------------------------
        # Fallback: normal article HTML
        # --------------------------------------------------
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
        # Polite delay to reduce detection risk
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
