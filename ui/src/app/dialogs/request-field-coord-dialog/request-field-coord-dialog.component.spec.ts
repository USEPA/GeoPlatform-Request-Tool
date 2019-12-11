import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestFieldCoordDialogComponent } from './request-field-coord-dialog.component';

describe('RequestFieldCoordDialogComponent', () => {
  let component: RequestFieldCoordDialogComponent;
  let fixture: ComponentFixture<RequestFieldCoordDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RequestFieldCoordDialogComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestFieldCoordDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
