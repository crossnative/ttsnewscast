from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .config import get_available_models
from .schemas import ArticleRequest, ArticleResponse, AvailableModelsResponse, ProviderInfo
from .services.article_extractor import ArticleExtractorService
from .services.article_pipeline import ArticlePipelineService
from .services.audio_storage import AudioStorageService

app = FastAPI(title="Article Extractor API")

audio_storage = AudioStorageService()
article_pipeline = ArticlePipelineService(
    extractor=ArticleExtractorService(),
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


@app.api_route("/audio/{file_name}", methods=["GET", "HEAD"])
def get_audio(file_name: str):
    audio_path = audio_storage.base_dir / file_name
    if not audio_path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(audio_path, media_type="audio/mpeg")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ttsnewscast.api:app", host="0.0.0.0", port=8000)
