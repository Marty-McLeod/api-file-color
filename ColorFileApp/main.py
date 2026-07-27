from fastapi import FastAPI, File, UploadFile, HTTPException, Body, Request
from fastapi.responses import JSONResponse
import logging
from .models import Options

import shutil
import uuid
from datetime import datetime
from pathlib import Path
import random 
from validators import DocumentValidator

"""
CLI curl commands:

curl http://127.0.0.1:8000/api/upload/single -F file=@./test.txt

curl -d @data.json http://127.0.0.1:8000/api/upload/single
   -H "Content-Type: application/json"
   -d '{"productId": 123456, "quantity": 100}' 
   
   
"""
'''
 NOTE: To log HTTP request/response messages, run this in the terminal:
 > uvicorn main:app --reload --log-level debug


'''


# Create our upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create validator instance
doc_validator = DocumentValidator(max_size=25 * 1024 * 1024)  # 25MB limit

# Enable the FastAPI logger for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

app = FastAPI(
    root_path="/api",
    title="FastAPI file upload API",
)


# ==== Middleware for logging or deubgging purposes ====
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    body = await request.body()
    if body:
        logger.info(f"Body: {body.decode()}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

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

# # Accepts a request and body contains a file upload + JSON option parameters
# @app.post("/upload/eval-file")
# async def upload_file_and_options(options: Options, file: UploadFile = File(...)):
#     option_params = options
#     # .... insert code here...
    
#     content = await file.read()
    
#     return {
#         "option_params": {
#                     "hex_rgb": options.hex_rgb,
#                     "hex_hsl": options.hex_hsl,
#                     "lightdark_hex": options.lightdark_hex,
#                     "colorswap_hex": options.colorswap_hex
#         },
#         "file_params": {
#             "name": file.filename,
#             "content": content
#         }
#     }
    
# Accepts a request and uploads a file after validation
@app.post("/upload/single")
async def upload_single_file(options: Options, file: UploadFile = File(...)):
    '''
    Uploads color task options (JSON object) and a single file.
    The uploaded file is validated as the correct type and that its content is accessible.
    '''
    params = options
    
    # Validate the file first. 
    validation = await doc_validator.validate_file(file)
    
    # Raise/return HTTP error if an error condition exists for the file. validation()
    # supplies error messages which are returned to the client/user.
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                    "message": "File validation failed", 
                    "errors": validation["errors"]
                    }
        )
        
    # == Validation has passed ==
    # Create unique temp filename to prevent conflicts
    file_ext = Path(file.filename).suffix
    # unique_filename = f"{uuid.uuid4()}{file_ext}"
    temp_filename = f"{file.filename}{format(random.randrange(999_999), "06d")}{file_ext}"
    
    file_path = UPLOAD_DIR / temp_filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code = 400,
            detail = f"Failed to save file: {str(e)}"
        )
        
    # Call color functions as needed; iterate through options object
    # & determine tasks needed
    
    
    return {
        "success": True,
        "original_filename": file.filename,
        "stored_filename": temp_filename,
        "content_type": file.content_type,
        "size": file.size,
        "upload_time": datetime.utcnow().isoformat(),
        "location": str(file_path)
    }
    
    

# ==== PUT endpoints ====

# ==== PATCH endpoints ====

# ==== DELETE endpoints ====