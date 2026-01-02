import os
from datetime import datetime, timezone, timedelta

# =========================
# TIMEZONE
# =========================
WIB = timezone(timedelta(hours=7))

# =========================
# DATE RANGE (yesterday only)
# =========================
YESTERDAY = datetime.now(WIB) - timedelta(days=1)

START_DATE = YESTERDAY.replace(hour=0, minute=0, second=0, microsecond=0)
END_DATE   = YESTERDAY.replace(hour=23, minute=59, second=59, microsecond=0)

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
# OUTPUT (local only, optional)
# =========================
OUTPUT_DIR = "output"

# =========================
# GOOGLE SHEETS CONFIG
# =========================
# From GitHub Secrets / Environment Variables
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME", "bangka_tribunnews")

# Credentials file:
# - Local: real file
# - GitHub: created dynamically in workflow
GOOGLE_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_CREDENTIALS_FILE",
    "service_account.json"
)
