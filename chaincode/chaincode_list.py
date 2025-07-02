import os
import json
from pathlib import Path
from datetime import datetime

def list_local_chaincodes(directory="./ChainCode-local/"):
    entries = []
    for file in Path(directory).glob("*.json"):
        try:
            with open(file, "r") as f:
                data = json.load(f)
            chaincode_id = data.get("chaincode_id", "")
            slug = data.get("public_slug", "")
            metadata = data.get("metadata", {})
            type_ = metadata.get("type", "")
            value = metadata.get("value", "")
            created_at = data.get("generated_at", "")
            entries.append({
                "file": file.name,
                "slug": slug,
                "type": type_,
                "value": value,
                "created_at": created_at,
                "chaincode_id": chaincode_id
            })
        except Exception as e:
            entries.append({"file": file.name, "error": str(e)})

    return entries

if __name__ == "__main__":
    import pandas as pd
    df = pd.DataFrame(list_local_chaincodes())
    print(df.to_markdown(index=False))
