import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from config.settings import (
    TRIBUN_SITEMAP_URL,
    START_DATE,
    END_DATE,
    CRAWL_DELAY
)
from utilities.utils import (
    extract_category_from_url,
    format_day,
    format_datetime
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def load_sitemap_articles():
    resp = requests.get(TRIBUN_SITEMAP_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "xml")
    articles = []

    for url in soup.find_all("url"):
        try:
            loc = url.find("loc").text.strip()
            pub_date = datetime.fromisoformat(
                url.find("news:publication_date").text.strip()
            )

            if not (START_DATE <= pub_date <= END_DATE):
                continue

            title = url.find("news:title").text.strip()
            kw = url.find("news:keywords")
            tags = kw.text.strip() if kw else ""

            articles.append({
                "day": format_day(pub_date),
                "publication_datetime": format_datetime(pub_date),
                "category": extract_category_from_url(loc),
                "title": title,
                "url": loc,
                "tags": tags
            })

        except Exception:
            continue

    return articles

def extract_article_content(page, url):
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)

    soup = BeautifulSoup(page.content(), "html.parser")

    # total pages
    total_pages = 1
    info = soup.select_one("span.total-page")
    if info:
        m = re.search(r"Halaman\s+\d+/(\d+)", info.get_text())
        if m:
            total_pages = int(m.group(1))

    # content
    for s in soup.find_all("script"):
        if s.string and "keywordBrandSafety" in s.string:
            m = re.search(
                r'keywordBrandSafety\s*=\s*"(.+?)";',
                s.string,
                re.DOTALL
            )
            if m:
                return (
                    m.group(1)
                    .replace("\\n", "\n")
                    .replace("\\\"", "\"")
                    .strip(),
                    total_pages
                )

    div = soup.find("div", class_="side-article txt-article")
    if div:
        paragraphs = [
            p.get_text(strip=True)
            for p in div.find_all("p")
            if p.get_text(strip=True)
        ]
        return "\n\n".join(paragraphs), total_pages

    return "N/A", total_pages

