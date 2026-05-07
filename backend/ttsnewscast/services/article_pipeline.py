from dataclasses import dataclass

from ..schemas import ArticleProperties, ArticleResponse
from .article_extractor import ArticleExtractorService
from .audio_storage import AudioStorageService
from .tts.factory import get_tts_service


@dataclass(slots=True)
class ArticlePipelineService:
    extractor: ArticleExtractorService
    audio_storage: AudioStorageService

    def run(self, url: str, properties: ArticleProperties) -> ArticleResponse:
        article = self.extractor.extract(url)
        tts_service = get_tts_service(properties.provider)
        audio_result = tts_service.synthesize(article.text, properties)

        audio_id = self.audio_storage.save(audio_result.audio_bytes, audio_result.extension)
        return ArticleResponse(
            title=article.title,
            authors=article.authors,
            publish_date=article.publish_date,
            top_image=article.top_image,
            keywords=article.keywords,
            summary=article.summary,
            text=article.text,
            audio_provider=audio_result.provider,
            audio_mime_type=audio_result.mime_type,
            audio_base64=audio_result.audio_base64,
            audio_url=f"/audio/{audio_id}.{audio_result.extension}",
        )
