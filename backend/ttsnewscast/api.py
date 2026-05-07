from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .config import get_available_models
from .schemas import (
    ArticleRequest,
    ArticleResponse,
    ExtractRequest,
    ExtractResponse,
    TTSRequest,
    TTSResponse,
    AvailableModelsResponse,
    ProviderInfo
)

from .services.article_extractor import ArticleExtractorService
from .services.article_pipeline import ArticlePipelineService
from .services.audio_storage import AudioStorageService
from .services.tts.factory import get_tts_service
from .services.tts_cache import TtsCacheService

app = FastAPI(title="Article Extractor API")

audio_storage = AudioStorageService()
tts_cache = TtsCacheService(audio_storage=audio_storage)
article_extractor = ArticleExtractorService()
article_pipeline = ArticlePipelineService(
    extractor=article_extractor,
    audio_storage=audio_storage,
    tts_cache=tts_cache,
)


@app.get("/models", response_model=list[ProviderInfo])
def list_models() -> AvailableModelsResponse:
    return get_available_models()


@app.post("/extract", response_model=ArticleResponse)
def extract_article(req: ArticleRequest) -> ArticleResponse:
    try:
        return article_pipeline.run(str(req.url), req.properties)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/extract-text", response_model=ExtractResponse)
def extract_text(req: ExtractRequest) -> ExtractResponse:
    try:
        article = article_extractor.extract(str(req.url))
        return ExtractResponse(
            title=article.title,
            authors=article.authors,
            publish_date=article.publish_date,
            top_image=article.top_image,
            keywords=article.keywords,
            summary=article.summary,
            text=article.text,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/tts", response_model=TTSResponse)
def text_to_speech(req: TTSRequest) -> TTSResponse:
    try:
        cacheable = tts_cache.is_cacheable(req.properties)
        cache_key = tts_cache.make_key(req.text, req.properties) if cacheable else None

        audio_result = tts_cache.load(cache_key) if cache_key else None

        if audio_result is None:
            tts_service = get_tts_service(req.properties.provider)
            audio_result = tts_service.synthesize(req.text, req.properties)
            if cache_key is not None:
                tts_cache.store(cache_key, audio_result)
                audio_id = cache_key
            else:
                audio_id = audio_storage.save(
                    audio_result.audio_bytes, audio_result.extension
                )
        else:
            audio_id = cache_key  # type: ignore[assignment]

        return TTSResponse(
            audio_provider=audio_result.provider,
            audio_mime_type=audio_result.mime_type,
            audio_base64=audio_result.audio_base64,
            audio_url=f"/audio/{audio_id}.{audio_result.extension}",
            alignment=audio_result.alignment,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.api_route("/audio/{file_name}", methods=["GET", "HEAD"])
def get_audio(file_name: str):
    audio_path = audio_storage.base_dir / file_name
    if not audio_path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")

    media_type = "audio/wav" if file_name.lower().endswith(".wav") else "audio/mpeg"
    return FileResponse(audio_path, media_type=media_type)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ttsnewscast.api:app", host="0.0.0.0", port=8000)
