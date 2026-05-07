"""Filesystem-backed cache for TTS results.

The cache is keyed by a SHA-256 hash over the input text and the relevant
synthesis parameters (provider, voice, model, output format). For each cache
entry two files live next to each other in :pyattr:`AudioStorageService.base_dir`:

* ``<key>.<ext>`` — the raw audio bytes (re-used as the served audio file)
* ``<key>.json`` — sidecar metadata: provider, mime type, extension, alignment

Currently only the ``elevenlabs`` provider is cached, since Piper runs locally
and incurs no per-call cost.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ..schemas import ArticleProperties, AudioAlignment
from .audio_storage import AudioStorageService
from .tts.base import TtsAudioResult

_CACHED_PROVIDERS: frozenset[str] = frozenset({"elevenlabs"})


@dataclass(slots=True)
class TtsCacheService:
    audio_storage: AudioStorageService

    # ── Public API ────────────────────────────────────────────────────────

    def is_cacheable(self, properties: ArticleProperties) -> bool:
        return properties.provider in _CACHED_PROVIDERS

    def make_key(self, text: str, properties: ArticleProperties) -> str:
        """Return the deterministic cache key for *text* + *properties*.

        The api key is intentionally **not** part of the hash — different users
        synthesising the same text with the same voice should still hit the
        cache.
        """
        h = sha256()
        h.update(properties.provider.encode("utf-8"))
        h.update(b"\0")
        h.update((properties.voice_id or "").encode("utf-8"))
        h.update(b"\0")
        h.update((properties.model_id or "").encode("utf-8"))
        h.update(b"\0")
        h.update((properties.output_format or "").encode("utf-8"))
        h.update(b"\0")
        h.update(text.encode("utf-8"))
        return h.hexdigest()

    def load(self, key: str) -> TtsAudioResult | None:
        """Return a cached :class:`TtsAudioResult` for *key*, or ``None``."""
        meta_path = self._meta_path(key)
        if not meta_path.is_file():
            return None

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

        extension = meta.get("extension")
        if not extension:
            return None

        audio_path = self.audio_storage.get_path(key, extension)
        if not audio_path.is_file():
            return None

        try:
            audio_bytes = audio_path.read_bytes()
        except OSError:
            return None

        alignment_data = meta.get("alignment")
        alignment = AudioAlignment(**alignment_data) if alignment_data else None

        return TtsAudioResult(
            provider=meta.get("provider", ""),
            mime_type=meta.get("mime_type", "application/octet-stream"),
            extension=extension,
            audio_bytes=audio_bytes,
            alignment=alignment,
        )

    def store(self, key: str, result: TtsAudioResult) -> None:
        """Persist *result* under *key*. Audio file uses *key* as its stem."""
        self.audio_storage.save(
            result.audio_bytes,
            result.extension,
            audio_id=key,
        )
        meta = {
            "provider": result.provider,
            "mime_type": result.mime_type,
            "extension": result.extension,
            "alignment": result.alignment.model_dump() if result.alignment else None,
        }
        self._meta_path(key).write_text(
            json.dumps(meta, ensure_ascii=False),
            encoding="utf-8",
        )

    # ── Internals ─────────────────────────────────────────────────────────

    def _meta_path(self, key: str) -> Path:
        return self.audio_storage.base_dir / f"{key}.json"
