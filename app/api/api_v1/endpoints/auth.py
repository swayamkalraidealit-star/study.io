from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core import security
from app.core.config import settings
from app.api import deps
from app.schemas.user import Token, UserCreate, UserResponse, UserInDB
from app.db.mongodb import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncIOMotorDatabase = Depends(get_database),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = await db["users"].find_one({"email": form_data.username})
    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user["is_active"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user["_id"], expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserResponse)
async def register_user(
    *,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user_in: UserCreate
) -> Any:
    user = await db["users"].find_one({"email": user_in.email})
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user_dict = user_in.dict()
    password = user_dict.pop("password")
    user_dict["hashed_password"] = security.get_password_hash(password)
    user_dict["_id"] = str(uuid.uuid4())
    
    await db["users"].insert_one(user_dict)
    
    return {**user_dict, "id": user_dict["_id"]}

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: UserInDB = Depends(deps.get_current_active_user),
) -> Any:
    return {**current_user.dict(), "id": current_user.id}
