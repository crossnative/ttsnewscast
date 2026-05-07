"""
Piper TTS synthesis module.

Converts text to a WAV file using a Piper voice model. Voice models are
stored in the models/ directory alongside this package. Available voices
are declared in voices.json.
"""

import json
import urllib.request
import wave
from pathlib import Path

from piper.voice import PiperVoice

# Paths relative to this file
_HERE = Path(__file__).parent
MODELS_DIR = _HERE / "models"
VOICES_FILE = _HERE / "voices.json"


def load_voices() -> dict:
    """Return the voices registry as a dict keyed by voice name."""
    with open(VOICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_model(voice_name: str) -> Path:
    """
    Return the path to the .onnx model for *voice_name*, downloading it
    (along with its .onnx.json config) if not already present.
    """
    voices = load_voices()
    if voice_name not in voices:
        available = ", ".join(voices.keys())
        raise ValueError(
            f"Unknown voice '{voice_name}'. Available voices: {available}"
        )

    voice_info = voices[voice_name]
    model_url: str = voice_info["model_url"]
    config_url: str = voice_info["config_url"]

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model_path = MODELS_DIR / Path(model_url).name
    config_path = MODELS_DIR / Path(config_url).name

    if not model_path.exists():
        print(f"Downloading model '{voice_name}' from {model_url} ...")
        urllib.request.urlretrieve(model_url, model_path)

    if not config_path.exists():
        print(f"Downloading config for '{voice_name}' from {config_url} ...")
        urllib.request.urlretrieve(config_url, config_path)

    return model_path


def synthesize(text: str, voice_name: str, output_path: Path) -> Path:
    """
    Synthesize *text* with *voice_name* and write the result to *output_path*.

    Downloads the voice model automatically if it is not already cached.

    :param text: Text to synthesize.
    :param voice_name: Name of the voice as defined in voices.json.
    :param output_path: Destination .wav file path.
    :return: Resolved path to the written WAV file.
    """
    model_path = ensure_model(voice_name)

    print(f"Loading voice model: {model_path.name}")
    voice = PiperVoice.load(str(model_path))

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Synthesizing {len(text)} characters with voice '{voice_name}' ...")
    with wave.open(str(output_path), "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    return output_path.resolve()
