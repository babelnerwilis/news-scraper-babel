import re
from datetime import datetime

def extract_category_from_url(url):
    m = re.search(r"tribunnews\.com/([^/]+)/", url)
    return m.group(1) if m else ""

def format_day(dt):
    return dt.strftime("%d/%m/%Y")

def format_datetime(dt):
    return dt.strftime("%d/%m/%Y %H:%M")

