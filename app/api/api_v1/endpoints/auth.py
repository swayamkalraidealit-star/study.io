from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from app.core import security
from app.core.config import settings
from app.api import deps
from app.schemas.user import Token, UserCreate, UserResponse, UserInDB
from app.db.mongodb import get_database
from app.services.email import email_service
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
import logging

logger = logging.getLogger(__name__)

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
    elif not user.get("is_email_verified", True):  # Default True for backward compatibility
        raise HTTPException(
            status_code=401, 
            detail="Please verify your email before logging in. Check your inbox for the verification link."
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user["_id"], expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=dict)
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
    
    # Create user with unverified email
    user_dict = user_in.dict()
    password = user_dict.pop("password")
    user_dict["hashed_password"] = security.get_password_hash(password)
    user_dict["_id"] = str(uuid.uuid4())
    user_dict["is_email_verified"] = False
    
    # Generate verification token
    verification_token = security.create_verification_token()
    user_dict["verification_token"] = verification_token
    user_dict["verification_token_expires"] = datetime.utcnow() + timedelta(hours=24)
    
    await db["users"].insert_one(user_dict)
    
    # Send verification email
    email_sent = await email_service.send_verification_email(
        user_in.email, 
        verification_token
    )
    
    if not email_sent:
        logger.warning(f"Failed to send verification email to {user_in.email}")
    
    return {
        "message": "Registration successful! Please check your email to verify your account.",
        "email": user_in.email,
        "email_sent": email_sent
    }

@router.post("/verify-email")
async def verify_email(
    token: str = Query(..., description="Email verification token"),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Any:
    """Verify user email with token"""
    user = await db["users"].find_one({"verification_token": token})
    
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification token"
        )
    
    # Check if token is expired
    if not user.get("verification_token_expires"):
        raise HTTPException(
            status_code=400,
            detail="Invalid verification token"
        )
    
    if not security.verify_token_expiry(user["verification_token_expires"]):
        raise HTTPException(
            status_code=400,
            detail="Verification token has expired. Please request a new verification email."
        )
    
    # Update user as verified
    await db["users"].update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "is_email_verified": True,
                "verification_token": None,
                "verification_token_expires": None
            }
        }
    )
    
    return {
        "message": "Email verified successfully! You can now log in.",
        "email": user["email"]
    }

@router.post("/resend-verification")
async def resend_verification(
    email: EmailStr = Body(..., embed=True),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Any:
    """Resend verification email"""
    user = await db["users"].find_one({"email": email})
    
    if not user:
        # Don't reveal if user exists for security
        return {"message": "If an account exists with this email, a verification email has been sent."}
    
    if user.get("is_email_verified", False):
        raise HTTPException(
            status_code=400,
            detail="Email is already verified"
        )
    
    # Generate new verification token
    verification_token = security.create_verification_token()
    
    await db["users"].update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "verification_token": verification_token,
                "verification_token_expires": datetime.utcnow() + timedelta(hours=24)
            }
        }
    )
    
    # Send verification email
    email_sent = await email_service.send_verification_email(email, verification_token)
    
    if not email_sent:
        logger.warning(f"Failed to resend verification email to {email}")
    
    return {"message": "If an account exists with this email, a verification email has been sent."}

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: UserInDB = Depends(deps.get_current_active_user),
) -> Any:
    return {**current_user.dict(), "id": current_user.id}

# Test endpoint for email configuration
@router.post("/test-email")
async def test_email(
    email: EmailStr = Body(..., embed=True),
    current_user: UserInDB = Depends(deps.get_current_active_user)
) -> Any:
    """Send a test email (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    email_sent = await email_service.send_test_email(email)
    
    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send test email. Check SMTP configuration."
        )
    
    return {"message": f"Test email sent to {email}"}

