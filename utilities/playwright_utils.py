from playwright.sync_api import sync_playwright

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

def launch_browser(user_agent: str = DEFAULT_USER_AGENT):
    p = sync_playwright().start()

    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ],
    )

    context = browser.new_context(
        user_agent=user_agent,
        viewport={"width": 1366, "height": 768},
        locale="id-ID",
        timezone_id="Asia/Jakarta",
    )

    page = context.new_page()
    return p, browser, page
