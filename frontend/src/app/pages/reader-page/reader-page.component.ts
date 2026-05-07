import {
  Component,
  inject,
  signal,
  computed,
  OnInit,
  ElementRef,
  viewChild,
  effect,
} from '@angular/core';
import { Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import {
  ArticleProperties,
  AudioAlignment,
  ExtractResponse,
  TtsResponse,
} from '../../models/article.model';
import { TtsService } from '../../services/tts.service';

interface TimedToken {
  text: string;
  /** Whitespace following the token (preserved for rendering). */
  trailing: string;
  /** Audio start time in seconds, or null if no alignment is available. */
  start: number | null;
  /** Audio end time in seconds, or null if no alignment is available. */
  end: number | null;
}

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
  currentTokenIndex = signal<number>(-1);

  private readonly audioEl = viewChild<ElementRef<HTMLAudioElement>>('audioEl');

  /** Tokens with attached audio timings (computed once alignment + text are available). */
  readonly tokens = computed<TimedToken[]>(() => {
    const text = this.article()?.text ?? '';
    if (!text) return [];
    const alignment = this.audio()?.alignment ?? null;
    return buildTimedTokens(text, alignment);
  });

  constructor() {
    // Auto-scroll the active word into view when it changes.
    effect(() => {
      const idx = this.currentTokenIndex();
      if (idx < 0) return;
      queueMicrotask(() => {
        const el = document.querySelector<HTMLElement>(
          `[data-token-index="${idx}"]`,
        );
        el?.scrollIntoView({ block: 'center', behavior: 'smooth' });
      });
    });
  }

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

  onTimeUpdate() {
    const el = this.audioEl()?.nativeElement;
    if (!el) return;
    const t = el.currentTime;
    const tokens = this.tokens();
    const idx = findActiveToken(tokens, t);
    if (idx !== this.currentTokenIndex()) {
      this.currentTokenIndex.set(idx);
    }
  }

  onAudioEnded() {
    this.currentTokenIndex.set(-1);
  }

  /** Click a word → seek audio to the word's start time. */
  onTokenClick(idx: number) {
    const token = this.tokens()[idx];
    const el = this.audioEl()?.nativeElement;
    if (!token || token.start == null || !el) return;
    el.currentTime = token.start;
    if (el.paused) {
      el.play().catch(() => {/* ignore autoplay errors */});
    }
  }

  goBack() {
    this.router.navigate(['/']);
  }
}

// ───────────────────────── Helpers ─────────────────────────

/**
 * Tokenise *text* into words + trailing whitespace and, where possible,
 * attach start/end audio timings derived from the ElevenLabs character-level
 * alignment.
 */
export function buildTimedTokens(
  text: string,
  alignment: AudioAlignment | null,
): TimedToken[] {
  const tokens: TimedToken[] = [];
  // Match runs of non-whitespace ("word") followed by trailing whitespace.
  const re = /(\S+)(\s*)/g;
  let match: RegExpExecArray | null;
  while ((match = re.exec(text)) !== null) {
    tokens.push({
      text: match[1],
      trailing: match[2],
      start: null,
      end: null,
    });
  }

  if (!alignment || !alignment.characters?.length) {
    return tokens;
  }

  // Map alignment characters → token boundaries by walking the alignment
  // sequence in lock-step with a flat (whitespace-stripped) view of the tokens.
  // This is robust against the alignment containing extra whitespace chars
  // and small normalisation differences (case, punctuation).
  const starts = alignment.character_start_times_seconds;
  const ends = alignment.character_end_times_seconds;
  const chars = alignment.characters;

  let alignIdx = 0;
  for (const token of tokens) {
    const wordChars = [...token.text];
    let firstStart: number | null = null;
    let lastEnd: number | null = null;

    for (const wc of wordChars) {
      const matched = advanceTo(chars, alignIdx, wc);
      if (matched === -1) {
        // Could not align this character; bail out for this token.
        break;
      }
      alignIdx = matched + 1;
      if (firstStart == null) firstStart = starts[matched] ?? null;
      lastEnd = ends[matched] ?? lastEnd;
    }

    token.start = firstStart;
    token.end = lastEnd;
  }

  return tokens;
}

/**
 * Find the next index `>= from` in *chars* whose lower-cased value matches
 * the lower-cased *target* character. Returns -1 if no match is found.
 */
function advanceTo(chars: string[], from: number, target: string): number {
  const t = target.toLowerCase();
  for (let i = from; i < chars.length; i++) {
    if ((chars[i] ?? '').toLowerCase() === t) return i;
  }
  return -1;
}

/**
 * Binary-search the token whose [start, end] interval contains *time*.
 * Falls back to the last token whose start ≤ time when intervals have gaps.
 */
export function findActiveToken(tokens: TimedToken[], time: number): number {
  if (!tokens.length) return -1;

  let lo = 0;
  let hi = tokens.length - 1;
  let best = -1;

  while (lo <= hi) {
    const mid = (lo + hi) >>> 1;
    const tok = tokens[mid];
    const start = tok.start;
    if (start == null) {
      // Skip untimed tokens by linear fallback.
      lo = mid + 1;
      continue;
    }
    if (start <= time) {
      best = mid;
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }

  if (best === -1) return -1;
  const end = tokens[best].end;
  if (end != null && time > end + 0.25) {
    // Past the end of this word with a small grace period.
    return -1;
  }
  return best;
}
