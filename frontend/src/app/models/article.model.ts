export interface ExtractResponse {
    title: string;
    authors: string[];
    publish_date: string | null;
    top_image: string | null;
    keywords: string[];
    summary: string;
    text: string;
}

export interface AudioAlignment {
    characters: string[];
    character_start_times_seconds: number[];
    character_end_times_seconds: number[];
}

export interface TtsResponse {
    audio_provider: string;
    audio_mime_type: string;
    audio_base64: string;
    audio_url: string;
    alignment?: AudioAlignment | null;
}

export interface ArticleProperties {
    provider: string;
    api_key?: string;
    voice_id?: string;
    model_id?: string;
    output_format?: string;
}
