from abc import ABC, abstractmethod
from base64 import b64encode
from dataclasses import dataclass, field

from ...schemas import ArticleProperties, AudioAlignment


@dataclass(slots=True)
class TtsAudioResult:
    provider: str
    mime_type: str
    extension: str
    audio_bytes: bytes
    alignment: AudioAlignment | None = None

    @property
    def audio_base64(self) -> str:
        return b64encode(self.audio_bytes).decode("ascii")


class TtsService(ABC):
    @abstractmethod
    def synthesize(self, text: str, properties: ArticleProperties) -> TtsAudioResult:
        raise NotImplementedError
