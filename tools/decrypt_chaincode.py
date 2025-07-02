import json
import argparse
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.fernet import Fernet, InvalidToken
import base64
import os


def decrypt_value_rsa(encrypted_hex, private_key_path):
    encrypted_bytes = bytes.fromhex(encrypted_hex)
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    decrypted = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode()


def decrypt_value_fernet(encrypted_b64, key_path):
    # Try to load key directly or from a .env style file
    key = None
    with open(key_path, "r") as f:
        raw = f.read().strip()
        if raw.startswith("CHAINCODE_ENCRYPTION_KEY="):
            key = raw.split("=", 1)[1].strip()
        else:
            key = raw

    if not key or len(key) != 44:
        raise ValueError("Invalid Fernet key format (must be 32 bytes base64 encoded, 44 chars long)")

    fernet = Fernet(key.encode())
    decrypted = fernet.decrypt(encrypted_b64.encode())
    return decrypted.decode()


def main():
    parser = argparse.ArgumentParser(description="Decrypt an encrypted chaincode value")
    parser.add_argument("--file", required=True, help="Path to the chaincode .json file")
    parser.add_argument("--key", required=True, help="Path to the private RSA or Fernet key or .env file")
    args = parser.parse_args()

    with open(args.file, "r") as f:
        data = json.load(f)

    encrypted = data.get("metadata", {}).get("encrypted_value")
    if not encrypted:
        print("❌ No encrypted value found.")
        return

    try:
        decrypted = decrypt_value_rsa(encrypted, args.key)
        print(f"\n🔓 Decrypted with RSA: {decrypted}\n")
    except (ValueError, Exception):
        try:
            decrypted = decrypt_value_fernet(encrypted, args.key)
            print(f"\n🔓 Decrypted with Fernet: {decrypted}\n")
        except InvalidToken:
            print("❌ Fernet decryption failed: invalid key or data")
        except Exception as e:
            print(f"❌ Failed to decrypt with RSA or Fernet: {e}")


if __name__ == "__main__":
    main()
