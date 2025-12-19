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

    async def text_to_speech(self, text: str) -> tuple[bytes, list[dict], int]:
        if not self.client:
            logger.warning("AWS Polly client not initialized. Returning mock audio data.")
            return b"Mock audio data", [], len(text)

        try:
            # Polly has a character limit per request
            text_to_synthesize = text[:100]
            
            # 1. Synthesize Audio
            audio_response = self.client.synthesize_speech(
                Text=text_to_synthesize,
                OutputFormat="mp3",
                VoiceId="Joanna",
                Engine="neural"
            )
            
            audio_data = b""
            if "AudioStream" in audio_response:
                with closing(audio_response["AudioStream"]) as stream:
                    audio_data = stream.read()
            else:
                raise Exception("Could not synthesize speech audio")

            # 2. Synthesize Speech Marks (Timestamps)
            marks_response = self.client.synthesize_speech(
                Text=text_to_synthesize,
                OutputFormat="json",
                SpeechMarkTypes=["word"],
                VoiceId="Joanna",
                Engine="neural"
            )

            speech_marks = []
            if "AudioStream" in marks_response:
                with closing(marks_response["AudioStream"]) as stream:
                    marks_text = stream.read().decode("utf-8")
                    # Polly returns multiple JSON objects, one per line
                    for line in marks_text.strip().split("\n"):
                        if line:
                            import json
                            speech_marks.append(json.loads(line))
            else:
                logger.warning("Could not synthesize speech marks")

            return audio_data, speech_marks, len(text_to_synthesize)
                
        except Exception as e:
            logger.error(f"Error in Polly synthesis: {e}")
            raise e

polly_service = PollyService()
