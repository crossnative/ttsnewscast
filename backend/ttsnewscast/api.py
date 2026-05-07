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

app = FastAPI(title="Article Extractor API")

audio_storage = AudioStorageService()
article_extractor = ArticleExtractorService()
article_pipeline = ArticlePipelineService(
    extractor=article_extractor,
    audio_storage=audio_storage,
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
        tts_service = get_tts_service(req.properties.provider)
        audio_result = tts_service.synthesize(req.text, req.properties)
        audio_id = audio_storage.save(audio_result.audio_bytes, audio_result.extension)
        return TTSResponse(
            audio_provider=audio_result.provider,
            audio_mime_type=audio_result.mime_type,
            audio_base64=audio_result.audio_base64,
            audio_url=f"/audio/{audio_id}.{audio_result.extension}",
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

    return FileResponse(audio_path, media_type="audio/mpeg")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ttsnewscast.api:app", host="0.0.0.0", port=8000)
