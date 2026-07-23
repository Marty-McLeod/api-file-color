from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.responses import JSONResponse
import os
from pydantic import BaseModel, PositiveInt
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from validators import DocumentValidator
import logging

"""
CLI curl commands:

curl http://127.0.0.1:8000/api/upload/single -F file=@./test.txt

curl -d @data.json http://127.0.0.1:8000/api/upload/single
   -H "Content-Type: application/json"
   -d '{"productId": 123456, "quantity": 100}' 
   
   
"""
# Create Pydantic data model for JSON options received in HTTP body
class LightdarkHex(BaseModel):
    active: bool
    mode: str
    percent: PositiveInt


class LightdarkRgb(BaseModel):
    active: bool
    mode: str
    percent: PositiveInt


class ColorswapHex(BaseModel):
    active: bool
    order: str


class ColorswapRgb(BaseModel):
    active: bool
    order: str
    
class Options(BaseModel):
    # hex: bool  # Initial test parameters
    # name: bool
    # rgba: bool
    # color_val: str
    hex_rgb: bool 
    hex_hsl: bool
    
    name_hex: bool
    name_rgb: bool
    
    rgb_hsl: bool
    rgb_hex: bool
    
    hsl_hex: bool
    hsl_rgb: bool
    hsl_hsv: bool
    hsv_hsl: bool
    
    hsv_hex: bool
    hsv_rgb: bool

    lightdark_hex: LightdarkHex
    lightdark_rgb: LightdarkRgb
    colorswap_hex: ColorswapHex
    colorswap_rgb: ColorswapRgb



# Create our upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create validator instance
doc_validator = DocumentValidator(max_size=25 * 1024 * 1024)  # 25MB limit

# Enable the FastAPI logger for debugging
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

app = FastAPI(
    root_path="/api",
    title="FastAPI file upload API",
)

# ==== GET endpoints ====
@app.get("/")
def read_test():
    return { "message": "Working ok" }

# ==== POST endpoints ====

# Receives a POST request with color options in body
@app.post("/upload/options")
async def receive_file_options(options: Options):
        
    return {
        "hex_rgb": options.hex_rgb,
        "hex_hsl": options.hex_hsl,
        "lightdark_hex": options.lightdark_hex,
        "colorswap_hex": options.colorswap_hex
    }


# Accepts a request and uploads a file after validationn
@app.post("/upload/single")
async def upload_single_file(file: UploadFile = File(...)):
    """ Upload a single file with basic validation """
    # Validate the file first
    validation = await doc_validator.validate_file(file)

    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                    "message": "File validation failed", 
                    "errors": validation["errors"]
                    }
        )

    # Create unique filename to prevent conflicts
    file_ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code = 400,
            detail = f"Failed to save file: {str(e)}"
        )
        
    return {
        "success": True,
        "original_filename": file.filename,
        "stored_filename": unique_filename,
        "content_type": file.content_type,
        "size": file.size,
        "upload_time": datetime.utcnow().isoformat(),
        "location": str(file_path)
    }
    
    

# ==== PUT endpoints ====

# ==== PATCH endpoints ====

# ==== DELETE endpoints ====