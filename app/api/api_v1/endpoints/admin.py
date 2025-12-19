from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.schemas.admin import AppConfig, ConfigUpdate, TopicPreset
from app.schemas.user import UserResponse
from app.db.mongodb import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.get("/config", response_model=AppConfig)
async def get_app_config(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: Any = Depends(deps.get_current_active_admin),
) -> Any:
    config = await db["config"].find_one({"_id": "app_config"})
    if not config:
        # Return default config if not found
        return AppConfig()
    return config

@router.put("/config", response_model=AppConfig)
async def update_app_config(
    *,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: Any = Depends(deps.get_current_active_admin),
    config_in: ConfigUpdate
) -> Any:
    update_data = config_in.dict(exclude_unset=True)
    await db["config"].update_one(
        {"_id": "app_config"},
        {"$set": update_data},
        upsert=True
    )
    config = await db["config"].find_one({"_id": "app_config"})
    return config

@router.post("/topics", response_model=List[TopicPreset])
async def add_topic_preset(
    *,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: Any = Depends(deps.get_current_active_admin),
    topic: TopicPreset
) -> Any:
    await db["config"].update_one(
        {"_id": "app_config"},
        {"$push": {"topics": topic.dict()}},
        upsert=True
    )
    config = await db["config"].find_one({"_id": "app_config"})
    return config["topics"]

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: Any = Depends(deps.get_current_active_admin),
) -> Any:
    cursor = db["users"].find()
    users = await cursor.to_list(length=100)
    return [{**u, "id": u["_id"]} for u in users]

@router.get("/usage-report")
async def get_usage_report(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: Any = Depends(deps.get_current_active_admin),
) -> Any:
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_openai_tokens": {"$sum": "$openai_tokens"},
                "total_polly_characters": {"$sum": "$polly_characters"},
                "total_sessions": {"$sum": 1}
            }
        }
    ]
    cursor = db["usage"].aggregate(pipeline)
    result = await cursor.to_list(length=1)
    
    if not result:
        return {
            "total_openai_tokens": 0,
            "total_polly_characters": 0,
            "total_sessions": 0
        }
    
    return result[0]
