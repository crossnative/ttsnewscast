import { Component, inject, signal, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ArticleProperties, ExtractResponse, TtsResponse } from '../../models/article.model';
import { TtsService } from '../../services/tts.service';

@Component({
  selector: 'app-reader-page',
  imports: [MatButtonModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './reader-page.component.html',
  styleUrl: './reader-page.component.scss',
})
export class ReaderPage implements OnInit {
  private readonly router = inject(Router);
  private readonly ttsService = inject(TtsService);

  article = signal<ExtractResponse | null>(null);
  audio = signal<TtsResponse | null>(null);
  audioLoading = signal(false);
  audioError = signal<string | null>(null);

  ngOnInit() {
    const state = history.state;
    const articleData: ExtractResponse | undefined = state?.article;
    const properties: ArticleProperties | undefined = state?.properties;

    if (!articleData) {
      this.router.navigate(['/']);
      return;
    }

    this.article.set(articleData);

    if (articleData.text && properties) {
      this.generateAudio(articleData.text, properties);
    }
  }

  private generateAudio(text: string, properties: ArticleProperties) {
    this.audioLoading.set(true);
    this.audioError.set(null);

    this.ttsService.synthesize(text, properties).subscribe({
      next: (res) => {
        this.audio.set(res);
        this.audioLoading.set(false);
      },
      error: (err) => {
        this.audioLoading.set(false);
        this.audioError.set(err?.error?.detail ?? 'Failed to generate audio.');
      },
    });
  }

  get audioSrc(): string | null {
    const a = this.audio();
    if (!a) return null;
    if (a.audio_url) return '/api' + a.audio_url;
    if (a.audio_base64 && a.audio_mime_type) {
      return `data:${a.audio_mime_type};base64,${a.audio_base64}`;
    }
    return null;
  }

  goBack() {
    this.router.navigate(['/']);
  }
}
