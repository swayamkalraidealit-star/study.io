from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StudyPrompt(BaseModel):
    prompt: str
    topic: str
    duration_minutes: int  # 3, 5, or 10

class StudySessionResponse(BaseModel):
    id: str
    topic: str
    content: str
    audio_url: Optional[str] = None
    created_at: datetime

class StudyHistory(BaseModel):
    sessions: List[StudySessionResponse]
