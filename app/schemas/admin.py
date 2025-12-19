from pydantic import BaseModel
from typing import List, Optional

class TopicPreset(BaseModel):
    name: str
    description: Optional[str] = None

class AppConfig(BaseModel):
    allowed_durations: List[int] = [3, 5, 10]
    trial_limit_sessions: int = 3
    topics: List[TopicPreset] = []
    features_enabled: dict = {
        "audio_generation": True,
        "history_view": True
    }

class ConfigUpdate(BaseModel):
    allowed_durations: Optional[List[int]] = None
    trial_limit_sessions: Optional[int] = None
    features_enabled: Optional[dict] = None
