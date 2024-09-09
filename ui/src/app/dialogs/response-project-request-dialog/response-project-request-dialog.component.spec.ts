import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResponseProjectRequestDialogComponent } from './response-project-request-dialog.component';
import {MatLegacyDialogRef} from '@angular/material/legacy-dialog';

describe('ResponseProjectRequestDialogComponent', () => {
  let component: ResponseProjectRequestDialogComponent;
  let fixture: ComponentFixture<ResponseProjectRequestDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ResponseProjectRequestDialogComponent ],
      providers: [
        {provide: MatLegacyDialogRef, useValue: {}}
      ]
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
