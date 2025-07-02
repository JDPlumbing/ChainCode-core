import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
CHAINCODES_FOLDER = "./ChainCode-local/"  # 👈 Add this



def generate_chaincode(gps=(0.0, 0.0), seed=None):
    device_id = platform.node() or uuid.getnode()
    timestamp = str(int(time.time() * 1000))
    lat, lon = gps
    salt = str(lat * 3.14159 + lon * 2.71828)[:16]
    user_entropy = seed or os.urandom(16).hex()
    raw = f"{device_id}|{timestamp}|{salt}|{user_entropy}"
    chaincode_bytes = hashlib.blake2b(raw.encode(), digest_size=32).digest()
    chaincode_hex = chaincode_bytes.hex()
    return chaincode_hex

def slugify_chaincode(chaincode_hex):
    return f"{chaincode_hex[:4]}-{chaincode_hex[4:8]}-{chaincode_hex[8:12]}"

def save_chaincode(chaincode_hex, output_dir="./ChainCode-local"):
    slug = slugify_chaincode(chaincode_hex)
    data = {
        "chaincode_id": chaincode_hex,
        "public_slug": slug,
        "generated_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }
    if metadata:
        data["metadata"] = metadata

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(f"{output_dir}/{slug}.json", "w") as f:
        json.dump(data, f, indent=2)
    return data

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a new chaincode")
    parser.add_argument("--type", dest="type", help="Optional metadata type (e.g. 'email', 'phone')")
    parser.add_argument("--value", dest="value", help="Optional metadata value (e.g. 'jd@example.com')")
    args = parser.parse_args()

    metadata = None
    if args.type and args.value:
        metadata = {"type": args.type, "value": args.value}

    chaincode = generate_chaincode()
    saved_data = save_chaincode(chaincode, metadata=metadata)
    print(json.dumps(saved_data, indent=2))
