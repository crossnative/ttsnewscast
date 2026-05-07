from fastapi import HTTPException

from .base import TtsService
from .elevenlabs import ElevenLabsTtsService


def get_tts_service(provider: str) -> TtsService:
    if provider == "elevenlabs":
        return ElevenLabsTtsService()

    raise HTTPException(status_code=400, detail=f"Unsupported provider '{provider}'")
