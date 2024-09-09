import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditAccountPropsDialogComponent } from './edit-account-props-dialog.component';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {MAT_LEGACY_DIALOG_DATA, MatLegacyDialogModule, MatLegacyDialogRef} from '@angular/material/legacy-dialog';

describe('EditAccountPropsDialogComponent', () => {
  let component: EditAccountPropsDialogComponent;
  let fixture: ComponentFixture<EditAccountPropsDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditAccountPropsDialogComponent ],
      imports: [
        HttpClientTestingModule,
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
    fixture = TestBed.createComponent(EditAccountPropsDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
