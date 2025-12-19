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

@router.get("/sessions")
async def get_all_sessions(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: Any = Depends(deps.get_current_active_admin),
) -> Any:
    cursor = db["study_sessions"].find().sort("created_at", -1)
    sessions = await cursor.to_list(length=100)
    return [{**s, "id": s["_id"]} for s in sessions]

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
                "total_openai_cost": {"$sum": "$openai_cost"},
                "total_polly_cost": {"$sum": "$polly_cost"},
                "total_cost": {"$sum": "$total_cost"},
                "total_sessions": {"$sum": 1}
            }
        }
    ]
    cursor = db["usage"].aggregate(pipeline)
    result = await cursor.to_list(length=1)
    
    if not result:
        summary = {
            "total_openai_tokens": 0,
            "total_polly_characters": 0,
            "total_openai_cost": 0,
            "total_polly_cost": 0,
            "total_cost": 0,
            "total_sessions": 0
        }
    else:
        summary = result[0]

    # Get detailed usage per user
    user_pipeline = [
        {
            "$group": {
                "_id": "$user_id",
                "openai_tokens": {"$sum": "$openai_tokens"},
                "polly_characters": {"$sum": "$polly_characters"},
                "total_cost": {"$sum": "$total_cost"},
                "sessions": {"$sum": 1}
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "_id",
                "as": "user_info"
            }
        },
        {"$unwind": "$user_info"},
        {
            "$project": {
                "email": "$user_info.email",
                "openai_tokens": 1,
                "polly_characters": 1,
                "total_cost": 1,
                "sessions": 1
            }
        }
    ]
    user_cursor = db["usage"].aggregate(user_pipeline)
    user_usage = await user_cursor.to_list(length=100)

    return {
        "summary": summary,
        "user_usage": user_usage
    }
