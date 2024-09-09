import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GenericConfirmDialogComponent } from './generic-confirm-dialog.component';
import {MAT_LEGACY_DIALOG_DATA, MatLegacyDialogModule, MatLegacyDialogRef} from '@angular/material/legacy-dialog';
import {MAT_DIALOG_DATA} from '@angular/material/dialog';

describe('GenericConfirmDialogComponent', () => {
  let component: GenericConfirmDialogComponent;
  let fixture: ComponentFixture<GenericConfirmDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GenericConfirmDialogComponent ],
      imports: [
        MatLegacyDialogModule
      ],
      providers: [
        {provide: MatLegacyDialogRef, useValue: {}},
        {provide: MAT_LEGACY_DIALOG_DATA, useValue: {}}
      ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GenericConfirmDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
