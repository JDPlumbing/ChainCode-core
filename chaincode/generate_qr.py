import json
import qrcode
from pathlib import Path

def generate_qr_from_chaincode(file_path, output_dir="./ChainCode-local/qrcodes/", format="slug"):
    with open(file_path, "r") as f:
        data = json.load(f)

    if format == "slug":
        content = data.get("public_slug")
    elif format == "id":
        content = data.get("chaincode_id")
    elif format == "url":
        slug = data.get("public_slug")
        content = f"https://trustledger.dev/cc/{slug}"
    else:
        raise ValueError("Invalid format. Use 'slug', 'id', or 'url'.")

    if not content:
        raise ValueError("Missing content to encode")

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filename = Path(file_path).stem + f".{format}.qr.png"
    full_path = Path(output_dir) / filename

    img = qrcode.make(content)
    img.save(full_path)

    return str(full_path)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Path to chaincode .json')
    parser.add_argument('--format', choices=['slug', 'id', 'url'], default='slug')
    args = parser.parse_args()
    print(generate_qr_from_chaincode(args.file, format=args.format))
