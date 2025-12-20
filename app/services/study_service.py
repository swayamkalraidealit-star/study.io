from openai import AsyncOpenAI
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

class StudyService:
    def __init__(self):
        api_key = settings.OPENAI_API_KEY
        if api_key and api_key.startswith("ey"):
            logger.error("OPENAI_API_KEY appears to be a JWT token instead of a valid OpenAI API key.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key) if api_key else None

    async def generate_content(
        self, 
        db: AsyncIOMotorDatabase, 
        topic: str, 
        duration_minutes: int, 
        prompt: str,
        exam_mode: bool = False,
        system_prompt_override: str = None
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
        
        if system_prompt_override:
            system_prompt = system_prompt_override
        else:
            system_prompt = (
                "You are an expert academic tutor. Generate accurate, engaging, and pedagogically effective study content based on the user’s topic and requirements."

"Follow these rules:"

"Match the academic level and depth requested"

"Use clear structure (headings, bullet points, steps)"

"Explain concepts logically and succinctly"

"Prioritize conceptual understanding over rote facts"

"Use examples or analogies when they improve clarity"

"Maintain a neutral, supportive, and professional tone"

"When appropriate:"

"Define key terms before using them"

"Break down complex ideas step by step"

"Provide summaries, study tips, or practice questions"

"Avoid unnecessary verbosity. Ensure factual accuracy and educational value at all times."
            )

        # Always append constraints to ensure output fits app requirements
        system_prompt += (
            f"\n\nTOPIC: {topic}\n"
            f"CONTENT TYPE: Study Guide for a {duration_minutes}-minute audio presentation.\n"
            f"STRICT LIMIT: Do not exceed {max_chars} characters.\n"
            "STRUCTURE: Use clear headings, logical flow, and engaging language suitable for listening."
        )

        if exam_mode:
            system_prompt += (
                "\n\nEXAM MODE ENABLED: Focus on high-yield information, concise revision-focused summaries, "
                "bullet points for key facts, and clear definitions."
            )
        
        user_prompt = f"Topic Template Context: {base_prompt}\n\nSpecific Study Requirements/Instructions: {prompt}"
        
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
            logger.info(f"Full OpenAI Response:\n{response.model_dump_json(indent=2)}")
            content = response.choices[0].message.content
            usage = response.usage.total_tokens
            
            logger.info(f"OpenAI Response Content: {content}")
            logger.info(f"OpenAI Response Usage: {usage} tokens")
            
            # Final trim to ensure strict limit
            if len(content) > max_chars:
                content = content[:max_chars].rsplit('.', 1)[0] + '.'
                
            return content, usage
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise e

study_service = StudyService()
