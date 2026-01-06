import requests
import time
import random
import re
from bs4 import BeautifulSoup
from datetime import datetime
from config.settings import (
    INDEX_BASE_URL,
    START_DATE,
    END_DATE,
    WIB,
    HEADERS,
    MIN_DELAY,
    MAX_DELAY,
    MAX_PAGES,
)

MONTHS_ID = {
    "Januari": 1,
    "Februari": 2,
    "Maret": 3,
    "April": 4,
    "Mei": 5,
    "Juni": 6,
    "Juli": 7,
    "Agustus": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Desember": 12,
}

def parse_wib_datetime(text: str) -> datetime:
    parts = text.replace(" WIB", "").split(",")[1].strip()
    d, m_str, y, hm = parts.split()
    hour, minute = hm.split(":")

    return datetime(
        int(y),
        MONTHS_ID[m_str],
        int(d),
        int(hour),
        int(minute),
        tzinfo=WIB
    )

# =========================
# LOAD INDEX
# =========================
def load_articles_from_index():
    print("🕒 START_DATE:", START_DATE.isoformat())
    print("🕒 END_DATE  :", END_DATE.isoformat())

    articles = []
    seen_urls = set()

    for page_num in range(1, MAX_PAGES + 1):
        url = INDEX_BASE_URL.format(page=page_num)
        print(f"Index page {page_num}")

        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            break

        soup = BeautifulSoup(r.text, "lxml")
        items = soup.select("li.ptb15")
        if not items:
            break

        for li in items:
            try:
                time_tag = li.find("time", class_="grey")
                if not time_tag:
                    continue

                pub_date = parse_wib_datetime(time_tag.text.strip())
                if not (START_DATE <= pub_date <= END_DATE):
                    continue

                title_tag = li.select_one("h3 a")
                if not title_tag:
                    continue

                article_url = title_tag["href"]
                if article_url in seen_urls:
                    continue
                seen_urls.add(article_url)

                category_tag = li.select_one("h4 a")
                category = category_tag.text.strip() if category_tag else ""

                articles.append({
                    "day": pub_date.strftime("%A"),
                    "publication_datetime": pub_date.strftime("%d/%m/%Y %H:%M"),
                    "category": category,
                    "title": title_tag.text.strip(),
                    "url": article_url,
                })

            except Exception as e:
                print("⚠️ Index error:", e)

        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    articles.sort(key=lambda x: x["publication_datetime"])
    return articles

# =========================
# ARTICLE CONTENT + TAGS
# =========================
def extract_article_content(page, url):
    """
    Extract article text, total pages, and tags from Tribunnews article.
    Returns (content_text, total_pages, tags)
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
        # Tags extraction (independent of content)
        # ------------------------------------------
        tag_nodes = soup.select("h5.tagcloud3 a")
        tags = ", ".join(
            t.get_text(strip=True)
            for t in tag_nodes
            if t.get_text(strip=True)
        )

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
                    return content, total_pages, tags

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
                return "\n\n".join(paragraphs), total_pages, tags

        return "N/A", total_pages, tags

    finally:
        # Polite delay (anti-detection)
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
