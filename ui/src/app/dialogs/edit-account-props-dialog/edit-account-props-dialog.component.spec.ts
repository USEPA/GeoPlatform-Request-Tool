import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditAccountPropsDialogComponent } from './edit-account-props-dialog.component';

describe('EditAccountPropsDialogComponent', () => {
  let component: EditAccountPropsDialogComponent;
  let fixture: ComponentFixture<EditAccountPropsDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditAccountPropsDialogComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditAccountPropsDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
