from fastapi import (
    FastAPI, File, UploadFile, 
    HTTPException, Request, Form, 
    status, Depends, Path, Query
)

from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from typing import Annotated
import shutil
from dotenv import load_dotenv
import resend
from resend.exceptions import ResendError
import pathlib as plb
import random, json, os, logging

from validators import DocumentValidator
from models import  PayloadWrapperListType, EmailMessage
from file_processing import file_color_processor
from utils.file_functions import load_dict_from_json

import db_models
from db_models import Users, UserRequest
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from auth.api_key import generate_api_key, EMAIL_BODY_HTML

# Create DB using record object models specified
db_models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def validate_api_key(apikey):
    db = SessionLocal()
    
    result = db.query(Users).filter(Users.api_key == apikey.lower()).first()
    db.close()
    
    print(">>Result:", result)
    
    # Returns false on user record not found or is not yet activated
    # Returns true if apikey is found AND active state
    if (result is None) or (result.active == False):
        return False
    elif (result is not None) and (result.active == True):
        return True
    
    
db_dependency = Annotated[Session, Depends(get_db)]
# user_dependency = Annotated[Session, Depends(get_current_user)] # for use with from .auth import get_current_user


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
UPLOAD_DIR = plb.Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initially load the color names JSON file as a dict:
# Assumes it is loaded in the same directory
try:
    COLOR_NAME_DICT # type: ignore
except NameError:
    COLOR_NAME_DICT = load_dict_from_json("color_names.json")
    

# Create validator instance
doc_validator = DocumentValidator(max_size=25 * 1024 * 1024)  # 25MB limit

# Enable the FastAPI logger for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = FastAPI(
    root_path="/api",
    title="FastAPI file upload API",
)
origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurations for using the Resend service to send emails
load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

# example DB query in endpoing
@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Users).all()

# Read a single user record from active Users DB, with explicit HTTP response
# code and only a valid integer
@app.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(db: db_dependency, user_id: int = Path(gt=0)):
    user_model = db.query(Users).filter(Users.id == user_id).first()

    if user_model is not None:
        return user_model
    raise HTTPException(status_code=404, detail="No active User record found.")

# POST (create) a single new User record
@app.post("/user", status_code=status.HTTP_200_OK)
async def create_user(db: db_dependency, user_request: UserRequest):
    user_model = Users(**user_request.model_dump())
    db.add(user_model)
    db.commit()
    
# PATCH (PUT, update) a single User record
@app.put("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(db: db_dependency, 
                      user_request: UserRequest,
                      user_id: int = Path(gt=0)):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found.")
    
    user_model.api_key = user_request.api_key
    user_model.email = user_request.email
    user_model.auth_level = user_request.auth_level
    user_model.active = user_request.active
    
    db.add(user_model)
    db.commit()



# 
@app.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user_id: int = Path(gt=0)):
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found.")
    
    db.query(Users).filter(Users.id == user_id).delete()
    db.commit()
    
    
    
    
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     errors = {}
#     for err in exc.errors():
#         loc = [p for p in err["loc"] if p not in ("body", "query", "path", "header", "cookie")]
#         field = ".".join(str(p) for p in loc) or "__root__"
#         # first error per field wins; keep it simple for the UI
#         errors.setdefault(field, err["msg"])
#     return JSONResponse(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         content={"errors": errors},
#     )


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
@app.get("/message")
def read_test():
    return { "message": "Hello from FastAPI & ColorSwap!" }

@app.get("/email-test")
def send_email():
    resend_status = ""
    
    test_params: resend.Emails.SendParams = {
        "from": "Acme <onboarding@resend.dev>",
        "to": ["delivered@resend.dev"],
        "subject": "Hello world",
        "html": "<strong>it works!</strong>",
    }
    
    try:
        email = resend.Emails.send(test_params)
        print(email)
        resend_status = "Email sent"
    except ResendError as error:
        print(error)
        resend_status = error.message
        
    return(
        {
            "email_status": resend_status
        }
    )
    
    
@app.get("/activate")
async def activate_api_key(db: db_dependency, 
                           apikey: Annotated[str, Query(min_length=8, max_length=8, to_lower=True)]):
    # Check for existing record with the API key record
    user_model = db.query(Users).filter(Users.api_key == apikey)
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found with this API key."
        )
    if user_model.api_key == True:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="API key is already active.")

    user_model.active = True
    db.add(user_model)
    db.commit()
    
    return{
        "message": f"User {user_model.email} API key {apikey} now active for use."
    }


# API key test path: append URL with ?apikey=<key> to verify valid key
# and/or is in DB
@app.get("/api/check_apikey")
async def test_api_key(apikey: Annotated[str, Query(min_length=8, max_length=8, to_lower=True)], 
                       authenticated: Annotated[bool, Depends(validate_api_key)]
                        ):
    if not authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="API key not valid or not found."
                            )
    return{
        "message": "API key validated!",
        "api_key": apikey.lower()
    }
    

# ==== POST endpoints ====

# Generate an API key and send email w/ activation link
@app.post("/get-apikey")
def create_user_and_key(db: db_dependency, email_payload: EmailMessage):
    resend_status = ""
    # payload = email_payload.model_dump()
    
    # Generate a simple API key and verify not alredy in User DB
    # if it exists, generate another key & repeat
    check = True
    while check:
        new_key = generate_api_key(8)
        check = validate_api_key(new_key)
    
    user_model = UserRequest()
    user_model.email = email_payload.to
    user_model.api_key = new_key
    user_model.active = False
    # Save new user record (inactive) to DB
    db.add(user_model)
    db.commit()
    # Send a notification email & link for activation
    email_params: resend.Emails.SendParams = {    
        "from": email_payload.from_field,
        "to": email_payload.to,
        "subject": email_payload.subject,
        "html": EMAIL_BODY_HTML.format(apikey=f"{apikey}", 
                                       activation_url="")
    }

    try:
        smtp_response = resend.Emails.send(email_params)
        resend_status = "Email sent!"
    except ResendError as error:
        resend_status = error.message
        
    return(
        {
            "email_status": resend_status,
        }
    )


@app.post("/send")
def send_email(email_payload: EmailMessage):
    resend_status = ""
    # print(">>> Payload:", email_payload)
    
    email_params: resend.Emails.SendParams = {    
        "from": email_payload.from_field,
        "to": email_payload.to,
        "subject": email_payload.subject,
        "html": email_payload.html
    }

    try:
        smtp_response = resend.Emails.send(email_params)
        resend_status = "Email sent!"
    except ResendError as error:
        resend_status = error.message
        
    return(
        {
            "email_status": resend_status,
        }
    )



# Receives a POST request with color options in body
@app.post("/upload/options")
async def receive_file_options(options_payload: PayloadWrapperListType):

    # Example of accessing a single dict in the validated data ( is in a list):
    # data = options_payload.options[0].hex_rgb
    # print("\noptions_payload:", data)
    
    return {
        "received": {
            "options_payload": options_payload,
        }
        # "hex_rgb": options.hex_rgb,
        # "hex_hsl": options.hex_hsl,
        # "lightdark_hex": options.lightdark_hex,
        # "colorswap_hex": options.colorswap_hex
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
    
# Accepts a request with supplied data in the body:
# 1. Stringified JSON structure 'options' containing user options for color functions
# 2. A file containing text w/ color codes to be affected by the functions
@app.post("/upload/file")
async def upload_single_file(options_payload: str = Form(...), file: UploadFile = File(...)):
    """
    Uploads color task options (JSON object) and a single file.
    The uploaded file is validated as the correct type and that its content is accessible.
    
    NOTE!: JSON cannot be sent alongside a file/files in the body as the FastAPI uses the
    standard HTTP form structure. There are work-arounds, including here where the JSON
    object is stringified (converted to a single string) on the client side, then sent as
    form data to be extracted here. 
    
    The Pydantic model 'Options' is still used to validate data,
    just that it is no longer immediately done.
    """
    
    # As the JSON options data is sent as a string, validate it (parsed) as JSON for the
    # Pydantic model, Options
    try:
        PayloadWrapperListType.model_validate_json(options_payload)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=jsonable_encoder(e.errors())
        )
        
    options_dict = json.loads(options_payload)
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
                        "message": f"File validation failed for '{file.filename}'", 
                        "errors": validation["errors"]
                        }
            )

    # # == Validation has passed ==
    # # Create unique temp filename to prevent conflicts
    file_ext = plb.Path(file.filename).suffix # NOTE: Includes '.'!
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
    
    file_color_processor(output_filename, file_path, options_dict, logfile_path, white_filename="", black_filename="", color_name_dict=COLOR_NAME_DICT)
    
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
    
    
# Accepts a request with supplied data in the body:
# 1. Stringified JSON structure 'options' containing user options for color functions
# 2. 1+ files containing text w/ color codes to be affected by the functions
@app.post("/upload/files")
async def upload_multiple_files(options: str = Form(...), files: list[UploadFile] = File(...)):
    """
    Uploads color task options (JSON object) and multiple files.
    The uploaded files are validated as the correct type and that their content is accessible.
    
    NOTE!: JSON cannot be sent alongside a file/files in the body as the FastAPI uses the
    standard HTTP form structure. There are work-arounds, including here where the JSON
    object is stringified (converted to a single string) on the client side, then sent as
    form data to be extracted here. 
    
    The Pydantic model 'Options' is still used to validate data,
    just that it is no longer immediately done (i.e., as done in the function parameter call).
    """
    MAX_FILES = 5
    
    # Check received file length. If not allowed, return HTTP exception
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File count of {len(files)} exceeds limit of {MAX_FILES}."
        )
        
    # As the JSON options data is sent as a string, validate it (parsed) as JSON for the
    # Pydantic model, Options
    try:
        PayloadWrapperListType.model_validate_json(options)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=jsonable_encoder(e.errors())
        )
        
    options_dict = json.loads(options)
    # logger.info("options_valid:", str(options_dict))
    
    # Validate each file sent via the body of the request
    if files:
        for file in files:
            validation = await doc_validator.validate_file(file)

            # # Raise/return HTTP error if an error condition exists for the file. validation()
            # # supplies error messages which are returned to the client/user.
            if not validation["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                            "message": f"File validation failed for '{file.filename}'", 
                            "errors": validation["errors"]
                            }
                )

    # # == Validation has passed ==
    # # Create unique temp filename to prevent conflicts
    file_exts = []
    file_prefixes = []
    temp_filenames = []
    output_filenames = []
    temp_file_paths = []
    logfile_paths = []
    
    for i, file in enumerate(files):
        file_exts.append(plb.Path(file.filename).suffix) # NOTE: Includes '.'!
        file_prefixes.append(file.filename[:-4])
        
        # unique_filename = f"{uuid.uuid4()}{file_ext}"
        # Create unique temporary filenames for processing work + target output filenames
        temp_filenames.append(f"{file_prefixes[i]}{format(random.randrange(9999), "04d")}{file_exts}")
        output_filenames.append(f"{file_prefixes[i]}_output{file_exts}")
            
        temp_file_paths.append(UPLOAD_DIR / temp_filenames[i])
    
        # Save file to the local path for storage. Return HTTP error if this fails.
        try:
            with open(temp_file_paths[i], "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
        except Exception as e:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"Failed to save file '{files[i].filename}': {str(e)}"
            )
        
        logfile_paths = f"{UPLOAD_DIR}/{file_prefixes[i]}_logfile.txt"
    
    # Consolidate all logfiles into one if > 1 have been processed

        
        
        
    # Calls the top color processing function for the following parameters:
    # target filename: the original filename received, file_path: current file (source) file location/name,
    # JSON options object (dictionary), path to create a logfile/name
    for temp_file in enumerate(temp_file_paths):
        file_color_processor(output_filenames[i], temp_file, options_dict, logfile_paths[i], \
            white_filename="", black_filename="", color_name_dict=COLOR_NAME_DICT)
    
        # Delete the source file
        try:
            os.remove(temp_file_paths[i])
        except:
            raise FileNotFoundError(f"{temp_file_paths[i]} was not found when deleting temp file.")
        
        
    
    # return {
    #     "success": True,
    #     "original_filename": file.filename,
    #     "stored_filename": temp_filename,
    #     "content_type": file.content_type,
    #     "size": file.size,
    #     "upload_time": datetime.utcnow().isoformat(),
    #     "location": str(file_path)
    # }
    
    # return FileResponse(
    #     path=output_filename,
    #     filename=os.path.basename(output_filename),
    #     media_type="text/plain"
    # )


# ==== PUT endpoints ====

# ==== PATCH endpoints ====

# ==== DELETE endpoints ====