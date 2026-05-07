from dataclasses import dataclass

from ..schemas import ArticleProperties, ArticleResponse
from .article_extractor import ArticleExtractorService
from .audio_storage import AudioStorageService
from .tts.factory import get_tts_service
from .tts_cache import TtsCacheService


@dataclass(slots=True)
class ArticlePipelineService:
    extractor: ArticleExtractorService
    audio_storage: AudioStorageService
    tts_cache: TtsCacheService

    def run(self, url: str, properties: ArticleProperties) -> ArticleResponse:
        article = self.extractor.extract(url)

        cacheable = self.tts_cache.is_cacheable(properties)
        cache_key = (
            self.tts_cache.make_key(article.text, properties) if cacheable else None
        )

        audio_result = None
        if cache_key is not None:
            audio_result = self.tts_cache.load(cache_key)

        if audio_result is None:
            tts_service = get_tts_service(properties.provider)
            audio_result = tts_service.synthesize(article.text, properties)
            if cache_key is not None:
                self.tts_cache.store(cache_key, audio_result)
                audio_id = cache_key
            else:
                audio_id = self.audio_storage.save(
                    audio_result.audio_bytes, audio_result.extension
                )
        else:
            audio_id = cache_key  # type: ignore[assignment]

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
            alignment=audio_result.alignment,
        )
