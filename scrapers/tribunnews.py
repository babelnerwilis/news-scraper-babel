import requests
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
    HEADERS,
    MIN_DELAY,
    MAX_DELAY,
)

# =========================
# LOAD SITEMAP
# =========================
def load_articles_from_sitemap():
    print("Loading sitemap...")
    resp = requests.get(SITEMAP_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "xml")
    articles = []

    for url in soup.find_all("url"):
        try:
            loc = url.find("loc").text.strip()

            pub_date = datetime.fromisoformat(
                url.find("news:publication_date").text.strip()
            ).astimezone(WIB)

            if not (START_DATE <= pub_date <= END_DATE):
                continue

            title = url.find("news:title").text.strip()
            kw_tag = url.find("news:keywords")
            tags = kw_tag.text.strip() if kw_tag else ""

            day = pub_date.strftime("%d/%m/%Y")
            publication_datetime = pub_date.strftime("%d/%m/%Y %H:%M")

            m = re.search(r"tribunnews\.com/([^/]+)/", loc)
            # category = m.group(1) if m else ""
            news_source_tag = url.find("news:name")
            news_source = news_source_tag.get_text(strip=True) if news_source_tag else ""


            articles.append({
                "day": day,
                "publication_datetime": publication_datetime,
                "source": news_source,
                "title": title,
                "url": loc,
                "tags": tags,
            })

        except Exception as e:
            print("⚠️ Sitemap error:", e)
            
    # SORT: oldest → newest
    articles.sort(key=lambda x: x["publication_datetime"])

    print(f"Found {len(articles)} articles")
    return articles


# =========================
# ARTICLE CONTENT
# =========================
def extract_article_content(page, url):
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)

    soup = BeautifulSoup(page.content(), "html.parser")

    total_pages = 1
    page_info = soup.select_one("span.total-page")
    if page_info:
        m = re.search(r"Halaman\s+\d+/(\d+)", page_info.get_text())
        if m:
            total_pages = int(m.group(1))

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

    content_div = soup.find("div", class_="side-article txt-article")
    if content_div:
        paragraphs = [
            p.get_text(strip=True)
            for p in content_div.find_all("p")
            if p.get_text(strip=True)
        ]
        return "\n\n".join(paragraphs), total_pages

    return "N/A", total_pages
