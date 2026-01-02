from datetime import datetime, timedelta, timezone

# =========================
# TIMEZONE
# =========================
WIB = timezone(timedelta(hours=7))

# =========================
# SCRAPING WINDOW
# =========================
# Daily run: yesterday → today
TODAY = datetime.now(WIB)
START_DATE = (TODAY - timedelta(days=1)).replace(hour=0, minute=0, second=0)
END_DATE   = TODAY.replace(hour=23, minute=59, second=59)

# =========================
# TRIBUNNEWS
# =========================
TRIBUN_SITEMAP_URL = "https://bangka.tribunnews.com/lokal/sitemap_news.xml"

# =========================
# GOOGLE SHEETS
# =========================
SPREADSHEET_NAME = "Bangka Tribunnews Daily"
WORKSHEET_NAME   = "data"

# =========================
# SCRAPER BEHAVIOR
# =========================
# CRAWL_DELAY = 5
MIN_DELAY = 5
MAX_DELAY = 7
