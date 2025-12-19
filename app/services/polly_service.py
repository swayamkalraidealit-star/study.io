import boto3
from app.core.config import settings
import logging
from typing import IO
from contextlib import closing

logger = logging.getLogger(__name__)

class PollyService:
    def __init__(self):
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.client = boto3.client(
                "polly",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        else:
            self.client = None

    async def text_to_speech(self, text: str) -> tuple[bytes, int]:
        if not self.client:
            logger.warning("AWS Polly client not initialized. Returning mock audio data.")
            return b"Mock audio data", len(text)

        try:
            # Polly has a character limit per request
            text_to_synthesize = text[:3000]
            response = self.client.synthesize_speech(
                Text=text_to_synthesize,
                OutputFormat="mp3",
                VoiceId="Joanna",
                Engine="neural"
            )
            
            if "AudioStream" in response:
                with closing(response["AudioStream"]) as stream:
                    return stream.read(), len(text_to_synthesize)
            else:
                raise Exception("Could not synthesize speech")
                
        except Exception as e:
            logger.error(f"Error in Polly synthesis: {e}")
            raise e

polly_service = PollyService()
