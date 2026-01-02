from playwright.sync_api import sync_playwright

def launch_browser(user_agent: str):
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent=user_agent)
    page = context.new_page()
    return p, browser, page
