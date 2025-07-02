from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn

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

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
