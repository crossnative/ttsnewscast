import { Component } from '@angular/core';
import { UrlInput } from '../../components/url-input/url-input.component';

@Component({
  selector: 'app-start-page',
  imports: [UrlInput],
  templateUrl: './start-page.component.html',
  styleUrl: './start-page.component.scss',
})
export class StartPage {}
