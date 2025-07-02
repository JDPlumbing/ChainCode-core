from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from typing import Dict
import json
import uuid
from pathlib import Path
from datetime import datetime
import os
import subprocess
from fastapi import HTTPException

from tools.sync_links import sync_link_file
from chaincode.sync_chaincodes import sync_chaincode_file

from chaincode.generate_chaincode import generate_chaincode, save_chaincode

app = FastAPI()
app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")
from fastapi.responses import RedirectResponse

@app.get("/")
def root():
    return RedirectResponse(url="/ui")


class ChaincodeInput(BaseModel):
    visibility: Optional[str] = "public"
    name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    ssn: Optional[str] = None
    email: Optional[str] = None
    phone_mobile: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None
    employer: Optional[str] = None
    job_title: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    preferred_language: Optional[str] = None
    citizenship: Optional[str] = None 

class ChaincodeForm(BaseModel):
    entity_type: str
    fields: Dict[str, str]
    register: Optional[bool] = False
    download: Optional[bool] = False

@app.post("/generate")
async def generate(data: ChaincodeInput):
    created = []
    for key, value in data.dict().items():
        if key == "visibility" or not value:
            continue
        metadata = {
            "type": key,
            "value": value,
            "visibility": data.visibility
        }
        chaincode = generate_chaincode(seed=value)
        saved = save_chaincode(chaincode, metadata=metadata)
        created.append(saved)
    return JSONResponse(content={"chaincodes": created})

@app.post("/generate_entity")
async def generate_entity(form: ChaincodeForm):
    entity_id = generate_chaincode()
    entity_slug = entity_id[:4] + "-" + entity_id[4:8] + "-" + entity_id[8:12]
    entity_data = {
        "chaincode_id": entity_id,
        "public_slug": entity_slug,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "metadata": {
            "type": form.entity_type,
            "value": "auto",
            "visibility": "public"
        }
    }
    entity_file = f"ChainCode-local/{entity_slug}.json"
    Path("ChainCode-local").mkdir(exist_ok=True)
    with open(entity_file, "w") as f:
        json.dump(entity_data, f, indent=2)

    if form.register:
        sync_chaincode_file(entity_file)

    results = {"entity": entity_data, "fields": [], "links": []}

    for field_type, field_value in form.fields.items():
        if not field_value.strip():
            continue

        field_id = generate_chaincode()
        field_slug = field_id[:4] + "-" + field_id[4:8] + "-" + field_id[8:12]
        metadata = {
            "type": field_type,
            "value": field_value,
            "visibility": "public"
        }
        field_data = save_chaincode(field_id, metadata=metadata)
        results["fields"].append(field_data)

        if form.register:
            sync_chaincode_file(f"ChainCode-local/{field_slug}.json")

        link_obj = {
            "from_id": entity_id,
            "to_id": field_id,
            "link_type": "linked_to",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        link_slug = f"{entity_slug}__linked_to__{field_slug}.link.json"
        link_path = os.path.join("ChainCode-local/links", link_slug)
        Path("ChainCode-local/links").mkdir(parents=True, exist_ok=True)
        with open(link_path, "w") as lf:
            json.dump(link_obj, lf, indent=2)

        if form.register:
            sync_link_file(link_path)

        results["links"].append(link_obj)

    return JSONResponse(content=results)

@app.post("/link")
async def create_link(link: Dict[str, str]):
    try:
        from_id = link["from_id"]
        to_id = link["to_id"]
        link_type = link.get("link_type", "linked_to")
        created_at = link.get("created_at", datetime.utcnow().isoformat() + "Z")

        from_slug = f"{from_id[:4]}-{from_id[4:8]}-{from_id[8:12]}"
        to_slug = f"{to_id[:4]}-{to_id[4:8]}-{to_id[8:12]}"
        link_slug = f"{from_slug}__{link_type}__{to_slug}.link.json"
        link_path = os.path.join("ChainCode-local/links", link_slug)
        Path("ChainCode-local/links").mkdir(parents=True, exist_ok=True)

        link_data = {
            "from_id": from_id,
            "to_id": to_id,
            "link_type": link_type,
            "created_at": created_at,
        }

        with open(link_path, "w") as f:
            json.dump(link_data, f, indent=2)

        return {"status": "ok", "path": link_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync")
async def sync_all_chaincodes():
    try:
        subprocess.run(["python", "main.py", "sync"], check=True)
        return {"status": "chaincodes synced"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync-links")
async def sync_all_links():
    try:
        subprocess.run(["python", "main.py", "sync-links"], check=True)
        return {"status": "links synced"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi.responses import FileResponse

@app.get("/download/{slug}")
async def download_chaincode(slug: str):
    file_path = f"ChainCode-local/{slug}.json"
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(path=file_path, filename=f"{slug}.json", media_type="application/json")

@app.post("/unlink/{filename}")
async def unlink(filename: str):
    try:
        path = os.path.join("ChainCode-local", "links", filename)
        if not os.path.exists(path):
            return JSONResponse(status_code=404, content={"error": "Link file not found"})
        with open(path, "r+") as f:
            data = json.load(f)
            data["revoked"] = True
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
        return {"message": f"{filename} marked as revoked"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
