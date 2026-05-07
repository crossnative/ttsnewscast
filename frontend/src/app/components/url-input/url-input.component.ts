import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { TtsService } from '../../services/tts.service';

@Component({
  selector: 'app-url-input',
  imports: [MatFormFieldModule, MatInputModule, FormsModule, MatButtonModule, MatIconModule, MatCardModule],
  templateUrl: './url-input.component.html',
  styleUrl: './url-input.component.scss',
})
export class UrlInput {
  ttsService = inject(TtsService);
  url = signal('https://knightcolumbia.org/content/ai-as-normal-technology');

  onSubmit() {
    this.ttsService.getArticle(this.url()).subscribe(res => {
      console.log(res);
    });
  }
}
