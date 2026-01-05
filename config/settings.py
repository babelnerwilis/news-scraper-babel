import os
from datetime import datetime, timezone, timedelta

# =========================
# TIMEZONE
# =========================
WIB = timezone(timedelta(hours=7))

NOW_WIB = datetime.now(WIB)

# =========================
# DATE RANGE (ROLLING WINDOW)
# - Prevents missing articles due to:
#   - UTC delay
#   - Sitemap lag
# =========================
START_DATE = (NOW_WIB - timedelta(days=2)).replace(
    hour=0, minute=0, second=0, microsecond=0
)

END_DATE = NOW_WIB.replace(
    hour=23, minute=59, second=59, microsecond=0
)

# =========================
# SCRAPER CONFIG
# =========================
SITEMAP_URL = "https://bangka.tribunnews.com/lokal/sitemap_news.xml"

MIN_DELAY = 5
MAX_DELAY = 7

# =========================
# OUTPUT (optional local)
# =========================
OUTPUT_DIR = "output"

# =========================
# GOOGLE SHEETS CONFIG
# =========================
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME", "automated_bangka_tribunnews")

GOOGLE_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_CREDENTIALS_FILE",
    "service_account.json"
)
