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

# --- Take screenshot ---
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1600, "height": 1000})
    page.goto(SHEET_URL)
    time.sleep(8)  # give Sheets time to render
    page.screenshot(path=IMAGE_NAME, full_page=True)
    browser.close()

# --- Configure git ---
subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"])
subprocess.run(["git", "config", "--global", "user.name", "github-actions"])

# --- Commit screenshot (force add) ---
subprocess.run(["git", "add", "-f", IMAGE_NAME])
subprocess.run(["git", "commit", "-m", "Add sheet screenshot"], check=False)
subprocess.run(["git", "push"], check=False)

# --- Send Google Chat card ---
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

r = requests.post(CHAT_WEBHOOK, json=payload)
print("Chat response:", r.status_code, r.text)
