import hashlib
import time
import uuid
import platform
import os
import json
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from dotenv import load_dotenv

load_dotenv()

ENCRYPTION_KEY = os.getenv("CHAINCODE_ENCRYPTION_KEY")  # Optional fallback
fernet = Fernet(ENCRYPTION_KEY) if ENCRYPTION_KEY else None

def encrypt_value(value):
    if fernet:
        return fernet.encrypt(value.encode()).decode()
    raise ValueError("No symmetric key configured")

def encrypt_value_rsa(value, public_key_path):
    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    encrypted = public_key.encrypt(
        value.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted.hex()

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

def save_chaincode(chaincode_hex, output_dir="./ChainCode-local", metadata=None):
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
    parser.add_argument("--type", dest="type", help="Any label (e.g. 'email', 'license', 'pet')")
    parser.add_argument("--value", dest="value", help="Any value (e.g. 'jd@example.com', 'CFC#1428158')")
    parser.add_argument("--visibility", dest="visibility", choices=["public", "masked", "private"], default="public", help="Visibility level")
    parser.add_argument("--encrypt-to", dest="encrypt_to", help="Path to recipient's public key for RSA encryption")

    args = parser.parse_args()

    metadata = None
    if args.type and args.value:
        visibility = args.visibility or "public"
        if visibility == "private" and args.encrypt_to:
            encrypted = encrypt_value_rsa(args.value, args.encrypt_to)
            metadata = {
                "type": args.type,
                "visibility": visibility,
                "encrypted_value": encrypted,
                "encrypted_for": os.path.basename(args.encrypt_to)
            }
        elif visibility == "private":
            encrypted = encrypt_value(args.value)
            metadata = {
                "type": args.type,
                "visibility": visibility,
                "encrypted_value": encrypted
            }
        else:
            metadata = {
                "type": args.type,
                "value": args.value,
                "visibility": visibility
            }

    chaincode = generate_chaincode()
    saved_data = save_chaincode(chaincode, metadata=metadata)
    print(json.dumps(saved_data, indent=2))
