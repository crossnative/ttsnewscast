import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class TtsService {
  public readonly BACKEND_URL = 'http://localhost:8000';

  private readonly http = inject(HttpClient);

  getArticle(url: string) {
    return this.http.post(`/api/extract`, { url });
  }
}
