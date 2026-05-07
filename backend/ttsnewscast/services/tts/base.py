from abc import ABC, abstractmethod
from base64 import b64encode
from dataclasses import dataclass

from ...schemas import ArticleProperties


@dataclass(slots=True)
class TtsAudioResult:
    provider: str
    mime_type: str
    extension: str
    audio_bytes: bytes

    @property
    def audio_base64(self) -> str:
        return b64encode(self.audio_bytes).decode("ascii")


class TtsService(ABC):
    @abstractmethod
    def synthesize(self, text: str, properties: ArticleProperties) -> TtsAudioResult:
        raise NotImplementedError
