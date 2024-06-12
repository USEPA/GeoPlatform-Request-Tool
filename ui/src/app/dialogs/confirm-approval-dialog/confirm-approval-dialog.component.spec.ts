import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {ConfirmApprovalDialogComponent} from './confirm-approval-dialog.component';
import {MAT_LEGACY_DIALOG_DATA, MatLegacyDialogModule, MatLegacyDialogRef} from '@angular/material/legacy-dialog';
import {MAT_DIALOG_DATA} from '@angular/material/dialog';

describe('ConfirmApprovalDialogComponent', () => {
  let component: ConfirmApprovalDialogComponent;
  let fixture: ComponentFixture<ConfirmApprovalDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ConfirmApprovalDialogComponent],
      imports: [
        MatLegacyDialogModule,
      ],
      providers: [
        {provide: MatLegacyDialogRef, useValue: {}},
        {provide: MAT_LEGACY_DIALOG_DATA, useValue: {}}
      ]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ConfirmApprovalDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
