export interface ArticleResponse {
    title: string;
    authors: string[];
    publicationDate: string | null;
    top_image: string | null;
    keywords: string[];
    summary: string;
    text: string;
}

export interface ArticleRequest {
    url: string;
}