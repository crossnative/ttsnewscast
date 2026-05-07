import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { ArticleProperties, ExtractResponse, TtsResponse } from '../models/article.model';

@Injectable({
  providedIn: 'root',
})
export class TtsService {
  private readonly http = inject(HttpClient);

  extractText(url: string) {
    return this.http.post<ExtractResponse>('/api/extract-text', { url });
  }

  synthesize(text: string, properties: ArticleProperties) {
    return this.http.post<TtsResponse>('/api/tts', { text, properties });
  }
}
