"""
Backend configuration.

Describes the available TTS providers and their voices/models.
Piper voices are loaded dynamically from piper_files/voices.json.
ElevenLabs entries are declared statically (no API call required).
"""

from __future__ import annotations

from ttsnewscast.schemas import AvailableModelsResponse, ModelInfo, ProviderInfo, VoiceInfo
from ttsnewscast.services.tts.piper import load_voices

# ---------------------------------------------------------------------------
# ElevenLabs – static list of supported models and well-known voices
# ---------------------------------------------------------------------------

ELEVENLABS_MODELS: list[ModelInfo] = [
    ModelInfo(model_id="eleven_multilingual_v2", description="Multilingual v2 (recommended)"),
    ModelInfo(model_id="eleven_monolingual_v1",  description="English monolingual v1"),
    ModelInfo(model_id="eleven_turbo_v2",        description="Turbo v2 – low latency"),
    ModelInfo(model_id="eleven_turbo_v2_5",      description="Turbo v2.5 – low latency, multilingual"),
]

ELEVENLABS_VOICES: list[VoiceInfo] = [
    VoiceInfo(voice_id="JBFqnCBsd6RMkjVDRZzb", name="George", language="en"),
    VoiceInfo(voice_id="EXAVITQu4vr4xnSDxMaL", name="Bella",  language="en"),
    VoiceInfo(voice_id="TX3LPaxmHKxFdv7VOQHJ", name="Liam",   language="en"),
    VoiceInfo(voice_id="pFZP5JQG7iQjIQuC4Bku", name="Lily",   language="en"),
    VoiceInfo(voice_id="onwK4e9ZLuTAKqWW03F9", name="Daniel", language="en"),
]

# ---------------------------------------------------------------------------
# Piper – loaded from voices.json at call time
# ---------------------------------------------------------------------------

def _build_piper_voices() -> list[VoiceInfo]:
    return [
        VoiceInfo(voice_id=name, description=info["description"], language=info["language"])
        for name, info in load_voices().items()
    ]


# ---------------------------------------------------------------------------
# Combined registry
# ---------------------------------------------------------------------------

def get_available_models() -> AvailableModelsResponse:
    """Return the full provider → models/voices config."""
    return [
        ProviderInfo(
            name="elevenlabs",
            requires_api_key=True,
            models=ELEVENLABS_MODELS,
            voices=ELEVENLABS_VOICES,
        ),
        ProviderInfo(
            name="piper",
            requires_api_key=False,
            models=[],
            voices=_build_piper_voices(),
        ),
    ]
