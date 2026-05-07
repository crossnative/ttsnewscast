from fastapi import HTTPException

from .base import TtsService
from .elevenlabs import ElevenLabsTtsService
from .piper import PiperTtsService


def get_tts_service(provider: str) -> TtsService:
    if provider == "elevenlabs":
        return ElevenLabsTtsService()

    if provider == "piper":
        return PiperTtsService()

    raise HTTPException(status_code=400, detail=f"Unsupported provider '{provider}'")
