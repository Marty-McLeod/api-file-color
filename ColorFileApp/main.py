from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
import shutil
import uuid
from datetime import datetime
from pathlib import Path
import random, json, os, logging

from validators import DocumentValidator
from models import Options
from file_processing import file_color_processor
from utils.file_functions import load_dict_from_json

"""
CLI curl commands:

curl http://127.0.0.1:8000/api/upload/single -F file=@./test.txt

curl -d @data.json http://127.0.0.1:8000/api/upload/single
   -H "Content-Type: application/json"
   -d '{"productId": 123456, "quantity": 100}' 
   
   
"""
"""
 NOTE: To log HTTP request/response messages, run this in the terminal:
 > uvicorn main:app --reload --log-level debug

"""

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

# Initially load the color names JSON file as a dict:
# Assumes it is loaded in the same directory
try:
    GLOBAL_COLOR_NAME_DICT # type: ignore
except NameError:
    GLOBAL_COLOR_NAME_DICT = load_dict_from_json("color_names.json")
    
    
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
    
# Accepts a request 1) options data JSON as stringified form data, and 2) a file to validate
# & save once OK'd.
@app.post("/upload/single")
async def upload_single_filefile(options: str = Form(...), file: UploadFile = File(...)):
    """
    Uploads color task options (JSON object) and a single file.
    The uploaded file is validated as the correct type and that its content is accessible.
    """

    # As the JSON options data is sent as a string, validate it (parsed) as JSON for the
    # Pydantic model, Options
    try:
        Options.model_validate_json(options)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=jsonable_encoder(e.errors())
        )
        
    options_dict = json.loads(options)
    # logger.info("options_valid:", str(options_dict))
    
    # Validate the file sent via the body of the request
    if file:
        validation = await doc_validator.validate_file(file)

        # # Raise/return HTTP error if an error condition exists for the file. validation()
        # # supplies error messages which are returned to the client/user.
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                        "message": "File validation failed", 
                        "errors": validation["errors"]
                        }
            )

    # # == Validation has passed ==
    # # Create unique temp filename to prevent conflicts
    file_ext = Path(file.filename).suffix # NOTE: Includes '.'!
    file_prefix = file.filename[:-4]
    
    # unique_filename = f"{uuid.uuid4()}{file_ext}"
    temp_filename = f"{file_prefix}{format(random.randrange(9999), "04d")}{file_ext}"
    output_filename = f"{file_prefix}_output{file_ext}"
        
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
    logfile_path = f"{UPLOAD_DIR}/{file_prefix}_logfile.txt"
    
    # logger.info("logfile_path:", logfile_path)
    # logger.info("output_filename:", output_filename)
    # Calls the top color processing function for the following parameters:
    # target filename: the original filename received, file_path: current file (source) file location/name,
    # JSON options object (dictionary), path to create a logfile/name
    
    file_color_processor(output_filename, file_path, options_dict, logfile_path, white_filename="", black_filename="", color_name_dict=GLOBAL_COLOR_NAME_DICT)
    
    # Delete the source file
    try:
        os.remove(file_path)
    except:
        raise FileNotFoundError(f"{file_path} was not found.")
        
        
    
    # return {
    #     "success": True,
    #     "original_filename": file.filename,
    #     "stored_filename": temp_filename,
    #     "content_type": file.content_type,
    #     "size": file.size,
    #     "upload_time": datetime.utcnow().isoformat(),
    #     "location": str(file_path)
    # }
    
    return FileResponse(
        path=output_filename,
        filename=os.path.basename(output_filename),
        media_type="text/plain"
    )
    
    

# ==== PUT endpoints ====

# ==== PATCH endpoints ====

# ==== DELETE endpoints ====