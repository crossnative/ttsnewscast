import { Component, inject, signal, computed } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router } from '@angular/router';
import { TtsService } from '../../services/tts.service';
import { ArticleProperties } from '../../models/article.model';

@Component({
  selector: 'app-url-input',
  imports: [
    MatFormFieldModule, MatInputModule, FormsModule, MatButtonModule,
    MatButtonToggleModule, MatIconModule, MatCardModule, MatProgressSpinnerModule,
  ],
  templateUrl: './url-input.component.html',
  styleUrl: './url-input.component.scss',
})
export class UrlInput {
  private readonly ttsService = inject(TtsService);
  private readonly router = inject(Router);

  url = signal('https://knightcolumbia.org/content/ai-as-normal-technology');
  provider = signal<'piper' | 'elevenlabs'>('piper');
  apiKey = signal('');
  loading = signal(false);
  error = signal<string | null>(null);

  isElevenLabs = computed(() => this.provider() === 'elevenlabs');

  canSubmit = computed(() => {
    if (!this.url()) return false;
    if (this.isElevenLabs() && !this.apiKey().trim()) return false;
    return true;
  });

  onSubmit() {
    if (!this.canSubmit() || this.loading()) return;

    const properties: ArticleProperties = { provider: this.provider() };
    if (this.isElevenLabs()) {
      properties.api_key = this.apiKey().trim();
    }

    this.loading.set(true);
    this.error.set(null);

    this.ttsService.extractText(this.url()).subscribe({
      next: (article) => {
        this.loading.set(false);
        this.router.navigate(['/read'], { state: { article, properties } });
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set(err?.error?.detail ?? 'Failed to extract article. Please check the URL and try again.');
      },
    });
  }
}
