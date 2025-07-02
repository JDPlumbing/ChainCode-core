import os
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
LINKS_FOLDER = "./ChainCode-local/links/"

def sync_link_file(filepath):
    with open(filepath, "r") as f:
        link_data = json.load(f)

    payload = {
        "from_id": link_data["from_id"],
        "to_id": link_data["to_id"],
        "link_type": link_data.get("link_type", "linked"),
        "note": link_data.get("note", ""),
        "created_at": link_data.get("created_at", datetime.now(timezone.utc).isoformat()),
        "signature": link_data.get("signature", None)
    }

    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/links",
        headers=headers,
        json=payload
    )

    if response.status_code == 201:
        print(f"✅ Synced: {os.path.basename(filepath)}")
    else:
        print(f"❌ Failed to sync {os.path.basename(filepath)}: {response.status_code} {response.text}")


def sync_all_links():
    if not os.path.isdir(LINKS_FOLDER):
        print("No links folder found.")
        return

    files = [f for f in os.listdir(LINKS_FOLDER) if f.endswith(".link.json")]
    if not files:
        print("No link files found.")
        return

    for file in files:
        full_path = os.path.join(LINKS_FOLDER, file)
        sync_link_file(full_path)


if __name__ == '__main__':
    sync_all_links()