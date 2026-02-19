import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env", encoding="utf-8-sig")

token = os.environ.get("NOTION_TOKEN", "")
page_id = os.environ.get("NOTION_PAGE_ID", "")

print("Token:", token[:15], "...")
print("Page ID:", page_id)

r = requests.post(
    "https://api.notion.com/v1/databases",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    },
    json={
        "parent": {"type": "page_id", "page_id": page_id},
        "title": [],
        "properties": {"Name": {"title": {}}},
    },
)
print("Status:", r.status_code)
print("Body:", r.text)
