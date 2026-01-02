from playwright.sync_api import sync_playwright

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

def get_page():
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)

    context = browser.new_context(
        user_agent=USER_AGENT,
        viewport={"width": 1280, "height": 800}
    )

    # block heavy assets
    context.route(
        "**/*",
        lambda route: route.abort()
        if route.request.resource_type in ["image", "media", "font"]
        else route.continue_()
    )

    page = context.new_page()
    return p, browser, page

