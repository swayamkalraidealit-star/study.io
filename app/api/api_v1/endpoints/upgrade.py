from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.schemas.user import UserInDB, UserResponse, UserPlan
from app.db.mongodb import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/to-premium", response_model=UserResponse)
async def upgrade_to_premium(
    current_user: UserInDB = Depends(deps.get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Any:
    """
    Upgrade user's plan from trial to premium.
    """
    # Check if user is already on premium plan
    if current_user.plan == UserPlan.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already on the premium plan"
        )
    
    # Update user's plan to premium
    result = await db["users"].update_one(
        {"_id": current_user.id},
        {"$set": {"plan": UserPlan.PAID}}
    )
    
    if result.modified_count == 0:
        logger.error(f"Failed to upgrade user {current_user.id} to premium")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upgrade plan. Please try again."
        )
    
    # Fetch updated user
    updated_user = await db["users"].find_one({"_id": current_user.id})
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"User {current_user.email} upgraded to premium plan")
    
    return {
        "id": updated_user["_id"],
        "email": updated_user["email"],
        "full_name": updated_user.get("full_name"),
        "is_active": updated_user.get("is_active", True),
        "is_email_verified": updated_user.get("is_email_verified", True),
        "role": updated_user.get("role", "user"),
        "plan": updated_user["plan"]
    }
