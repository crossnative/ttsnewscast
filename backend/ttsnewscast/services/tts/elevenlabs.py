from base64 import b64decode

import httpx
from fastapi import HTTPException

from ...schemas import ArticleProperties, AudioAlignment
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
                f"{self.base_url}/{voice_id}/with-timestamps",
                params={"output_format": output_format},
                headers={
                    "xi-api-key": properties.api_key or "",
                    "Accept": "application/json",
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

        try:
            data = response.json()
        except ValueError as exc:
            raise HTTPException(status_code=502, detail="ElevenLabs returned invalid JSON") from exc

        audio_b64 = data.get("audio_base64")
        if not audio_b64:
            raise HTTPException(status_code=502, detail="ElevenLabs response missing audio_base64")

        audio_bytes = b64decode(audio_b64)

        # Prefer normalized_alignment when present (matches the original input text);
        # fall back to alignment (post-normalization characters) otherwise.
        raw_alignment = data.get("normalized_alignment") or data.get("alignment")
        alignment: AudioAlignment | None = None
        if raw_alignment and raw_alignment.get("characters"):
            alignment = AudioAlignment(
                characters=list(raw_alignment.get("characters", [])),
                character_start_times_seconds=list(
                    raw_alignment.get("character_start_times_seconds", [])
                ),
                character_end_times_seconds=list(
                    raw_alignment.get("character_end_times_seconds", [])
                ),
            )

        # output_format mp3_* → audio/mpeg
        mime_type = "audio/mpeg" if output_format.startswith("mp3") else "audio/wav"
        extension = "mp3" if output_format.startswith("mp3") else "wav"

        return TtsAudioResult(
            provider="elevenlabs",
            mime_type=mime_type,
            extension=extension,
            audio_bytes=audio_bytes,
            alignment=alignment,
        )
