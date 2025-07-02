import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from events.sync_tracker import is_already_synced, mark_synced


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
CHAINCODES_FOLDER = "./ChainCode-local/"

def sync_chaincode_file(filepath):
    filename = os.path.basename(filepath)
    if is_already_synced("chaincodes", filename):
        print(f"🔁 Skipped (already synced): {filename}")
        return

    with open(filepath, "r") as f:
        data = json.load(f)

    payload = {
        "chaincode_id": data["chaincode_id"],
        "public_slug": data["public_slug"],
        "type": data.get("metadata", {}).get("type"),
        "name": None if data.get("metadata", {}).get("visibility") == "private" else data.get("metadata", {}).get("value"),
        "encrypted_value": data.get("metadata", {}).get("encrypted_value"),
        "encrypted_for": data.get("metadata", {}).get("encrypted_for"),
        "visibility": data.get("metadata", {}).get("visibility", "public"),
        "created_at": data.get("generated_at"),
        "metadata": data.get("metadata", {}),
        "trust_score": 0.0,
        "is_public": True
    }

    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/chaincodes",
        headers=headers,
        json=payload
    )

    if response.status_code == 201:
        print(f"✅ Synced: {filename}")
        mark_synced("chaincodes", filename)
    elif response.status_code == 409:
        print(f"⚠️  Already exists in Supabase: {filename}")
        mark_synced("chaincodes", filename)
    else:
        print(f"❌ Failed to sync {filename}: {response.status_code} {response.text}")

def sync_all_chaincodes():
    files = list(Path(CHAINCODES_FOLDER).glob("*.json"))
    if not files:
        print("No chaincode files found.")
        return

    for file in files:
        sync_chaincode_file(file)

if __name__ == '__main__':
    sync_all_chaincodes()
