import httpx
from fastapi import HTTPException

from ...schemas import ArticleProperties
from .base import TtsAudioResult, TtsService


class ElevenLabsTtsService(TtsService):
    base_url = "https://api.elevenlabs.io/v1/text-to-speech"

    def synthesize(self, text: str, properties: ArticleProperties) -> TtsAudioResult:
        if not text.strip():
            raise HTTPException(status_code=422, detail="Extracted article text is empty")

        voice_id = properties.voice_id or "JBFqnCBsd6RMkjVDRZzb"
        payload = {
            "text": text,
            "model_id": properties.model_id or "eleven_multilingual_v2",
        }
        output_format = properties.output_format or "mp3_44100_128"

        try:
            response = httpx.post(
                f"{self.base_url}/{voice_id}",
                params={"output_format": output_format},
                headers={
                    "xi-api-key": properties.api_key or "",
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text or "ElevenLabs request failed"
            raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Unable to reach ElevenLabs") from exc

        return TtsAudioResult(
            provider="elevenlabs",
            mime_type=response.headers.get("content-type", "audio/mpeg"),
            extension="mp3",
            audio_bytes=response.content,
        )
