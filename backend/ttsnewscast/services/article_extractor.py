from dataclasses import dataclass
from html import unescape

from newspaper import Article


@dataclass(slots=True)
class ExtractedArticle:
    title: str
    authors: list[str]
    publish_date: str | None
    top_image: str | None
    keywords: list[str]
    summary: str
    text: str


class ArticleExtractorService:
    def extract(self, url: str) -> ExtractedArticle:
        article = Article(url)
        article.download()
        article.parse()
        
        return ExtractedArticle(
            title=article.title,
            authors=[unescape(author) for author in article.authors],
            publish_date=str(article.publish_date) if article.publish_date else None,
            top_image=article.top_image,
            keywords=article.keywords,
            summary=article.summary,
            text=article.text,
        )
