from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from app.api import deps
from app.schemas.study import StudyPrompt, StudySessionResponse
from app.schemas.user import UserInDB, UserPlan
from app.services.study_service import study_service
from app.services.polly_service import polly_service
from app.schemas.admin import AppConfig
from app.db.mongodb import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
from datetime import datetime
import io

router = APIRouter()

@router.get("/config", response_model=AppConfig)
async def get_public_config(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(deps.get_current_active_user),
) -> Any:
    config = await db["config"].find_one({"_id": "app_config"})
    if not config:
        return AppConfig()
    return config

@router.post("/generate", response_model=StudySessionResponse)
async def generate_study_session(
    *,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(deps.get_current_active_user),
    study_in: StudyPrompt
) -> Any:
    # Fetch dynamic config
    config = await db["config"].find_one({"_id": "app_config"})
    if not config:
        # Fallback to defaults if config not found
        daily_limit = 5
        plan_access = {
            "exam_mode": ["paid"],
            "durations": {"3": ["trial", "paid"], "5": ["paid"], "10": ["paid"]}
        }
    else:
        daily_limit = config.get("daily_generation_limit", 5)
        plan_access = config.get("plan_access", {})

    # Check duration access
    duration_access = plan_access.get("durations", {}).get(str(study_in.duration_minutes), ["paid"])
    if current_user.plan not in duration_access:
        raise HTTPException(
            status_code=403,
            detail=f"Your plan ({current_user.plan}) does not have access to {study_in.duration_minutes}-minute sessions."
        )

    # Check feature access (Exam Mode)
    if study_in.exam_mode:
        exam_mode_access = plan_access.get("exam_mode", ["paid"])
        if current_user.plan not in exam_mode_access:
            raise HTTPException(
                status_code=403,
                detail=f"Exam Mode is not available for your plan ({current_user.plan})."
            )

    # Check daily generation limit
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Reset daily count if it's a new day
    if not current_user.last_generation_date or current_user.last_generation_date < today:
        current_user.daily_generations = 0
    
    if current_user.daily_generations >= daily_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Daily generation limit reached ({daily_limit} sessions). Please try again tomorrow or upgrade."
        )
    
    # 1. Check Cache (Optimization)
    existing_session = await db["study_sessions"].find_one({
        "user_id": current_user.id,
        "topic": study_in.topic,
        "duration_minutes": study_in.duration_minutes,
        "exam_mode": study_in.exam_mode,
        "prompt": study_in.prompt
    })
    
    if existing_session:
        return {
            "id": existing_session["_id"],
            "topic": existing_session["topic"],
            "content": existing_session["content"],
            "audio_url": f"/api/v1/study/audio/{existing_session['_id']}",
            "listen_count": existing_session.get("listen_count", 0),
            "speech_marks": existing_session.get("speech_marks", []),
            "created_at": existing_session["created_at"]
        }

    # 2. Generate content
    content, openai_usage = await study_service.generate_content(
        db=db,
        topic=study_in.topic,
        duration_minutes=study_in.duration_minutes,
        prompt=study_in.prompt,
        exam_mode=study_in.exam_mode
    )
    
    # 3. Synthesize audio and speech marks
    audio_data, speech_marks, polly_usage = await polly_service.text_to_speech(content)
    
    # 4. Calculate Costs (Cost Awareness)
    # GPT-4 rates: $0.03/1k input, $0.06/1k output (approximate average $0.045/1k)
    openai_cost = (openai_usage / 1000) * 0.045
    # Polly Neural: $16.00 per 1M characters
    polly_cost = (polly_usage / 1000000) * 16.00
    total_cost = openai_cost + polly_cost

    session_id = str(uuid.uuid4())
    
    session_dict = {
        "_id": session_id,
        "user_id": current_user.id,
        "topic": study_in.topic,
        "prompt": study_in.prompt,
        "content": content,
        "audio_data": audio_data,
        "speech_marks": speech_marks,
        "duration_minutes": study_in.duration_minutes,
        "exam_mode": study_in.exam_mode,
        "listen_count": 0,
        "created_at": now
    }
    
    await db["study_sessions"].insert_one(session_dict)
    
    # Update user usage
    await db["users"].update_one(
        {"_id": current_user.id},
        {
            "$set": {"last_generation_date": now},
            "$inc": {"daily_generations": 1}
        }
    )
    
    # Store usage and cost
    usage_dict = {
        "session_id": session_id,
        "user_id": current_user.id,
        "openai_tokens": openai_usage,
        "polly_characters": polly_usage,
        "openai_cost": openai_cost,
        "polly_cost": polly_cost,
        "total_cost": total_cost,
        "created_at": now
    }
    await db["usage"].insert_one(usage_dict)
    
    return {
        "id": session_id,
        "topic": study_in.topic,
        "content": content,
        "audio_url": f"/api/v1/study/audio/{session_id}",
        "listen_count": 0,
        "speech_marks": speech_marks,
        "created_at": session_dict["created_at"]
    }

@router.get("/history", response_model=List[StudySessionResponse])
async def get_study_history(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(deps.get_current_active_user),
) -> Any:
    cursor = db["study_sessions"].find({"user_id": current_user.id}).sort("created_at", -1)
    sessions = await cursor.to_list(length=100)
    
    return [
        {
            "id": s["_id"],
            "topic": s["topic"],
            "content": s["content"],
            "audio_url": f"/api/v1/study/audio/{s['_id']}",
            "created_at": s["created_at"]
        }
        for s in sessions
    ]

@router.get("/audio/{session_id}")
async def get_study_audio(
    session_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(deps.get_current_active_user),
) -> Any:
    session = await db["study_sessions"].find_one({"_id": session_id, "user_id": current_user.id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check listen limit for trial users
    if current_user.plan == UserPlan.TRIAL:
        if session.get("listen_count", 0) >= 3:
            raise HTTPException(
                status_code=403,
                detail="Trial users can listen to each session a maximum of 3 times. Please upgrade for unlimited listens."
            )
        
        # Increment listen count
        await db["study_sessions"].update_one(
            {"_id": session_id},
            {"$inc": {"listen_count": 1}}
        )
    
    return StreamingResponse(
        io.BytesIO(session["audio_data"]),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline",
            "Accept-Ranges": "bytes"
        }
    )
