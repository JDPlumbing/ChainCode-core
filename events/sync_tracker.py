import os
import json

SYNC_TRACKER_FILE = "./.sync_tracker.json"

def load_synced():
    if os.path.exists(SYNC_TRACKER_FILE):
        with open(SYNC_TRACKER_FILE, "r") as f:
            return json.load(f)
    return {"chaincodes": [], "links": []}

def save_synced(data):
    with open(SYNC_TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def mark_synced(file_type, filename):
    data = load_synced()
    if filename not in data[file_type]:
        data[file_type].append(filename)
    save_synced(data)

def is_already_synced(file_type, filename):
    data = load_synced()
    return filename in data[file_type]