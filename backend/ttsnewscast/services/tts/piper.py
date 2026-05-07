import io
import json
import urllib.request
import wave
from pathlib import Path

from fastapi import HTTPException
from piper.voice import PiperVoice

from ...schemas import ArticleProperties
from .base import TtsAudioResult, TtsService

_PIPER_FILES = Path(__file__).parent / "piper_files"
_VOICES_FILE = _PIPER_FILES / "voices.json"
_MODELS_DIR = _PIPER_FILES / "models"


def load_voices() -> dict:
    """Return the voices registry as a dict keyed by voice name."""
    with open(_VOICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_model(voice_name: str) -> Path:
    """
    Return the path to the .onnx model for *voice_name*, downloading it
    (along with its .onnx.json config) if not already present.
    """
    voices = load_voices()
    if voice_name not in voices:
        available = ", ".join(voices.keys())
        raise ValueError(f"Unknown voice '{voice_name}'. Available voices: {available}")

    voice_info = voices[voice_name]
    model_url: str = voice_info["model_url"]
    config_url: str = voice_info["config_url"]

    _MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model_path = _MODELS_DIR / Path(model_url).name
    config_path = _MODELS_DIR / Path(config_url).name

    if not model_path.exists():
        print(f"Downloading model '{voice_name}' from {model_url} ...")
        urllib.request.urlretrieve(model_url, model_path)

    if not config_path.exists():
        print(f"Downloading config for '{voice_name}' from {config_url} ...")
        urllib.request.urlretrieve(config_url, config_path)

    return model_path


class PiperTtsService(TtsService):
    default_voice = "en_US-lessac-high"

    def synthesize(self, text: str, properties: ArticleProperties) -> TtsAudioResult:
        if not text.strip():
            raise HTTPException(status_code=422, detail="Extracted article text is empty")

        voice_name = properties.voice_id or self.default_voice

        try:
            model_path: Path = ensure_model(voice_name)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Failed to load Piper model: {exc}") from exc

        try:
            voice = PiperVoice.load(str(model_path))
            buf = io.BytesIO()
            with wave.open(buf, "wb") as wav_file:
                voice.synthesize_wav(text, wav_file)
            audio_bytes = buf.getvalue()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Piper synthesis failed: {exc}") from exc

        return TtsAudioResult(
            provider="piper",
            mime_type="audio/wav",
            extension="wav",
            audio_bytes=audio_bytes,
        )
