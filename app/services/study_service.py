from openai import AsyncOpenAI
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

class StudyService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def generate_content(
        self, 
        db: AsyncIOMotorDatabase, 
        topic: str, 
        duration_minutes: int, 
        prompt: str,
        exam_mode: bool = False
    ) -> tuple[str, int]:
        if not self.client:
            logger.warning("OpenAI client not initialized. Returning mock content.")
            return f"Mock study content for topic: {topic}. Duration: {duration_minutes} minutes. Exam Mode: {exam_mode}", 0

        # Fetch dynamic config
        config = await db["config"].find_one({"_id": "app_config"})
        if not config:
            # Fallback to defaults if config not found
            char_limits = {"3": 2500, "5": 4500, "10": 9000}
            topics = []
        else:
            char_limits = config.get("character_limits", {"3": 2500, "5": 4500, "10": 9000})
            topics = config.get("topics", [])

        max_chars = char_limits.get(str(duration_minutes), 2500)
        
        # Find topic template
        topic_template = "Generate a comprehensive study guide about {topic}."
        for t in topics:
            if t["name"].lower() == topic.lower():
                topic_template = t.get("prompt_template", topic_template)
                break
        
        base_prompt = topic_template.format(topic=topic)
        
        system_prompt = (
            "You are a professional study assistant. "
            f"{base_prompt} "
            f"The content MUST be suitable for an audio presentation of approximately {duration_minutes} minutes. "
            f"STRICT LIMIT: Do not exceed {max_chars} characters. "
            "Structure the content with clear headings and a logical flow."
        )

        if exam_mode:
            system_prompt += (
                "\n\nEXAM MODE ENABLED: Focus on concise, revision-focused summaries. "
                "Use bullet points for key facts and provide clear definitions for important terms."
            )
        
        user_prompt = f"Additional Context/Instructions: {prompt}"
        
        # Estimate tokens (roughly 1 token per 4 characters)
        max_tokens = (max_chars // 4) + 500 
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content
            
            # Final trim to ensure strict limit
            if len(content) > max_chars:
                content = content[:max_chars].rsplit('.', 1)[0] + '.'
                
            usage = response.usage.total_tokens
            return content, usage
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise e

study_service = StudyService()
