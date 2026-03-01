import os
import time
import subprocess
import requests
from playwright.sync_api import sync_playwright

SHEET_URL   = os.environ["SHEET_URL"]
CHAT_WEBHOOK = os.environ["CHAT_WEBHOOK"]
GITHUB_REPO  = os.environ["GITHUB_REPOSITORY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
IMAGE_NAME   = "sheet.png"
IMAGE_URL    = f"https://github.com/{GITHUB_REPO}/blob/main/{IMAGE_NAME}?raw=true"

# --- Take screenshot ---
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1600, "height": 1000})
    page.goto(SHEET_URL)
    time.sleep(8)
    page.screenshot(path=IMAGE_NAME, full_page=True)
    browser.close()

# --- Configure git with auth ---
subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"])
subprocess.run(["git", "config", "--global", "user.name", "github-actions"])
subprocess.run([
    "git", "remote", "set-url", "origin",
    f"https://x-access-token:{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
])

# --- Commit and push ---
subprocess.run(["git", "pull", "--rebase"], check=False)
subprocess.run(["git", "add", "-f", IMAGE_NAME])
result = subprocess.run(["git", "commit", "-m", "Update sheet screenshot"], capture_output=True)
if result.returncode == 0:
    subprocess.run(["git", "push"], check=True)
    print("Screenshot pushed to repo.")
else:
    print("Nothing to commit or commit failed.")

# --- Send Google Chat card ---
payload = {
    "cards": [{
        "sections": [{
            "widgets": [{
                "image": {
                    "imageUrl": IMAGE_URL,
                    "altText": "Google Sheet Snapshot"
                }
            }]
        }]
    }]
}

r = requests.post(CHAT_WEBHOOK, json=payload)
print("Chat response:", r.status_code, r.text)
