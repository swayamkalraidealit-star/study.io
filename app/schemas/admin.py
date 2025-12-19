from pydantic import BaseModel
from typing import List, Optional

class TopicPreset(BaseModel):
    name: str
    description: Optional[str] = None
    prompt_template: str

class AppConfig(BaseModel):
    allowed_durations: List[int] = [3, 5, 10]
    character_limits: dict = {
        "3": 100,
        "5": 100,
        "10": 100
    }
    trial_limit_sessions: int = 3
    daily_generation_limit: int = 5
    topics: List[TopicPreset] = [
        TopicPreset(name="Math", prompt_template="Generate a math study guide about {topic}."),
        TopicPreset(name="Physics", prompt_template="Generate a physics study guide about {topic}."),
        TopicPreset(name="Biology", prompt_template="Generate a biology study guide about {topic}."),
        TopicPreset(name="Chemistry", prompt_template="Generate a chemistry study guide about {topic}."),
        TopicPreset(name="History", prompt_template="Generate a history study guide about {topic}.")
    ]
    features_enabled: dict = {
        "audio_generation": True,
        "history_view": True,
        "exam_mode": True,
        "text_highlighting": True
    }
    plan_access: dict = {
        "exam_mode": ["paid"],
        "text_highlighting": ["paid"],
        "durations": {
            "3": ["trial", "paid"],
            "5": ["paid"],
            "10": ["paid"]
        }
    }

class ConfigUpdate(BaseModel):
    allowed_durations: Optional[List[int]] = None
    character_limits: Optional[dict] = None
    trial_limit_sessions: Optional[int] = None
    daily_generation_limit: Optional[int] = None
    features_enabled: Optional[dict] = None
    plan_access: Optional[dict] = None
