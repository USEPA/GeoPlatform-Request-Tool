import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfirmApprovalDialogComponent } from './confirm-approval-dialog.component';

describe('ConfirmApprovalDialogComponent', () => {
  let component: ConfirmApprovalDialogComponent;
  let fixture: ComponentFixture<ConfirmApprovalDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ConfirmApprovalDialogComponent ]
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
