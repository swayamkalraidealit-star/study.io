from openai import AsyncOpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class StudyService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def generate_content(self, prompt: str, topic: str, duration_minutes: int) -> str:
        if not self.client:
            logger.warning("OpenAI client not initialized. Returning mock content.")
            return f"Mock study content for topic: {topic}. Duration: {duration_minutes} minutes. Prompt: {prompt}"

        # Estimate word count based on duration (avg 150 words per minute)
        target_word_count = duration_minutes * 150
        
        system_prompt = (
            "You are a professional study assistant. Generate a comprehensive study guide "
            f"on the topic of '{topic}'. The content should be suitable for an audio "
            f"presentation of approximately {duration_minutes} minutes. "
            f"Target word count: {target_word_count} words. "
            "Structure the content with clear headings and a logical flow."
        )
        
        user_prompt = f"Study Prompt: {prompt}"
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000
            )
            content = response.choices[0].message.content
            usage = response.usage.total_tokens
            return content, usage
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise e

study_service = StudyService()
