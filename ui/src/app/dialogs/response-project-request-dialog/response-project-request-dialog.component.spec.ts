import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResponseProjectRequestDialogComponent } from './response-project-request-dialog.component';

describe('ResponseProjectRequestDialogComponent', () => {
  let component: ResponseProjectRequestDialogComponent;
  let fixture: ComponentFixture<ResponseProjectRequestDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ResponseProjectRequestDialogComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ResponseProjectRequestDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
