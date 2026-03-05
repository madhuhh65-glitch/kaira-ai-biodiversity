import os
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status, Depends
from models import UserCreate, UserLogin, Token, UserResponse
from database import get_user_collection
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from datetime import timedelta
from email_validator import validate_email, EmailNotValidError

router = APIRouter()

# Directory for profile images
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/register", response_model=UserResponse)
async def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    profile_image: UploadFile = File(None)
):
    # 1. Validate Input
    try:
        valid = validate_email(email, check_deliverability=False)
        email = valid.email
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    users_collection = get_user_collection()
    existing_user = await users_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Handle Image Upload
    image_path = None
    if profile_image:
        file_extension = profile_image.filename.split(".")[-1]
        filename = f"{email.replace('@', '_')}.{file_extension}"
        file_location = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)
        
        # Save relative path
        image_path = f"/static/images/{filename}"

    # 3. Hash Password & Save User
    hashed_password = get_password_hash(password)
    user_dict = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "profile_image": image_path
    }
    
    new_user = await users_collection.insert_one(user_dict)
    
    return {
        "id": str(new_user.inserted_id),
        "name": name,
        "email": email,
        "profile_image": image_path
    }

@router.post("/login", response_model=Token)
async def login(form_data: UserLogin):
    users_collection = get_user_collection()
    user = await users_collection.find_one({"email": form_data.email})
    
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
