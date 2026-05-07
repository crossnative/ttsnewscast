from pydantic import BaseModel, HttpUrl, field_validator, model_validator


# ---------------------------------------------------------------------------
# TTS models endpoint
# ---------------------------------------------------------------------------

class ModelInfo(BaseModel):
    model_id: str
    description: str


class VoiceInfo(BaseModel):
    voice_id: str
    name: str | None = None
    description: str | None = None
    language: str


class ProviderInfo(BaseModel):
    name: str
    requires_api_key: bool
    models: list[ModelInfo] = []
    voices: list[VoiceInfo] = []


AvailableModelsResponse = list[ProviderInfo]


class ArticleProperties(BaseModel):
    provider: str
    api_key: str | None = None
    voice_id: str | None = None
    model_id: str | None = None
    output_format: str | None = None

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("provider is required")
        return normalized

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            raise ValueError("api_key must not be blank")
        return normalized

    @model_validator(mode="after")
    def validate_provider_requirements(self) -> "ArticleProperties":
        if self.provider == "elevenlabs" and not self.api_key:
            raise ValueError("api_key is required for provider 'elevenlabs'")
        if self.provider == "piper" and self.api_key:
            raise ValueError("api_key is not used by provider 'piper'")
        return self


class ArticleRequest(BaseModel):
    url: HttpUrl
    properties: ArticleProperties


class ExtractRequest(BaseModel):
    url: HttpUrl


class ExtractResponse(BaseModel):
    title: str
    authors: list[str]
    publish_date: str | None
    top_image: str | None
    keywords: list[str]
    summary: str
    text: str


class TTSRequest(BaseModel):
    text: str
    properties: ArticleProperties


class TTSResponse(BaseModel):
    audio_provider: str
    audio_mime_type: str
    audio_base64: str
    audio_url: str


class ArticleResponse(ExtractResponse):
    audio_provider: str
    audio_mime_type: str
    audio_base64: str
    audio_url: str
