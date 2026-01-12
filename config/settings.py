from datetime import datetime, timezone, timedelta
import os

# =========================
# TIMEZONE
# =========================
WIB = timezone(timedelta(hours=7))
NOW_WIB = datetime.now(WIB)

# =========================
# DATE RANGE
# =========================
MAX_PAGES = 99
# START_DATE = datetime(2025, 10, 1, tzinfo=WIB)
# END_DATE   = datetime(2025, 12, 31, 23, 59, 59, tzinfo=WIB)

START_DATE = (NOW_WIB - timedelta(days=3)).replace(
    hour=0, minute=0, second=0, microsecond=0
)
END_DATE = NOW_WIB.replace(
    hour=23, minute=59, second=59, microsecond=0
)


# =========================
# SCRAPER CONFIG
# =========================
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
# TRIBUNNEWS SOURCES
# =========================
# INDEX_BASE_URL = "https://bangka.tribunnews.com/index-news/lokal?page={page}"
TRIBUN_SOURCES = {
    "bangka": {
        "label": "Bangka Tribunnews",
        "base_url": "https://bangka.tribunnews.com/index-news/lokal?page={page}",
        "sheet": "bangka_tribunnews",
    },
    "babel": {
        "label": "Babel Tribunnews",
        "base_url": "https://babel.tribunnews.com/index-news/lokal?page={page}",
        "sheet": "babel_tribunnews",
        # "sheet": "babel_tribunnews_2025_Q4",
    },
    "belitung": {
        "label": "Belitung Tribunnews",
        "base_url": "https://belitung.tribunnews.com/index-news/lokal?page={page}",
        "sheet": "belitung_tribunnews",
        # "sheet": "belitung_tribunnews_2025_Q4",
    }
}

# =========================
# GOOGLE SHEETS CONFIG
# =========================
SPREADSHEET_ID = "1C7dNMjAaPGCw_OnUqj1mJuA8Sk1MayNb-9TSserpM5U"
URL_SHEET_NAME = "tribunnews_urls"

# SHEET_NAME = "bangka_tribunnews"

# Resolve project root (repo root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Credentials path:
# 1) Use env var if set
# 2) Fallback to local service_account.json (ignored by git)
GOOGLE_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    os.path.join(BASE_DIR, "service_account.json")
)

# =========================
# CANONICAL COLUMN ORDER
# =========================
FIELDNAMES = [
    "source",
    "day",
    "publication_datetime",
    "category",
    "title",
    "url",
    "tags",
    "total_pages",
    "content",
]

URL_FIELDNAMES = [
    "source",
    "publication_datetime",
    "category",
    "title",
    "url",
]
