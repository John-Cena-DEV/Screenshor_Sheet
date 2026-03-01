import os
import time
import requests
from playwright.sync_api import sync_playwright

SHEET_URL = os.environ["SHEET_URL"]
CHAT_WEBHOOK = os.environ["CHAT_WEBHOOK"]

SCREENSHOT_FILE = "sheet.png"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(
        viewport={"width": 1600, "height": 1000}
    )

    page.goto(SHEET_URL)
    time.sleep(5)  # wait for Google Sheets to render

    page.screenshot(path=SCREENSHOT_FILE, full_page=True)
    browser.close()

with open(SCREENSHOT_FILE, "rb") as f:
    requests.post(CHAT_WEBHOOK, files={"file": f})
