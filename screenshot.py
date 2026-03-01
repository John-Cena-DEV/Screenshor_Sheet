import os
import time
import subprocess
import requests
from playwright.sync_api import sync_playwright

SHEET_URL = os.environ["SHEET_URL"]
CHAT_WEBHOOK = os.environ["CHAT_WEBHOOK"]
GITHUB_REPO = os.environ["GITHUB_REPOSITORY"]

IMAGE_NAME = "sheet.png"
IMAGE_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{IMAGE_NAME}"

# 1️⃣ Take screenshot
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1600, "height": 1000})
    page.goto(SHEET_URL)
    time.sleep(6)  # allow Google Sheets to fully render
    page.screenshot(path=IMAGE_NAME, full_page=True)
    browser.close()

# 2️⃣ Commit screenshot to repo
subprocess.run(["git", "config", "--global", "user.email", "bot@github.com"])
subprocess.run(["git", "config", "--global", "user.name", "github-actions"])
subprocess.run(["git", "add", IMAGE_NAME])
subprocess.run(["git", "commit", "-m", "Update sheet screenshot"])
subprocess.run(["git", "push"], check=False)

# 3️⃣ Send Google Chat card with image URL
payload = {
    "cards": [
        {
            "sections": [
                {
                    "widgets": [
                        {
                            "image": {
                                "imageUrl": IMAGE_URL,
                                "altText": "Google Sheet Snapshot"
                            }
                        }
                    ]
                }
            ]
        }
    ]
}

response = requests.post(CHAT_WEBHOOK, json=payload)
print("Chat status:", response.status_code)
print(response.text)
