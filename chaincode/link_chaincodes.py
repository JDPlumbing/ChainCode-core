import json
import time
from pathlib import Path

def link_chaincodes(
    from_file,
    to_file,
    link_type="associated_with",
    note=None,
    output_dir="./ChainCode-local/links"
):
    # Load both chaincode files
    with open(from_file, "r") as f:
        from_data = json.load(f)
    with open(to_file, "r") as f:
        to_data = json.load(f)

    link = {
        "from_id": from_data["chaincode_id"],
        "to_id": to_data["chaincode_id"],
        "link_type": link_type,
        "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "note": note,
        "signature": None
    }


    # Derive filename from slugs
    from_slug = from_data["public_slug"]
    to_slug = to_data["public_slug"]
    filename = f"{from_slug}__{link_type}__{to_slug}.link.json"

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    link_path = Path(output_dir) / filename

    with open(link_path, "w") as f:
        json.dump(link, f, indent=2)

    print(f"✅ Link saved to: {link_path}")
    return link

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Link two chaincodes together")
    parser.add_argument("--from", dest="from_file", required=True, help="Path to source chaincode JSON")
    parser.add_argument("--to", dest="to_file", required=True, help="Path to target chaincode JSON")
    parser.add_argument("--type", dest="link_type", default="associated_with", help="Type of link")
    parser.add_argument("--note", dest="note", default=None, help="Optional note")

    args = parser.parse_args()
    link_chaincodes(args.from_file, args.to_file, args.link_type, args.note)
