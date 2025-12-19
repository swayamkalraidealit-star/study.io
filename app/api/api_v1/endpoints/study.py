from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from app.api import deps
from app.schemas.study import StudyPrompt, StudySessionResponse
from app.schemas.user import UserInDB
from app.services.study_service import study_service
from app.services.polly_service import polly_service
from app.db.mongodb import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
from datetime import datetime
import io

router = APIRouter()

@router.post("/generate", response_model=StudySessionResponse)
async def generate_study_session(
    *,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(deps.get_current_active_user),
    study_in: StudyPrompt
) -> Any:
    # Check user limits
    if current_user.plan == "trial":
        session_count = await db["study_sessions"].count_documents({"user_id": current_user.id})
        
        # Get limit from config
        config = await db["config"].find_one({"_id": "app_config"})
        trial_limit = config.get("trial_limit_sessions", 3) if config else 3
        
        if session_count >= trial_limit:
            raise HTTPException(
                status_code=403,
                detail=f"Trial limit reached ({trial_limit} sessions). Please upgrade to a paid plan."
            )
    
    # Generate content
    content, openai_usage = await study_service.generate_content(
        prompt=study_in.prompt,
        topic=study_in.topic,
        duration_minutes=study_in.duration_minutes
    )
    
    # Synthesize audio
    audio_data, polly_usage = await polly_service.text_to_speech(content)
    
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    session_dict = {
        "_id": session_id,
        "user_id": current_user.id,
        "topic": study_in.topic,
        "content": content,
        "audio_data": audio_data,
        "duration_minutes": study_in.duration_minutes,
        "created_at": now
    }
    
    await db["study_sessions"].insert_one(session_dict)
    
    # Store usage
    usage_dict = {
        "session_id": session_id,
        "user_id": current_user.id,
        "openai_tokens": openai_usage,
        "polly_characters": polly_usage,
        "created_at": now
    }
    await db["usage"].insert_one(usage_dict)
    
    return {
        "id": session_id,
        "topic": study_in.topic,
        "content": content,
        "audio_url": f"/api/v1/study/audio/{session_id}",
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
    
    return StreamingResponse(
        io.BytesIO(session["audio_data"]),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline",
            "Accept-Ranges": "bytes"
        }
    )
