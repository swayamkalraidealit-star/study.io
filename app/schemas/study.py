from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StudyPrompt(BaseModel):
    prompt: str
    topic: str
    duration_minutes: int  # 3, 5, or 10
    exam_mode: bool = False
    text_highlighting: bool = False

class StudySessionResponse(BaseModel):
    id: str
    topic: str
    content: str
    audio_url: Optional[str] = None
    listen_count: int = 0
    speech_marks: List[dict] = []
    created_at: datetime

class StudyHistory(BaseModel):
    sessions: List[StudySessionResponse]
