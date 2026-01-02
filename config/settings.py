from datetime import datetime, timezone, timedelta

# =========================
# TIMEZONE
# =========================
WIB = timezone(timedelta(hours=7))

# =========================
# DATE RANGE (yesterday only)
# =========================
YESTERDAY = datetime.now(WIB) - timedelta(days=1)

START_DATE = YESTERDAY.replace(hour=0, minute=0, second=0)
END_DATE   = YESTERDAY.replace(hour=23, minute=59, second=59)

# =========================
# SCRAPER CONFIG
# =========================
SITEMAP_URL = "https://bangka.tribunnews.com/lokal/sitemap_news.xml"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

MIN_DELAY = 5
MAX_DELAY = 7

# =========================
# OUTPUT (local, optional)
# =========================
OUTPUT_DIR = "output"

# =========================
# GOOGLE SHEETS CONFIG
# =========================
SPREADSHEET_ID = "1C7dNMjAaPGCw_OnUqj1mJuA8Sk1MayNb-9TSserpM5U"
# SHEET_NAME = "bangka_tribunnews"
# SHEET_NAME = "github_test"
GOOGLE_CREDENTIALS_FILE = "service_account.json"

# =========================
# CANONICAL COLUMN ORDER
# =========================
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
