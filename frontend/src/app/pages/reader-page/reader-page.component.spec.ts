import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReaderPage } from './reader-page.component';

describe('ReaderPage', () => {
  let component: ReaderPage;
  let fixture: ComponentFixture<ReaderPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReaderPage],
    }).compileComponents();

    fixture = TestBed.createComponent(ReaderPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
