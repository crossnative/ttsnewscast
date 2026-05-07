from html import unescape

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from newspaper import Article

app = FastAPI(title="Article Extractor API")


class ArticleRequest(BaseModel):
    url: str


class ArticleResponse(BaseModel):
    title: str
    authors: list[str]
    publish_date: str | None
    top_image: str | None
    keywords: list[str]
    summary: str
    text: str


@app.post("/extract", response_model=ArticleResponse)
def extract_article(req: ArticleRequest):
    try:
        article = Article(req.url)
        article.download()
        article.parse()
        article.nlp()
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    return ArticleResponse(
        title=article.title,
        authors=[unescape(a) for a in article.authors],
        publish_date=str(article.publish_date) if article.publish_date else None,
        top_image=article.top_image,
        keywords=article.keywords,
        summary=article.summary,
        text=article.text,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
