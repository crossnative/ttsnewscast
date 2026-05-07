from pathlib import Path
from uuid import uuid4


class AudioStorageService:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent.parent / "tmp_audio"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, audio_bytes: bytes, extension: str) -> str:
        audio_id = uuid4().hex
        file_path = self.base_dir / f"{audio_id}.{extension}"
        file_path.write_bytes(audio_bytes)
        return audio_id

    def get_path(self, audio_id: str, extension: str) -> Path:
        return self.base_dir / f"{audio_id}.{extension}"
